import telebot
from telebot import types

# BOT TOKENINGIZ
TOKEN = "8322130528:AAGMPhK9p1sT5kSJMntqOXwZFt2UcjPx4Nk"
bot = telebot.TeleBot(TOKEN)

# Asosiy menyu tugmalari
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Kino Qidirish")
    btn2 = types.KeyboardButton("🎬 Asl Media")
    btn3 = types.KeyboardButton("📺 Yangi TV")
    btn4 = types.KeyboardButton("ℹ️ Ma'lumot")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# /start komandasi
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"👋 Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "🎬 **UmirovKino** botiga xush kelibsiz!\n"
        "Bu yerda siz eng sara kinolarni o'zbek tilida topishingiz mumkin.\n\n"
        "👇 Kerakli bo'limni tanlang:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode="Markdown")

# 🔍 Kino Qidirish (Umumiy)
@bot.message_handler(func=lambda message: message.text == "🔍 Kino Qidirish")
def search_start(message):
    msg = bot.send_message(message.chat.id, "🎬 Qidirilayotgan kino nomini kiriting:")
    bot.register_next_step_handler(msg, process_general_search)

def process_general_search(message):
    movie_name = message.text
    # Google orqali qidiruv linki (Uzmovi, i-kino va h.k. uchun)
    search_url = f"https://www.google.com/search?q={movie_name.replace(' ', '+')}+o'zbek+tilida+skachat+yoki+ko'rish"
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🌐 Google'dan natijalarni ko'rish", url=search_url)
    markup.add(btn)
    
    bot.send_message(message.chat.id, f"🔎 **{movie_name}** kinosi bo'yicha qidiruv natijalari tayyor:", reply_markup=markup, parse_mode="Markdown")

# 🎬 Asl Media Qidiruv
@bot.message_handler(func=lambda message: message.text == "🎬 Asl Media")
def asl_search_start(message):
    msg = bot.send_message(message.chat.id, "🎬 **Asl Media** saytidan qidirish uchun kino nomini yozing:")
    bot.register_next_step_handler(msg, process_asl_search)

def process_asl_search(message):
    movie_name = message.text
    search_url = f"https://aslmedia.net/index.php?do=search&subaction=search&story={movie_name.replace(' ', '+')}"
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🌐 AslMedia'da Ko'rish", url=search_url)
    markup.add(btn)
    
    bot.send_message(message.chat.id, f"🍿 **{movie_name}** kinosi AslMedia bazasidan qidirildi:", reply_markup=markup, parse_mode="Markdown")

# 📺 Yangi TV Qidiruv
@bot.message_handler(func=lambda message: message.text == "📺 Yangi TV")
def yangi_search_start(message):
    msg = bot.send_message(message.chat.id, "📺 **Yangi TV** platformasidan qidirish uchun kino nomini yozing:")
    bot.register_next_step_handler(msg, process_yangi_search)

def process_yangi_search(message):
    movie_name = message.text
    # Yangi TV qidiruv formati (agar sayti bo'lsa shunday bo'ladi)
    search_url = f"https://yangitv.uz/search?q={movie_name.replace(' ', '+')}"
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("🌐 Yangi TV'da Ko'rish", url=search_url)
    markup.add(btn)
    
    bot.send_message(message.chat.id, f"📡 **{movie_name}** kinosi Yangi TV platformasidan qidirildi:", reply_markup=markup, parse_mode="Markdown")

# ℹ️ Ma'lumot Bo'limi
@bot.message_handler(func=lambda message: message.text == "ℹ️ Ma'lumot")
def info_page(message):
    info_text = (
        "🤖 **Bot haqida:**\n"
        "UmirovKino bot orqali siz internetdagi eng mashhur o'zbekcha kino saytlaridan tezkor qidiruv amalga oshirishingiz mumkin.\n\n"
        "👨‍💻 **Dasturchi:** @umirovDev_bot\n"
        "🚀 **Versiya:** 2.0 (Kino Edition)"
    )
    bot.send_message(message.chat.id, info_text, parse_mode="Markdown")

# Har qanday boshqa matn kelsa
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(message.chat.id, "👇 Iltimos, menyudagi tugmalardan foydalaning:", reply_markup=main_menu())

if __name__ == "__main__":
    print("UmirovKino Bot ishga tushdi...")
    bot.infinity_polling()
