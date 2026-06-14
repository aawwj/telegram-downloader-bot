import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

TOKEN = '8655826632:AAFPCTVyCdpquYG1duBlfpAgixtqI_YuTGU'

# ========== خادم Flask ==========
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "✅ بوت التحميل شغال!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

keep_alive()
# ========== نهاية Flask ==========

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 أرسل رابط فيديو")

@bot.message_handler(func=lambda m: True)
def download(message):
    url = message.text.strip()
    if not url.startswith('http'):
        bot.reply_to(message, "❌ رابط صحيح")
        return
    
    msg = bot.reply_to(message, "⏳ جاري التحميل...")
    
    ydl_opts = {'outtmpl': 'video.%(ext)s', 'format': 'best', 'quiet': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            with open('video.mp4', 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"✅ {info['title'][:40]}")
            os.remove('video.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ فشل", message.chat.id, msg.message_id)

print("✅ البوت شغال مع Flask...")
bot.infinity_polling()
