import telebot
from telebot import types
import yt_dlp
import instaloader
import os
import glob

# Bot tokeningiz
TOKEN = "8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8"
bot = telebot.TeleBot(TOKEN)

# Vaqtincha linklarni saqlash uchun lug'at
user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Menga YouTube yoki Instagram linkini yuboring. Men uni video yoki MP3 ko'rinishida yuklab beraman! 📥")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text or "instagram.com" in message.text)
def handle_link(message):
    url = message.text
    user_links[message.chat.id] = url
    
    # Tugmalar yaratish
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video")
    btn_audio = types.InlineKeyboardButton("🎵 Musiqasini (MP3) yuklash", callback_data="audio")
    markup.add(btn_video, btn_audio)
    
    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        bot.answer_callback_query(call.id, "Xatolik: Link topilmadi.")
        return

    bot.delete_message(call.message.chat.id, call.message.message_id)
    status = bot.send_message(call.message.chat.id, "⏳ Jarayon boshlandi...")

    try:
        if call.data == "video":
            # Video yuklash (YouTube & Instagram uchun)
            ydl_opts = {'format': 'best', 'outtmpl': 'downloaded_video.mp4', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open('downloaded_video.mp4', 'rb') as f:
                bot.send_video(call.message.chat.id, f, caption="✅ Video tayyor!")
            os.remove('downloaded_video.mp4')
            
        elif call.data == "audio":
            # MP3 ajratib olish
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'music.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            audio_file = glob.glob("music.mp3")[0]
            with open(audio_file, 'rb') as f:
                bot.send_audio(call.message.chat.id, f, caption="✅ Musiqa tayyor!")
            os.remove(audio_file)

        bot.delete_message(call.message.chat.id, status.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xatolik yuz berdi: {e}")

bot.polling(none_stop=True)
