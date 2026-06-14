import telebot
import yt_dlp
import os
from telebot import types

TOKEN = '8655826632:AAFPCTVyCdpquYG1duBlfpAgixtqI_YuTGU'
CHANNEL_URL = 'https://t.me/gibranstors'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 قناتنا", url=CHANNEL_URL))
    bot.reply_to(message, 
        f"🎬 **بوت تحميل الفيديوهات**\n\n"
        f"أرسل رابط فيديو من يوتيوب أو انستغرام لتحميله\n\n"
        f"👑 **المطور:** Gibran\n"
        f"📢 **قناتنا:** {CHANNEL_URL}",
        reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def download(message):
    url = message.text.strip()
    if not url.startswith('http'):
        bot.reply_to(message, "❌ أرسل رابط صحيح")
        return
    msg = bot.reply_to(message, "⏳ جاري التحميل...")
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    ydl_opts = {'outtmpl': 'downloads/%(title)s.%(ext)s', 'format': 'best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"✅ تم التحميل: {info['title'][:50]}\n\n👑 المطور: Gibran\n📢 قناتنا: {CHANNEL_URL}")
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ فشل التحميل", message.chat.id, msg.message_id)

print("✅ البوت شغال...")
bot.infinity_polling()
