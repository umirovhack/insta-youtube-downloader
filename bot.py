import telebot
from telebot import types
from deep_translator import GoogleTranslator

# BOT TOKEN
TOKEN = "8322130528:AAGMPhK9p1sT5kSJMntqOXwZFt2UcjPx4Nk"
bot = telebot.TeleBot(TOKEN)

# Asosiy menyu
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🇺🇿 O'zbekcha -> Inglizcha")
    btn2 = types.KeyboardButton("🇬🇧 Inglizcha -> O'zbekcha")
    btn3 = types.KeyboardButton("🇷🇺 Ruscha -> O'zbekcha")
    markup.add(btn1, btn2, btn3)
    return markup

# Holatni saqlash (qaysi tildan qaysi tilga tarjima qilinayotganini bilish uchun)
user_lang = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        f"Salom {message.from_user.first_name}!\nMen aqlli Tarjimon botman. Qaysi yo'nalishda tarjima qilamiz?", 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text in ["🇺🇿 O'zbekcha -> Inglizcha", "🇬🇧 Inglizcha -> O'zbekcha", "🇷🇺 Ruscha -> O'zbekcha"])
def set_direction(message):
    if "O'zbekcha -> Inglizcha" in message.text:
        user_lang[message.chat.id] = ('uz', 'en')
    elif "Inglizcha -> O'zbekcha" in message.text:
        user_lang[message.chat.id] = ('en', 'uz')
    elif "Ruscha -> O'zbekcha" in message.text:
        user_lang[message.chat.id] = ('ru', 'uz')
    
    bot.send_message(message.chat.id, "Endi tarjima qilinishi kerak bo'lgan matnni yuboring:")

@bot.message_handler(func=lambda message: True)
def translate_text(message):
    chat_id = message.chat.id
    
    # Agar foydalanuvchi yo'nalish tanlamagan bo'lsa, avtomatik aniqlash (Auto-detect)
    if chat_id not in user_lang:
        src, dest = 'auto', 'uz'
    else:
        src, dest = user_lang[chat_id]

    try:
        translated = GoogleTranslator(source=src, target=dest).translate(message.text)
        bot.reply_to(message, f"✨ **Tarjima:**\n\n{translated}", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, "❌ Tarjimada xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")

if __name__ == "__main__":
    print("Translate bot ishlamoqda...")
    bot.infinity_polling()
