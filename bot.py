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

# Foydalanuvchi linklarini vaqtincha saqlash
user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "👋 Salom! Men universal yuklovchi botman:\n\n"
        "1️⃣ **Link yuboring:** Insta/YouTube video yoki audio yuklash.\n"
        "2️⃣ **Nomini yozing:** Musiqani qidirib topish.\n"
        "3️⃣ **Golos yuboring:** Musiqani Shazam orqali topish."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

# --- YUKLASH VA YUBORISH FUNKSIYASI ---
def download_and_send(chat_id, search_query, status_id, is_video=False):
    try:
        ext = 'mp4' if is_video else 'mp3'
        filename = f"file_{chat_id}.{ext}"
        
        # Agar eski fayl qolib ketgan bo'lsa o'chirish
        if os.path.exists(filename):
            os.remove(filename)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if is_video else 'bestaudio/best',
            'outtmpl': filename,
            'quiet': True,
            'nocheckcertificate': True,
            'default_search': 'ytsearch' if ("youtube.com" in search_query or "instagram.com" in search_query) else 'scsearch',
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                if is_video:
                    bot.send_video(chat_id, f, caption="✅ Video tayyor!")
                else:
                    bot.send_audio(chat_id, f, caption="🎵 Musiqa topildi!")
            os.remove(filename)
        else:
            bot.send_message(chat_id, "❌ Faylni yuklab bo'lmadi. Qaytadan urinib ko'ring.")
            
        bot.delete_message(chat_id, status_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik: {str(e)}")

# --- GOLOS (SHAZAM) QISMI ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    status = bot.send_message(message.chat.id, "🎧 Musiqa tahlil qilinmoqda...")
    
    file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    shazam_file = f"shazam_{message.chat.id}.ogg"
    with open(shazam_file, "wb") as f:
        f.write(downloaded_file)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    out = loop.run_until_complete(shazam.recognize_song(shazam_file))
    
    if out.get('matches'):
        track_name = out['track']['share']['subject']
        bot.edit_message_text(f"✅ Topildi: {track_name}\n⏳ Yuklab olinmoqda...", message.chat.id, status.message_id)
        download_and_send(message.chat.id, track_name, status.message_id)
    else:
        bot.edit_message_text("❌ Afsuski, musiqani aniqlab bo'lmadi.", message.chat.id, status.message_id)
    
    if os.path.exists(shazam_file):
        os.remove(shazam_file)

# --- MATN VA LINKLAR ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    if "http" in text:
        user_links[message.chat.id] = text
        markup = types.InlineKeyboardMarkup()
        btn_v = types.InlineKeyboardButton("🎬 Video", callback_data="video")
        btn_a = types.InlineKeyboardButton("🎵 Musiqa", callback_data="audio")
        markup.add(btn_v, btn_a)
        bot.send_message(message.chat.id, "Nima yuklaymiz?", reply_markup=markup)
    else:
        status = bot.send_message(message.chat.id, f"🔍 '{text}' qidirilmoqda...")
        download_and_send(message.chat.id, text, status.message_id)

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
    print("Bot ishlamoqda...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
