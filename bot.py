import telebot
import google.generativeai as genai
import os
import PIL.Image

# --- SOZLAMALAR ---
# Telegram Bot Token
TELEGRAM_TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'

# Gemini API Key (Google AI Studio'dan olgan kalitingizni shu yerga qo'ying)
GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY_HERE'

# Bot va AI'ni sozlash
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome = (f"🌟 **Assalomu alaykum, {message.from_user.first_name}!**\n\n"
               "Men **Gemini AI** aqlli botiman. ✨\n"
               "Menga xohlagan savolingizni yozing yoki rasm yuboring!")
    bot.send_message(message.chat.id, welcome, parse_mode="Markdown")

# --- MATNLI SAVOLLAR (AI) ---
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    status = bot.send_message(message.chat.id, "🤔 _O'ylayapman..._", parse_mode="Markdown")
    try:
        response = model.generate_content(message.text)
        bot.edit_message_text(response.text, message.chat.id, status.message_id)
    except Exception as e:
        bot.edit_message_text("❌ Xatolik yuz berdi. API Keyni tekshiring.", message.chat.id, status.message_id)

# --- RASMLARNI TAHLIL QILISH ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status = bot.send_message(message.chat.id, "🧐 _Rasmni tahlil qilyapman..._", parse_mode="Markdown")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        temp_path = f"img_{message.chat.id}.jpg"
        with open(temp_path, "wb") as f:
            f.write(downloaded_file)
            
        img = PIL.Image.open(temp_path)
        prompt = message.caption if message.caption else "Ushbu rasm haqida ma'lumot ber."
        
        response = model.generate_content([prompt, img])
        bot.edit_message_text(response.text, message.chat.id, status.message_id)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except Exception as e:
        bot.edit_message_text("❌ Rasmni tahlil qilib bo'lmadi.", message.chat.id, status.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
