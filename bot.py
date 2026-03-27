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

# Ma'lumotlarni vaqtincha saqlash
user_data = {}

# --- START BUYRUG'I (YANGILANGAN VA CHIROYLI) ---
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"🌟 **Assalomu alaykum, {user_name}!**\n\n"
        "Sizni eng qulay va tezkor yuklovchi botda ko'rganimizdan xursandmiz! ✨\n\n"
        "✨ **Bot nimalar qila oladi?**\n"
        "📸 **Instagram:** Link yuboring va videoni yuqori sifatda (ovozli) yuklab oling.\n"
        "🎵 **Musiqa:** Qo'shiq nomini yozing yoki audio/golos yuboring — men uni darhol topib beraman.\n"
        "🔟 **Variantlar:** Men sizga har doim 10 tagacha eng yaxshi variantni taklif qilaman.\n\n"
        "🚀 *Shunchaki link yuboring yoki musiqa nomini yozing!*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- ASOSIY YUKLASH FUNKSIYASI ---
def download_and_send(chat_id, url, status_id, is_video=True):
    try:
        ext = 'mp4' if is_video else 'mp3'
        filename = f"file_{chat_id}_{os.urandom(2).hex()}.{ext}"
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best' if is_video else 'bestaudio/best',
            'outtmpl': filename,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                # FAQAT USERNAME VA STIKER
                caption_text = "✨ @um1rov77"
                
                if is_video:
                    bot.send_video(chat_id, f, caption=caption_text, supports_streaming=True)
                else:
                    bot.send_audio(chat_id, f, caption=caption_text)
            os.remove(filename)
        else:
            bot.send_message(chat_id, "❌ Faylni yuklashda xatolik yuz berdi.")
        
        bot.delete_message(chat_id, status_id)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

# --- GOLOS (SHAZAM) FUNKSIYASI ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    status = bot.send_message(message.chat.id, "🎧 Musiqa tahlil qilinmoqda...")
    try:
        file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_file = f"temp_{message.chat.id}.ogg"
        
        with open(temp_file, "wb") as f:
            f.write(downloaded_file)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        out = loop.run_until_complete(shazam.recognize_song(temp_file))
        
        if out.get('matches'):
            track_name = out['track']['share']['subject']
            bot.edit_message_text(f"✅ Topildi: {track_name}\n⏳ Yuklanmoqda...", message.chat.id, status.message_id)
            # Avtomatik MP3 qidirish va yuborish
            download_and_send(message.chat.id, f"ytsearch1:{track_name}", status.message_id, is_video=False)
        else:
            bot.edit_message_text("❌ Musiqa topilmadi.", message.chat.id, status.message_id)
        
        if os.path.exists(temp_file): os.remove(temp_file)
    except:
        bot.send_message(message.chat.id, "❌ Ovozni tahlil qilib bo'lmadi.")

# --- INSTAGRAM VA MATNLI QIDIRUV (10 TA VARIANT) ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text
    chat_id = message.chat.id

    if "instagram.com" in text:
        status = bot.send_message(chat_id, "🔍 Instagram tekshirilmoqda...")
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=False)
                # Karusel bo'lsa barcha qismlarni, bo'lmasa bittasini oladi
                results = info.get('entries', [info])[:10]
                user_data[chat_id] = results
                
                markup = types.InlineKeyboardMarkup()
                buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"inst_{i}") for i in range(len(results))]
                
                # Tugmalarni 5 tadan qatorga terish
                markup.row(*buttons[:5])
                if len(buttons) > 5: markup.row(*buttons[5:])
                
                bot.edit_message_text("📸 Instagram variantlari topildi. Yuklash uchun raqamni tanlang:", 
                                     chat_id, status.message_id, reply_markup=markup)
        except:
            bot.edit_message_text("❌ Instagram linkidan ma'lumot olib bo'lmadi.", chat_id, status.message_id)

    else:
        status = bot.send_message(chat_id, f"🔍 '{text}' qidirilmoqda...")
        try:
            # 10 ta eng yaxshi natijani qidirish
            ydl_opts = {'quiet': True, 'default_search': 'ytsearch10'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch10:{text}", download=False)
                results = info['entries']
                user_data[chat_id] = results
                
                response_text = f"🎵 **'{text}' bo'yicha natijalar:**\n\n"
                markup = types.InlineKeyboardMarkup()
                
                buttons = []
                for i, entry in enumerate(results, 1):
                    title = entry.get('title', 'Noma\'lum')[:40]
                    response_text += f"{i}. {title}\n"
                    buttons.append(types.InlineKeyboardButton(str(i), callback_data=f"mus_{i-1}"))
                
                markup.row(*buttons[:5])
                if len(buttons) > 5: markup.row(*buttons[5:])
                
                bot.edit_message_text(response_text, chat_id, status.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.edit_message_text("❌ Hech qanday musiqa topilmadi.", chat_id, status.message_id)

# --- TUGMALARNI QAYTA ISHLASH ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    results = user_data.get(chat_id)
    
    if not results:
        bot.answer_callback_query(call.id, "Ma'lumot topilmadi, iltimos qayta qidiring.")
        return

    index = int(call.data.split('_')[1])
    selected_url = results[index].get('webpage_url') or results[index].get('url')
    
    bot.delete_message(chat_id, call.message.message_id)
    status = bot.send_message(chat_id, "⏳ Jarayon boshlandi...")

    # Instagram bo'lsa video, qidiruv bo'lsa audio yuklanadi
    is_vid = True if call.data.startswith("inst") else False
    download_and_send(chat_id, selected_url, status.message_id, is_video=is_vid)

if __name__ == "__main__":
    bot.infinity_polling()
