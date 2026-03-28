import telebot
import google.generativeai as genai
import os
import PIL.Image
from telebot import types

# --- SOZLAMALAR ---
# Telegram Bot Token
TELEGRAM_TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'

# Gemini API Key
GEMINI_API_KEY = 'AIzaSyDih1CxOtnxqYOSM2CuBUVjYs_eYhWzRuI'

# Bot va AI'ni sozlash
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        f"🌟 **Assalomu alaykum, {message.from_user.first_name}!**\n\n"
        "Men **@um1rov77** tomonidan yaratilgan aqlli AI botman! 🤖\n\n"
        "✨ **Nimalar qila olaman?**\n"
        "💬 **Savol-javob:** Xohlagan mavzuda savol bering, javob beraman.\n"
        "🖼 **Rasm tahlili:** Menga rasm yuboring va u haqida so'rang.\n"
        "💻 **Dasturlash:** Kod yozishda va xatolarni topishda yordam beraman."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- XABARLARNI QAYTA ISHLASH ---
@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    chat_id = message.chat.id

    # 1. AGAR RASM YUBORILSA
    if message.content_type == 'photo':
        status = bot.send_message(chat_id, "🧐 _Rasmni tahlil qilyapman..._", parse_mode="Markdown")
        try:
            # Rasmni yuklab olish
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            temp_path = f"img_{chat_id}.jpg"
            
            with open(temp_path, "wb") as f:
                f.write(downloaded)
            
            # AI orqali tahlil qilish
            img = PIL.Image.open(temp_path)
            prompt = message.caption if message.caption else "Ushbu rasmda nima borligini tushuntirib ber."
            response = model.generate_content([prompt, img])
            
            # Javobni yuborish
            bot.edit_message_text(response.text, chat_id, status.message_id)
            
            # Vaqtincha faylni o'chirish
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            bot.edit_message_text("❌ Rasmni tahlil qilishda xatolik yuz berdi.", chat_id, status.message_id)

    # 2. AGAR MATNLI SAVOL YUBORILSA
    elif message.content_type == 'text':
        status = bot.send_message(chat_id, "🤖 _O'ylayapman..._", parse_mode="Markdown")
        try:
            # AI'ga savolni yuborish
            response = model.generate_content(message.text)
            
            # Javobni yuborish
            bot.edit_message_text(response.text, chat_id, status.message_id)
        except Exception as e:
            bot.edit_message_text("❌ Kechirasiz, hozir javob bera olmayman. Keyinroq urinib ko'ring.", chat_id, status.message_id)

if __name__ == "__main__":
    bot.infinity_polling()
