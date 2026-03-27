import telebot
import yt_dlp
import os
from shazamio import Shazam
import asyncio
from telebot import types

# --- SOZLAMALAR ---
# O'zingizning tokeningizni shu yerga yozing
TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'
bot = telebot.TeleBot(TOKEN)
shazam = Shazam()

# Foydalanuvchi linklarini vaqtincha saqlash uchun
user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Menga YouTube yoki Instagram linkini yuboring. Men videoni yuklab beraman yoki undagi musiqani topib beraman! 🎬")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url or "instagram.com" in url:
        user_links[message.chat.id] = url
        
        markup = types.InlineKeyboardMarkup()
        btn_video = types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video")
        btn_audio = types.InlineKeyboardButton("🎵 Musiqa (SoundCloud orqali)", callback_data="audio")
        markup.add(btn_video, btn_audio)
        
        bot.send_message(message.chat.id, "Nima yuklamoqchisiz?", reply_markup=markup)
    else:
        bot.reply_to(message, "Iltimos, faqat YouTube yoki Instagram linkini yuboring.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        return

    bot.delete_message(call.message.chat.id, call.message.message_id)
    status = bot.send_message(call.message.chat.id, "⏳ Jarayon boshlandi...")

    try:
        if call.data == "video":
            bot.edit_message_text("⏳ Video yuklanmoqda...", call.message.chat.id, status.message_id)
            ydl_opts = {
                'format': 'best',
                'outtmpl': 'video.mp4',
                'quiet': True,
                'nocheckcertificate': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(call.message.chat.id, video)
            os.remove('video.mp4')

        elif call.data == "audio":
            bot.edit_message_text("⏳ Musiqa qidirilmoqda (YouTube blokini aylanib o'tish)...", call.message.chat.id, status.message_id)
            
            # YouTube blokidan qochish uchun Soundcloud'dan qidirish sozlamasi
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.mp3',
                'default_search': 'scsearch:', # SoundCloud qidiruvi
                'quiet': True,
                'nocheckcertificate': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('audio.mp3', 'rb') as audio:
                bot.send_audio(call.message.chat.id, audio)
            os.remove('audio.mp3')

        bot.delete_message(call.message.chat.id, status.message_id)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Xatolik yuz berdi: {str(e)}")

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()
