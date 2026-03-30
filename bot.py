import telebot
from googletrans import Translator

# 1. Botingiz ma'lumotlari
TOKEN = '8322130528:AAGgtExfH17TbsCfGxL2Rdrg6o_5wOXNRFg'
bot = telebot.TeleBot(TOKEN)
translator = Translator()

print("Bot ishga tushdi...")

# 2. Tarjima funksiyasi (Universal)
def get_translation(text):
    try:
        # Tilni aniqlaymiz
        detection = translator.detect(text)
        src_lang = detection.lang
        
        # Agar ingliz yoki rus tili bo'lsa, o'zbekchaga o'giramiz
        if src_lang in ['ru', 'en']:
            dest_lang = 'uz'
        # Agar o'zbekcha bo'lsa, ruscha yoki inglizchaga (ixtiyoriy, bu yerda ruscha)
        else:
            dest_lang = 'ru'
            
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception as e:
        return f"Xatolik yuz berdi: {e}"

# 3. Matn, Rasm va Video uchun yagona handler
@bot.message_handler(content_types=['text', 'photo', 'video'])
def handle_all_messages(message):
    # Matnni aniqlash (oddiy matn yoki media izohi)
    text_to_translate = ""
    
    if message.content_type == 'text':
        text_to_translate = message.text
    elif message.content_type in ['photo', 'video']:
        text_to_translate = message.caption

    # Agar tarjima qilish uchun matn bo'lsa
    if text_to_translate:
        translated_text = get_translation(text_to_translate)
        
        # Javobni chiroyli ko'rinishda qaytarish
        response = f"📝 **Tarjima:**\n\n{translated_text}"
        bot.reply_to(message, response, parse_mode="Markdown")
    else:
        # Agar rasm yoki videoda yozuv bo'lmasa
        if message.content_type != 'text':
            bot.reply_to(message, "Bu medianing izohi yo'q, tarjima qila olmayman. 🧐")

# 4. Botni to'xtovsiz ishlatish
if __name__ == "__main__":
    bot.infinity_polling()
