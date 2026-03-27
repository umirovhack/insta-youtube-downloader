import telebot
import yt_dlp
import os
import asyncio
from shazamio import Shazam
from telebot import types

# --- SOZLAMALAR ---
# Tokeningizni tekshiring, o'zgarmagan bo'lishi kerak
TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'
bot = telebot.TeleBot(TOKEN)
shazam = Shazam()

# Foydalanuvchi yuborgan linklarni vaqtincha xotirada saqlash
user_links = {}

# --- 1. KUTIB OLISH (START BUYRUG'I) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"👋 **Salom, {user_name}!**\n\n"
        "🤖 **Umirov Downloader** botiga xush kelibsiz!\n"
        "Men sizga ijtimoiy tarmoqlardan video yuklashda va musiqalar topishda yordam beraman.\n\n"
        "📌 **Imkoniyatlarim:**\n"
        "🔹 Insta/YouTube link yuboring -> Video yoki MP3 yuklayman.\n"
        "🔹 Qo'shiq nomini yozing -> Uni topib beraman.\n"
        "🔹 Ovozli xabar (Golos) yuboring -> Shazam orqali topaman.\n\n"
        "👇 Quyidagi tugmalardan foydalanishingiz mumkin:"
    )
    
    # Asosiy menyu tugmalari (Keyboard)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_search = types.KeyboardButton("🔍 Musiqa qidirish")
    btn_help = types.KeyboardButton("ℹ️ Yordam")
    markup.add(btn_search, btn_help)
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

# --- 2. YUKLASH VA YUBORISH LOGIKASI ---
def download_and_send(chat_id, search_query, status_id, is_video=False):
    try:
        # Har bir foydalanuvchi uchun unikal fayl nomi
        ext = 'mp4' if is_video else 'mp3'
        filename = f"file_{chat_id}_{os.urandom(3).hex()}.{ext}"
        
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
                    bot.send_video(chat_id, f, caption="🎬 Video tayyor! \n\n🚀 @umirov_hack")
                else:
                    bot.send_audio(chat_id, f, caption="🎵 Musiqa topildi! \n\n🚀 @umirov_hack")
            os.remove(filename) # Joyni bo'shatish uchun o'chiramiz
        else:
            bot.send_message(chat_id, "❌ Faylni yuklashda xatolik yuz berdi.")
            
        bot.delete_message(chat_id, status_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik: Link noto'g'ri yoki server band.\n(Xato: {str(e)})")

# --- 3. SHAZAM (OVOZ ORQALI QIDIRUV) ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    status = bot.send_message(message.chat.id, "🎧 Musiqa tahlil qilinmoqda, kuting...")
    
    try:
        file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        temp_shazam = f"shazam_{chat_id}.ogg"
        with open(temp_shazam, "wb") as f:
            f.write(downloaded_file)
        
        # Shazamio asinxron ishlaydi
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        out = loop.run_until_complete(shazam.recognize_song(temp_shazam))
        
        if out.get('matches'):
            track_name = out['track']['share']['subject']
            bot.edit_message_text(f"✅ Topildi: **{track_name}**\n⏳ Yuklab olinmoqda...", message.chat.id, status.message_id, parse_mode="Markdown")
            download_and_send(message.chat.id, track_name, status.message_id)
        else:
            bot.edit_message_text("❌ Musiqani aniqlab bo'lmadi. Ovoz aniqroq bo'lishi kerak.", message.chat.id, status.message_id)
        
        if os.path.exists(temp_shazam):
            os.remove(temp_shazam)
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Shazam jarayonida xato yuz berdi.")

# --- 4. MATN VA LINKLARNI BOSHQARISH ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    if text == "ℹ️ Yordam":
        bot.send_message(message.chat.id, "📖 **Yordam:**\n\n1. Instagram Reels yoki YouTube linkini yuboring.\n2. Paydo bo'lgan tugmalardan 'Video' yoki 'Musiqa'ni tanlang.\n3. Qo'shiq topish uchun shunchaki nomini yozing.", parse_mode="Markdown")
    
    elif text == "🔍 Musiqa qidirish":
        bot.send_message(message.chat.id, "✍️ Musiqa yoki ijrochi nomini yozib yuboring:")
    
    elif "http" in text:
        user_links[message.chat.id] = text
        markup = types.InlineKeyboardMarkup()
        btn_v = types.InlineKeyboardButton("🎬 Video yuklash", callback_data="video")
        btn_a = types.InlineKeyboardButton("🎵 MP3 (Audio) yuklash", callback_data="audio")
        markup.add(btn_v)
        markup.add(btn_a)
        bot.send_message(message.chat.id, "🎥 Link qabul qilindi. Nima yuklaymiz?", reply_markup=markup)
    
    else:
        # Shunchaki matn yozilsa, qidiruv deb hisoblaymiz
        status = bot.send_message(message.chat.id, f"🔍 '{text}' qidirilmoqda...")
        download_and_send(message.chat.id, text, status.message_id)

# --- 5. TUGMALARNI QAYTA ISHLASH (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    url = user_links.get(call.message.chat.id)
    if not url:
        bot.answer_callback_query(call.id, "Xatolik: Link topilmadi, qaytadan yuboring.")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    status = bot.send_message(call.message.chat.id, "⏳ Jarayon boshlandi...")
    
    if call.data == "video":
        download_and_send(call.message.chat.id, url, status.message_id, is_video=True)
    elif call.data == "audio":
        download_and_send(call.message.chat.id, url, status.message_id, is_video=False)

# --- 6. BOTNI ISHGA TUSHIRISH ---
if __name__ == "__main__":
    print("🚀 Bot muvaffaqiyatli ishga tushdi...")
    bot.infinity_polling(timeout=15, long_polling_timeout=5)
