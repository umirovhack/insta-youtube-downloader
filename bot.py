import telebot
import google.generativeai as genai
import os
import PIL.Image

# --- SOZLAMALAR ---
# Telegram Bot Token (BotFather'dan olingan)
TELEGRAM_TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'

# Yangi Gemini API Key (Siz nusxalagan kalit)
GEMINI_API_KEY = 'AIzaSyDYIulq1NMUajVsLPrrHa7USQSC72jzdeU'

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
        "💬 **Savol-javob:** Menga xohlagan savolingizni yozing.\n"
        "🖼 **Rasm tahlili:** Rasm yuboring, uni tushuntirib beraman.\n"
        "💻 **Dasturlash:** C, Flutter va boshqa tillarda yordam beraman."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- XABARLARNI QAYTA ISHLASH ---
@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    chat_id = message.chat.id

    # 1. AGAR RASM YUBORILSA
    if message.content_type == 'photo':
        status = bot.send_message(chat_id, "🧐 _Rasmni ko'ryapman..._", parse_mode="Markdown")
        try:
            # Rasmni yuklab olish
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            temp_path = f"img_{chat_id}.jpg"
            
            with open(temp_path, "wb") as f:
                f.write(downloaded)
            
            # AI orqali tahlil qilish
            img = PIL.Image.open(temp_path)
            prompt = message.caption if message.caption else "Bu rasmda nima borligini tushuntirib ber."
            response = model.generate_content([prompt, img])
            
            # Javobni yuborish
            bot.edit_message_text(response.text, chat_id, status.message_id)
            
            # Faylni o'chirish
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {str(e)}", chat_id, status.message_id)

    # 2. AGAR MATNLI SAVOL YUBORILSA
    elif message.content_type == 'text':
        # Start buyrug'ini o'tkazib yuboramiz
        if message.text.startswith('/'): return

        status = bot.send_message(chat_id, "🤖 _O'ylayapman..._", parse_mode="Markdown")
        try:
            # AI'ga savolni yuborish
            response = model.generate_content(message.text)
            
            # Javobni yuborish
            bot.edit_message_text(response.text, chat_id, status.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Kechirasiz, xato yuz berdi: {str(e)}", chat_id, status.message_id)

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling()
