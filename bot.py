import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread
from telebot import types

# ========== التوكن ==========
TOKEN = '8655826632:AAFPCTVyCdpquYG1duBlfpAgixtqI_YuTGU'  # 🔴 استبدل هذا بتوكن بوتك

# ========== إعدادات القناة الإجبارية ==========
FORCE_CHANNEL = "@gibranstors"  # قناتك (مع @)
CHANNEL_URL = "https://t.me/gibranstors"

bot = telebot.TeleBot(TOKEN)

# ========== دوال التحقق من الاشتراك ==========
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_force_subscribe(message):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("📢 اشترك في القناة أولاً", url=CHANNEL_URL)
    keyboard.add(button)
    bot.reply_to(message, 
                 f"⚠️ **عذراً، لا يمكنك استخدام البوت قبل الاشتراك في قناتنا!**\n\n"
                 f"🔹 **قناتنا:** {CHANNEL_URL}\n\n"
                 f"✅ اشترك ثم أعد إرسال الأمر.",
                 reply_markup=keyboard, parse_mode="Markdown")

# ========== سيرفر Flask عشان البوت ما ينام ==========
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

# ========== أوامر البوت ==========
@bot.message_handler(commands=['start'])
def start(message):
    # التحقق من الاشتراك أولاً
    if not is_subscribed(message.from_user.id):
        send_force_subscribe(message)
        return
    
    bot.reply_to(message, "🎬 **أهلاً بك!**\n\nأرسل رابط فيديو من يوتيوب أو انستغرام أو تيك توك وسأقوم بتحميله لك.\n\n👑 **المطور:** Gibran\n📢 **قناتنا:** " + CHANNEL_URL)

@bot.message_handler(commands=['help'])
def help_command(message):
    # التحقق من الاشتراك أولاً
    if not is_subscribed(message.from_user.id):
        send_force_subscribe(message)
        return
    
    bot.reply_to(message, "📖 **المساعدة**\n\n1. أرسل رابط الفيديو\n2. انتظر قليلاً\n3. استلم الفيديو\n\nللتبليغ عن مشكلة، تواصل مع المطور.")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    # التحقق من الاشتراك أولاً
    if not is_subscribed(message.from_user.id):
        send_force_subscribe(message)
        return
    
    url = message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        bot.reply_to(message, "❌ أرسل رابطاً صالحاً يبدأ بـ http:// أو https://")
        return
    
    msg = bot.reply_to(message, "⏳ جاري التحميل... يرجى الانتظار")
    
    # إنشاء مجلد التحميلات إذا لم يكن موجوداً
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            with open(file_path, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=f"✅ **تم التحميل بنجاح!**\n\n🎬 {info['title'][:50]}\n\n👑 **المطور:** Gibran\n📢 **قناتنا:** {CHANNEL_URL}")
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ فشل التحميل: {str(e)[:100]}", message.chat.id, msg.message_id)

print("✅ البوت شغال مع نظام الاشتراك الإجباري...")
bot.infinity_polling()
