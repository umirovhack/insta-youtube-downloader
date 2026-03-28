import telebot
from telebot import types
import requests
import math

# --- SOZLAMALAR ---
TOKEN = '8322130528:AAGMPhK9p1sT5kSJMntqOXwZFt2UcjPx4Nk'
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchi yozayotgan misolni saqlash uchun
user_data = {}

# --- TUGMALAR ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔢 Kalkulyator", "💵 Valyuta kursi")
    markup.add("🕌 Namoz vaqtlari", "☁️ Ob-havo")
    return markup

def calc_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("7", "8", "9", "/")
    markup.row("4", "5", "6", "*")
    markup.row("1", "2", "3", "-")
    markup.row("0", "C", "=", "+")
    markup.row("🔙 Orqaga")
    return markup

# --- API FUNKSIYALAR ---
def get_currency():
    try:
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = res[0]['Rate']
        return f"🇺🇸 1 USD = {usd} so'm\n🇪🇺 1 EUR = {res[1]['Rate']} so'm\n🗓 Sana: {res[0]['Date']}"
    except: return "⚠️ Kursni olib bo'lmadi."

def get_prayer_times():
    # Toshkent uchun namunaviy vaqtlar (Real API ulamoqchi bo'lsangiz ayting)
    return "📍 Toshkent vaqti (Taxminiy):\n🏙 Bamdod: 05:08\n☀️ Quyosh: 06:14\n Peshin: 12:28\n🌇 Asr: 16:51\n🌆 Shom: 18:44\n🌃 Xufton: 20:01"

# --- ASOSIY MANTIQ ---
@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = ""
    bot.send_message(message.chat.id, "🌟 **Umirov Utility Bot**ga xush kelibsiz!\n\nKerakli bo'limni tanlang:", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_all(message):
    cid = message.chat.id
    text = message.text

    if cid not in user_data: user_data[cid] = ""

    if text == "🔢 Kalkulyator":
        user_data[cid] = ""
        bot.send_message(cid, "Misolni kiritishni boshlang:", reply_markup=calc_keyboard())
    
    elif text == "💵 Valyuta kursi":
        bot.send_message(cid, get_currency())
    
    elif text == "🕌 Namoz vaqtlari":
        bot.send_message(cid, get_prayer_times())
    
    elif text == "☁️ Ob-havo":
        bot.send_message(cid, "🌤 Toshkentda hozir +24°C, havo ochiq.\nBugun yog'ingarchilik kutilmaydi.")
    
    elif text == "🔙 Orqaga":
        bot.send_message(cid, "Asosiy menyuga qaytdingiz:", reply_markup=main_menu())
    
    elif text == "C":
        user_data[cid] = ""
        bot.send_message(cid, "📝 Tozalandi. Yangi misol yozing:")

    elif text == "=":
        try:
            res = eval(user_data[cid].replace('^', '**'))
            bot.send_message(cid, f"🔢 Natija: `{res}`", parse_mode="Markdown")
            user_data[cid] = str(res)
        except:
            bot.send_message(cid, "❌ Xato! Misolni tekshiring.")
            user_data[cid] = ""

    elif text in "0123456789+-*/.":
        user_data[cid] += text
        # Har bir raqam bosilganda hozirgi holatni ko'rsatib turish
        bot.send_message(cid, f"📝 `{user_data[cid]}`", parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
