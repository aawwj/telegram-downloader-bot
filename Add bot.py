import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# التوكن من Render Environment Variables
TOKEN = os.environ.get('BOT_TOKEN', '')
if not TOKEN:
    print("❌ التوكن غير موجود!")
    exit()

bot = telebot.TeleBot(TOKEN)

# Flask server for keep-alive
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

# أوامر البوت
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎥 أرسل رابط فيديو من يوتيوب أو انستغرام لتحميله")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text.strip()
    if not url.startswith('http'):
        bot.reply_to(message, "❌ أرسل رابط صحيح")
        return
    
    bot.reply_to(message, "⏳ جاري التحميل...")
    
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            with open(file_path, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"✅ تم التحميل: {info['title'][:50]}")
            
            os.remove(file_path)
    except Exception as e:
        bot.reply_to(message, f"❌ فشل التحميل: {str(e)[:100]}")

print("✅ البوت شغال...")
bot.infinity_polling()
