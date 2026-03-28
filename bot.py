import telebot
import math

# --- SOZLAMALAR ---
# O'zingizning tokeningizni kiriting
TOKEN = '8322130528:AAGMPhK9p1sT5kSJMntqOXwZFt2UcjPx4Nk'
bot = telebot.TeleBot(TOKEN)

# --- KALKULYATOR LOGIKASI ---
def solve_math(expression):
    try:
        # Xavfsizlik uchun faqat matematik belgilarga ruxsat beramiz
        # 'math.' funksiyalarini ishlatishga ruxsat (sin, cos, sqrt va hokazo)
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        
        # '^' belgisini Python tushunadigan '**' ga almashtiramiz
        expression = expression.replace('^', '**').replace(':', '/')
        
        # Hisoblash
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return result
    except Exception as e:
        return None

# --- BUYRUQLAR ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        "🧮 **Aqlli Kalkulyator Botiga xush kelibsiz!**\n\n"
        "Menga matematik misol yuboring, men uni hisoblab beraman.\n\n"
        "**Misollar:**\n"
        "• `15 + 25 * 4`\n"
        "• `(100 - 20) / 5`\n"
        "• `sqrt(144)` (Ildiz chiqarish)\n"
        "• `2^10` (Darajaga ko'tarish)\n"
        "• `sin(30)` (Trigonometriya)"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# --- XABARLARNI QAYTA ISHLASH ---
@bot.message_handler(func=lambda message: True)
def do_math(message):
    expression = message.text
    result = solve_math(expression)
    
    if result is not None:
        bot.reply_to(message, f"🔢 **Natija:** `{result}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ **Xatolik!** Iltimos, misolni to'g'ri formatda yozing.\nMasalan: `2 + 2` yoki `sqrt(25)`")

if __name__ == "__main__":
    print("Kalkulyator ishga tushdi...")
    bot.remove_webhook()
    bot.infinity_polling()
