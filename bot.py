import telebot
from telebot import types
import yt_dlp
import os
import glob
from shazamio import Shazam
import asyncio

# Sizning bot tokeningiz
TOKEN = "8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8"
bot = telebot.TeleBot(TOKEN)
shazam = Shazam()

user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Menga YouTube yoki Instagram linkini yuboring. Men videoni yuklab beraman yoki undagi musiqani topib, to'liq variantini yuboraman! 📥")

@bot.message_handler(func=lambda message: any(x in message.text for x in ["youtube.com", "youtu.be", "instagram.com"]))
def handle_link(message):
    url = message.text
    user_links[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video")
    btn_audio = types.InlineKeyboardButton("🎵 To'liq musiqasini topish", callback_data="audio")
    markup.add(btn_video, btn_audio)
    
    bot.send_message(message.chat.id, "Tanlang:", reply_markup=markup)

async def recognize_and_download(url, chat_id, status_id):
    temp_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_shazam.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '128'}],
        'quiet': True,
        'no_warnings': True
    }
    
    try:
        with yt_dlp.YoutubeDL(temp_opts) as ydl:
            ydl.download([url])
        
        out = await shazam.recognize_song('temp_shazam.mp3')
        
        if out['matches']:
            track_title = out['track']['title']
            track_artist = out['track']['subtitle']
            search_query = f"{track_artist} {track_title}"
            bot.edit_message_text(f"🔍 Musiqa topildi: {search_query}. Yuklanmoqda...", chat_id, status_id)
            
            final_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'final_music.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(final_opts) as ydl:
                ydl.download([f"ytsearch1:{search_query}"])
            
            with open('final_music.mp3', 'rb') as f:
                bot.send_audio(chat_id, f, caption=f"✅ {search_query}")
        else:
            bot.send_message(chat_id, "❌ Shazam bu musiqani topa olmadi.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Xato: {e}")

    for f in glob.glob("temp_shazam*") + glob.glob("final_music*"):
        if os.path.exists(f): os.remove(f)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_links.get(call.message.chat.id)
    if not url: return

    try:
        if call.data == "video":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            status = bot.send_message(call.message.chat.id, "⏳ Video yuklanmoqda...")
            ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open('video.mp4', 'rb') as f:
                bot.send_video(call.message.chat.id, f, caption="✅ Tayyor!")
            os.remove('video.mp4')
            bot.delete_message(call.message.chat.id, status.message_id)
            
        elif call.data == "audio":
            bot.delete_message(call.message.chat.id, call.message.message_id)
            status = bot.send_message(call.message.chat.id, "⏳ Musiqa qidirilmoqda...")
            asyncio.run(recognize_and_download(url, call.message.chat.id, status.message_id))
            bot.delete_message(call.message.chat.id, status.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    bot.infinity_polling()
