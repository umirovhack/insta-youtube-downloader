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
user_data = {}

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"🌟 **Assalomu alaykum, {user_name}!**\n\n"
        "Sizni eng qulay yuklovchi botda ko'rganimizdan xursandmiz! ✨\n\n"
        "✨ **Bot imkoniyatlari:**\n"
        "📸 **Instagram:** Link yuboring, video yoki MP3 tanlang.\n"
        "🎵 **Musiqa:** Ismini yozing yoki Golos yuboring.\n"
        "🔟 **10 ta variant:** Eng yaxshi natijalarni tanlash imkoniyati.\n\n"
        "🚀 *Shunchaki link yuboring yoki musiqa nomini yozing!*"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- ASOSIY YUKLASH FUNKSIYASI ---
def download_and_send(chat_id, url, status_id, is_video=True):
    try:
        ext = 'mp4' if is_video else 'mp3'
        filename = f"f_{chat_id}_{os.urandom(2).hex()}.{ext}"
        
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
                caption_text = "✨ @um1rov77"
                if is_video:
                    bot.send_video(chat_id, f, caption=caption_text, supports_streaming=True)
                else:
                    bot.send_audio(chat_id, f, caption=caption_text)
            os.remove(filename)
        else:
            bot.send_message(chat_id, "❌ Faylni yuklashda xatolik yuz berdi.")
        
        bot.delete_message(chat_id, status_id)
    except Exception:
        bot.send_message(chat_id, "❌ Yuklash imkonsiz bo'ldi. Link xato bo'lishi mumkin.")

# --- GOLOS (SHAZAM) ---
@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice(message):
    status = bot.send_message(message.chat.id, "🎧 Musiqa tahlil qilinmoqda...")
    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_file = f"temp_{message.chat.id}.ogg"
        
        with open(temp_file, "wb") as f:
            f.write(downloaded_file)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        out = loop.run_until_complete(shazam.recognize_song(temp_file))
        
        if out.get('matches'):
            track_name = out['track']['share']['subject']
            bot.edit_message_text(f"✅ Topildi: **{track_name}**\n⏳ Yuklanmoqda...", message.chat.id, status.message_id, parse_mode="Markdown")
            download_and_send(message.chat.id, f"scsearch1:{track_name}", status.message_id, is_video=False)
        else:
            bot.edit_message_text("❌ Musiqa topilmadi.", message.chat.id, status.message_id)
        
        if os.path.exists(temp_file): os.remove(temp_file)
    except:
        bot.send_message(message.chat.id, "❌ Ovozni tahlil qilib bo'lmadi.")

# --- INSTAGRAM VA MATNLI QIDIRUV ---
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = message.text
    chat_id = message.chat.id

    if "instagram.com" in text:
        user_data[chat_id] = text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎬 Video yuklash", callback_data="ins_vid"))
        markup.add(types.InlineKeyboardButton("🎵 MP3 yuklash", callback_data="ins_aud"))
        bot.send_message(chat_id, "🎥 **Instagram linki aniqlandi.**\nNima yuklaymiz?", reply_markup=markup, parse_mode="Markdown")

    else:
        status = bot.send_message(chat_id, f"🔍 **'{text}'** qidirilmoqda...", parse_mode="Markdown")
        try:
            ydl_opts = {'quiet': True, 'default_search': 'scsearch10', 'nocheckcertificate': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"scsearch10:{text}", download=False)
                results = info['entries']
                user_data[chat_id] = results
                
                # Qidiruv natijalarini chiroyli ko'rinishga keltirish
                response_text = f"🎵 **'{text}' bo'yicha natijalar:**\n\n"
                for i, entry in enumerate(results, 1):
                    title = entry.get('title', 'Noma\'lum')[:45]
                    response_text += f"{i}. {title}\n"
                
                markup = types.InlineKeyboardMarkup()
                buttons = [types.InlineKeyboardButton(str(i+1), callback_data=f"mus_{i}") for i in range(len(results))]
                
                # Tugmalarni 5 tadan qilib chiroyli terish
                markup.row(*buttons[:5])
                if len(buttons) > 5:
                    markup.row(*buttons[5:])
                
                bot.edit_message_text(response_text, chat_id, status.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.edit_message_text("❌ Hech narsa topilmadi. Iltimos, aniqroq yozing.", chat_id, status.message_id)

# --- CALLBACK TUGMALARI ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    data = call.data
    
    if data.startswith("ins_"):
        url = user_data.get(chat_id)
        is_vid = True if data == "ins_vid" else False
        bot.delete_message(chat_id, call.message.message_id)
        status = bot.send_message(chat_id, "⏳ Jarayon boshlandi...")
        download_and_send(chat_id, url, status.message_id, is_video=is_vid)

    elif data.startswith("mus_"):
        results = user_data.get(chat_id)
        if not results: return
        index = int(data.split('_')[1])
        selected_url = results[index].get('url') or results[index].get('webpage_url')
        bot.delete_message(chat_id, call.message.message_id)
        status = bot.send_message(chat_id, "⏳ Yuklanmoqda...")
        download_and_send(chat_id, selected_url, status.message_id, is_video=False)

if __name__ == "__main__":
    bot.infinity_polling()
