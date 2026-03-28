import telebot
from telebot import types

# --- SOZLAMALAR ---
TOKEN = '8322130528:AAGMPhK9p1sT5kSJMntqOXwZFt2UcjPx4Nk'
bot = telebot.TeleBot(TOKEN)

# --- FULL SAVOLLAR BAZASI ---
quiz_data = {
    "Matematika": {
        "Oson": [
            {"q": "5 + 7 = ?", "a": "12", "o": ["10", "12", "15", "11"]},
            {"q": "100 / 4 = ?", "a": "25", "o": ["20", "25", "30", "50"]},
            {"q": "25 * 3 = ?", "a": "75", "o": ["70", "75", "80", "65"]},
            {"q": "81 ning ildizi nechchi?", "a": "9", "o": ["7", "8", "9", "10"]}
        ],
        "O'rta": [
            {"q": "12^2 necha?", "a": "144", "o": ["122", "144", "169", "100"]},
            {"q": "x + 15 = 40; x = ?", "a": "25", "o": ["15", "25", "30", "20"]},
            {"q": "Doira yuzi formulasi?", "a": "πr²", "o": ["2πr", "πr²", "2r", "πd"]}
        ],
        "Qiyin": [
            {"q": "log2(32) = ?", "a": "5", "o": ["4", "5", "6", "3"]},
            {"q": "sin(30°) = ?", "a": "0.5", "o": ["0", "1", "0.5", "0.8"]}
        ]
    },
    "Kimyo": {
        "Oson": [
            {"q": "Suvning formulasi?", "a": "H2O", "o": ["CO2", "H2O", "O2", "H2"]},
            {"q": "Osh tuzi?", "a": "NaCl", "o": ["NaCl", "KCl", "HCl", "NaOH"]}
        ],
        "O'rta": [
            {"q": "Oltinning kimyoviy belgisi?", "a": "Au", "o": ["Ag", "Au", "Fe", "Al"]},
            {"q": "Uglerod nechanchi valentli?", "a": "4", "o": ["2", "3", "4", "1"]}
        ],
        "Qiyin": [
            {"q": "Sulfat kislota formulasi?", "a": "H2SO4", "o": ["H2SO3", "H2SO4", "HCl", "HNO3"]}
        ]
    },
    "Fizika": {
        "Oson": [
            {"q": "Tezlik birligi?", "a": "m/s", "o": ["kg", "m/s", "N", "J"]},
            {"q": "Kuch birligi?", "a": "Nyuton", "o": ["Vatt", "Joul", "Nyuton", "Pa"]}
        ],
        "O'rta": [
            {"q": "Bosim formulasi?", "a": "P=F/S", "o": ["P=m/V", "P=F/S", "P=UI", "P=mg"]}
        ]
    },
    "Tarix": {
        "Oson": [
            {"q": "Amir Temur tug'ilgan yil?", "a": "1336", "o": ["1336", "1342", "1405", "1300"]},
            {"q": "O'zbekiston mustaqilligi?", "a": "1991", "o": ["1990", "1991", "1992", "1989"]}
        ],
        "O'rta": [
            {"q": "Zahiriydin Muhammad Bobur qayerda tug'ilgan?", "a": "Andijon", "o": ["Samarqand", "Andijon", "Farg'ona", "Hirot"]}
        ]
    },
    "Biologiya": {
        "Oson": [
            {"q": "Odamda nechta buyrak bor?", "a": "2", "o": ["1", "2", "3", "4"]},
            {"q": "Fotosintez organi?", "a": "Barg", "o": ["Ildiz", "Barg", "Poya", "Gul"]}
        ]
    }
}

# --- BOT FUNKSIYALARI ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    subjects = list(quiz_data.keys())
    markup.add(*subjects)
    bot.send_message(message.chat.id, "🌟 **TASHMI Quiz Botga xush kelibsiz!**\n\nYo'nalishni tanlang:", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in quiz_data.keys())
def choose_level(message):
    subject = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(f"{subject}: Oson", f"{subject}: O'rta", f"{subject}: Qiyin", "Orqaga")
    bot.send_message(message.chat.id, f"📊 {subject} darajasini tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: ":" in m.text)
def start_quiz(message):
    try:
        subject, level = message.text.split(": ")
        if subject in quiz_data and level in quiz_data[subject]:
            questions = quiz_data[subject][level]
            for item in questions:
                markup = types.InlineKeyboardMarkup()
                options = item['o']
                for opt in options:
                    # Callback_data orqali javobni tekshiramiz
                    is_correct = "✅" if opt == item['a'] else "❌"
                    markup.add(types.InlineKeyboardButton(text=opt, callback_data=f"res_{is_correct}_{opt}"))
                bot.send_message(message.chat.id, f"❓ {item['q']}", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "⚠️ Savollar topilmadi.")
    except:
        bot.send_message(message.chat.id, "⚠️ Xatolik yuz berdi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('res_'))
def handle_answer(call):
    _, result, val = call.data.split('_')
    bot.answer_callback_query(call.id, f"Sizning javobingiz: {val}")
    bot.edit_message_text(chat_id=call.message.chat.id, 
                          message_id=call.message.message_id, 
                          text=f"{call.message.text}\n\n{result} Javob: {val}")

@bot.message_handler(func=lambda m: m.text == "Orqaga")
def back(message):
    start(message)

if __name__ == "__main__":
    bot.remove_webhook()
    bot.infinity_polling()
