import telebot
import google.generativeai as genai
import os
import PIL.Image
import time

# --- SOZLAMALAR ---
# 1. Telegram Bot Token (Yangi olingan token)
TELEGRAM_TOKEN = '8322130528:AAGMPhK9p1sT5kSJMntqOXwZFt2UcjPx4Nk'

# 2. Gemini API Key
GEMINI_API_KEY = 'AIzaSyDYIulq1NMUajVsLPrrHa7USQSC72jzdeU'

# Bot va AI'ni sozlash
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        f"🌟 **Assalomu alaykum, {message.from_user.first_name}!**\n\n"
        "Men **@um1rov77** tomonidan yaratilgan aqlli AI botman! 🤖\n\n"
        "💬 Savol yozing yoki rasm yuboring, javob beraman!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- XABARLARNI QAYTA ISHLASH ---
@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    chat_id = message.chat.id
    
    if message.content_type == 'photo':
        status = bot.send_message(chat_id, "🧐 _Rasmni tahlil qilyapman..._", parse_mode="Markdown")
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            temp_path = f"img_{chat_id}.jpg"
            
            with open(temp_path, "wb") as f:
                f.write(downloaded)
            
            img = PIL.Image.open(temp_path)
            prompt = message.caption if message.caption else "Bu rasmda nima borligini tushuntirib ber."
            response = model.generate_content([prompt, img])
            
            bot.edit_message_text(response.text, chat_id, status.message_id)
            if os.path.exists(temp_path): os.remove(temp_path)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {str(e)}", chat_id, status.message_id)

    elif message.content_type == 'text':
        if message.text.startswith('/'): return
        status = bot.send_message(chat_id, "🤖 _O'ylayapman..._", parse_mode="Markdown")
        try:
            response = model.generate_content(message.text)
            bot.edit_message_text(response.text, chat_id, status.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xato: {str(e)}", chat_id, status.message_id)

# --- KONFLIKTNI OLIB TASHLASH VA ISHGA TUSHIRISH ---
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    # Telegram-dagi eski ulanishlarni o'chirish (Muhim!)
    bot.remove_webhook()
    time.sleep(1) 
    
    # Render port xatosini chetlab o'tish uchun infinity polling
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
