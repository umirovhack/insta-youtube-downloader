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
    # 1. Qisqa audio yuklash (Shazam uchun)
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
        
        # 2. Shazam orqali musiqani tanish
        out = await shazam.recognize_song('temp_shazam.mp3')
        
        if out['matches']:
            track_title = out['track']['title']
            track_artist = out['track']['subtitle']
            search_query = f"{track_artist} {track_title}"
            bot.edit_message_text(f"🔍 Musiqa topildi: {search_query}. To'liq versiyasi yuklanmoqda...", chat_id, status_id)
            
            # 3. To'liq musiqani YouTubedan qidirib yuklash
            final_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'final_music.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                'quiet': True
            }
            with yt_dlp.YoutubeDL(final_opts) as ydl:
                ydl.download([f"ytsearch1:{search_query}"])
            
            with open('final_music.mp3', 'rb') as f:
                bot.send_audio(chat_id, f, caption=f"✅ {search_query} (To'liq versiya)")
        else:
            with open('temp_shazam.mp3', 'rb') as f:
                bot.send_audio(chat_id, f, caption="✅ Videodagi ovoz (Shazam topa olmadi)")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Audio jarayonida xato: {e}")

    # Tozalash
    for f in glob.glob("temp_shazam*") + glob.glob("final_music*"):
        if os.path.exists(f): os.remove(f)

@bot.callback_query_handler(func=lambda call: True
