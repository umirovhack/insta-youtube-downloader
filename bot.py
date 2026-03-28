import telebot
import google.generativeai as genai
import os
import PIL.Image
import yt_dlp
from telebot import types

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = '8322130528:AAEerleOyHrAQIdx7B16pV3BBZqN6fTZdf8'
GEMINI_API_KEY = 'AIzaSyDih1CxOtnxqYOSM2CuBUVjYs_eYhWzRuI'

# Bot va AI'ni sozlash
bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_data = {}

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        f"🌟 **Assalomu alaykum, {message.from_user.first_name}!**\n\n"
        "Men **@um1rov77** tomonidan yaratilgan aqlli botman! ✨\n\n"
        "✨ **Imkoniyatlarim:**\n"
        "🤖 **AI Savol-javob:** Xohlagan savolingizni yozing.\n"
        "🖼 **Rasm tahlili:** Rasm yuboring, uni tushuntirib beraman.\n"
        "🎵 **Musiqa qidirish:** Musiqa nomini yozing (10 variant).\n"
        "📸 **Instagram:** Link yuboring, video/MP3 yuklayman."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

# --- MUSIQA VA VIDEO YUKLASH FUNKSIYASI ---
def download_and_send(chat_id, url, status_id, is_video=True):
    try:
        ext = 'mp4' if is_video else 'mp3'
        filename = f"file_{chat_id}.{ext}"
        ydl_opts = {
            'format': 'best[ext=mp4]/best' if is_video else 'bestaudio/best',
            'outtmpl': filename, 'quiet': True, 'nocheckcertificate': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                cap = "✨ @um1rov77"
                if is_video: bot.send_video(chat_id, f, caption=cap)
                else: bot.send_audio(chat_id, f, caption=cap)
            os.remove(filename)
        bot.delete_message(chat_id, status_id)
    except:
        bot.send_message(chat_id, "❌ Yuklashda xatolik yuz berdi.")

# --- ASOSIY XABARLARNI QAYTA ISHLASH ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all(message):
    chat_id = message.chat.id

    # 1. AGAR RASM YUBORILSA (AI TAHLIL)
    if message.content_type == 'photo':
        status = bot.send_message(chat_id, "🧐 _Rasmni tahlil qilyapman..._", parse_mode="Markdown")
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded = bot.download_file(file_info.file_path)
            temp_path = f"img_{chat_id}.jpg"
            with open(temp_path, "wb") as f: f.write(downloaded)
            
            img = PIL.Image.open(temp_path)
            prompt = message.caption if message.caption else "Bu rasmda nima borligini tushuntir."
            response = model.generate_content([prompt, img])
            
            bot.edit_message_text(response.text, chat_id, status.message_id)
            os.remove(temp_path)
        except: bot.edit_message_text("❌ Rasm tahlilida xato.", chat_id, status.message_id)

    # 2. AGAR INSTAGRAM LINKI BO'LSA
    elif "instagram.com" in message.text:
        user_data[chat_id] = message.text
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎬 Video", callback_data="vid"),
                   types.InlineKeyboardButton("🎵 MP3", callback_data="aud"))
        bot.send_message(chat_id, "🎥 Instagram aniqlandi. Tanlang:", reply_markup=markup)

    # 3. AGAR SAVOL BO'LSA YOKI MUSIQA QIDIRILSA
    else:
        text = message.text
        # Agar savol oxirida '?' bo'lsa yoki matn uzun bo'lsa - AI javob beradi
        if len(text) > 15 or text.endswith('?'):
            status = bot.send_message(chat_id, "🤖 _AI o'ylamoqda..._", parse_mode="Markdown")
            try:
                response = model.generate_content(text)
                bot.edit_message_text(response.text, chat_id, status.message_id)
            except: bot.edit_message_text("❌ AI hozir javob bera olmaydi.", chat_id, status.message_id)
        
        # Musiqa qidiruvi (har doim matn yozilganda variantlar chiqaradi)
        else:
            status = bot.send_message(chat_id, f"🔍 **'{text}'** qidirilmoqda...", parse_mode="Markdown")
            try:
                ydl_opts = {'quiet': True, 'default_search': 'scsearch10', 'nocheckcertificate': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"scsearch10:{text}", download=False)
                    results = info['entries']
                    user_data[chat_id] = results
                    res_text = f"🎵 **'{text}' natijalari:**\n\n"
                    markup = types.InlineKeyboardMarkup()
                    btns = []
                    for i, entry in enumerate(results, 1):
                        res_text += f"{i}. {entry.get('title', '...')[:40]}\n"
                        btns.append(types.InlineKeyboardButton(str(i), callback_data=f"m_{i}"))
                    markup.row(*btns[:5])
                    if len(btns) > 5: markup.row(*btns[5:])
                    bot.edit_message_text(res_text, chat_id, status.message_id, reply_markup=markup, parse_mode="Markdown")
            except: bot.edit_message_text("❌ Topilmadi.", chat_id, status.message_id)

# --- CALLBACK (TUGMALAR) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    if call.data == "vid" or call.data == "aud":
        url = user_data.get(chat_id)
        is_v = True if call.data == "vid" else False
        bot.delete_message(chat_id, call.message.message_id)
        st = bot.send_message(chat_id, "⏳ Yuklanmoqda...")
        download_and_send(chat_id, url, st.message_id, is_video=is_v)
    elif call.data.startswith("m_"):
        res = user_data.get(chat_id)
        idx = int(call.data.split('_')[1])
        url = res[idx].get('url') or res[idx].get('webpage_url')
        bot.delete_message(chat_id, call.message.message_id)
        st = bot.send_message(chat_id, "⏳ Yuklanmoqda...")
        download_and_send(chat_id, url, st.message_id, is_video=False)

if __name__ == "__main__":
    bot.infinity_polling()
