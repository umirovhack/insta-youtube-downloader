import telebot
import yt_dlp
import os
import asyncio
from shazamio import Shazam
from telebot import types

# --- SOZLAMALAR ---
TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'
bot = telebot.TeleBot(TOKEN)
shazam = Shazam()

# Vaqtincha ma'lumotlarni saqlash
user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men universal botman: \n\n"
                          "1. 🔗 YouTube/Insta link yuboring (Video/Audio uchun)\n"
                          "2. 🎙 Musiqa parchasini yuboring (Shazam qilaman)\n"
                          "3. 📝 Musiqa nomini yozing (Qidirib topaman)!")

# --- 1 & 3: LINKLAR VA NOMI ORQALI QIDIRUV ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    # Agar bu link bo'lsa
    if "youtube.com" in url or "youtu.be" in url or "instagram.com" in url:
        user_links[message.chat.id] = url
        markup = types.InlineKeyboardMarkup()
        btn_video = types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video")
        btn_audio = types.InlineKeyboardButton("🎵 Musiqa (SoundCloud)", callback_data="audio")
        markup.add(btn_video, btn_audio)
        bot.send_message(message.chat.id, "Nima yuklamoqchisiz?", reply_markup=markup)
    
    # Agar bu shunchaki matn bo'lsa (Musiqa nomi deb hisoblaymiz)
    else:
        status = bot.send_message(message.chat.id, f"🔍 '{url}' qidirilmoqda...")
        download_and_send(message.chat.id, f"scsearch:{url}", status.message_id)

# --- 2: GOLOS (OVOZ) ORQALI SHAZAM ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    status = bot.send_message(message.chat.id, "🎧 Musiqa tahlil qilinmoqda...")
    
    file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open("shazam_check.ogg", "wb") as f:
        f.write(downloaded_file)
    
    # Shazam orqali aniqlash
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    out = loop.run_until_complete(shazam.recognize_song("shazam_check.ogg"))
    
    if out['matches']:
        track_name = out['track']['share']['subject']
        bot.edit_message_text(f"✅ Topildi: {track_name}\n⏳ Yuklab olinmoqda...", message.chat.id, status.message_id)
        download_and_send(message.chat.id, f"scsearch:{track_name}", status.message_id)
    else:
        bot.edit_message_text("❌ Afsuski, musiqani aniqlab bo'lmadi.", message.chat.id, status.message_id)
    
    if os.path.exists("shazam_check.ogg"):
        os.remove("shazam_check.ogg")

# --- YUKLASH FUNKSIYASI ---
def download_and_send(chat_id, search_query, status_id, is_video=False):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_video else 'bestaudio/best',
            'outtmpl': 'downloaded_file.%(ext)s',
            'quiet': True,
            'nocheckcertificate': True,
            'default_search': 'ytsearch' if "instagram.com" in search_query else 'scsearch'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            filename = ydl.prepare_filename(info)
        
        with open(filename, 'rb') as f:
            if is_video:
                bot.send_video(chat_id, f)
            else:
                bot.send_audio(chat_id, f)
        
        os.remove(filename)
        bot.delete_message(chat_id, status_id)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_links.get(call.message.chat.id)
    if not url: return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    status = bot.send_message(call.message.chat.id, "⏳ Jarayon ketyapti...")
    
    if call.data == "video":
        download_and_send(call.message.chat.id, url, status.message_id, is_video=True)
    elif call.data == "audio":
        download_and_send(call.message.chat.id, url, status.message_id, is_video=False)

if __name__ == "__main__":
    bot.infinity_polling()
