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

# Foydalanuvchi linklarini saqlash
user_links = {}

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 Salom, {user_name}!\n\n"
        "🤖 **Umirov Downloader** botiga xush kelibsiz!\n"
        "Men sizga Instagram va YouTube'dan sifatli video yuklab beraman.\n\n"
        "👇 Link yuboring va tugmani tanlang!"
    )
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔍 Musiqa qidirish"), types.KeyboardButton("ℹ️ Yordam"))
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# --- ASOSIY YUKLASH FUNKSIYASI ---
def download_and_send(chat_id, search_query, status_id, is_video=False):
    try:
        ext = 'mp4' if is_video else 'mp3'
        filename = f"file_{chat_id}_{os.urandom(2).hex()}.{ext}"
        
        # Instagram va YouTube uchun eng yaxshi format sozlamalari
        if is_video:
            # Eng yaxshi video va audio birlashtirilgan formatni qidiradi
            format_opt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            format_opt = 'bestaudio/best'

        ydl_opts = {
            'format': format_opt,
            'outtmpl': filename,
            'quiet': True,
            'nocheckcertificate': True,
            'merge_output_format': 'mp4' if is_video else None,
            'default_search': 'ytsearch' if ("http" not in search_query) else None,
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                # Username qismi @um1rov77 qilib belgilandi
                caption_text = f"✅ Tayyor! \n\n👤 Yukladi: @um1rov77\n🚀 @umirov_hack"
                
                if is_video:
                    bot.send_video(chat_id, f, caption=caption_text, supports_streaming=True)
                else:
                    bot.send_audio(chat_id, f, caption=caption_text)
            os.remove(filename)
        else:
            bot.send_message(chat_id, "❌ Faylni tayyorlashda xatolik. Linkni tekshiring.")
            
        bot.delete_message(chat_id, status_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.\n\n(Xato: {str(e)})")

# --- GOLOS / SHAZAM ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    status = bot.send_message(message.chat.id, "🎧 Musiqa tahlil qilinmoqda...")
    try:
        file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_shazam = f"sh_temp_{message.chat.id}.ogg"
        with open(temp_shazam, "wb") as f:
            f.write(downloaded_file)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        out = loop.run_until_complete(shazam.recognize_song(temp_shazam))
        
        if out.get('matches'):
            track_name = out['track']['share']['subject']
            bot.edit_message_text(f"✅ Topildi: {track_name}\n⏳ Yuklanmoqda...", message.chat.id, status.message_id)
            download_and_send(message.chat.id, track_name, status.message_id)
        else:
            bot.edit_message_text("❌ Musiqa topilmadi.", message.chat.id, status.message_id)
        
        if os.path.exists(temp_shazam): os.remove(temp_shazam)
    except:
        bot.send_message(message.chat.id, "❌ Xato yuz berdi.")

# --- MATN VA LINKLAR ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text
    if text == "ℹ️ Yordam":
        bot.reply_to(message, "Link yuboring va nima yuklashni tanlang!")
    elif text == "🔍 Musiqa qidirish":
        bot.reply_to(message, "Qo'shiq nomini yozib yuboring:")
    elif "http" in text:
        user_links[message.chat.id] = text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video"))
        markup.add(types.InlineKeyboardButton("🎵 MP3 yuklash", callback_data="audio"))
        bot.send_message(message.chat.id, "🎥 Nima yuklaymiz?", reply_markup=markup)
    else:
        status = bot.send_message(message.chat.id, f"🔍 '{text}' qidirilmoqda...")
        download_and_send(message.chat.id, text, status.message_id)

# --- CALLBACK (TUGMALAR) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    url = user_links.get(call.message.chat.id)
    if not url: return
    bot.delete_message(call.message.chat.id, call.message.message_id)
    status = bot.send_message(call.message.chat.id, "⏳ Yuklash boshlandi...")
    
    if call.data == "video":
        download_and_send(call.message.chat.id, url, status.message_id, is_video=True)
    elif call.data == "audio":
        download_and_send(call.message.chat.id, url, status.message_id, is_video=False)

if __name__ == "__main__":
    bot.infinity_polling()
