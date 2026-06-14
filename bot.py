import telebot
import yt_dlp
import os
import subprocess
import sys
from telebot import types

TOKEN = '8655826632:AAFPCTVyCdpquYG1duBlfpAgixtqI_YuTGU'
CHANNEL_URL = 'https://t.me/gibranstors'

bot = telebot.TeleBot(TOKEN)

# ========== الدوال المتقدمة ==========
def update_yt_dlp():
    """تحديث yt-dlp إلى أحدث إصدار"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
        return True
    except:
        return False

def check_ffmpeg():
    """التحقق من وجود FFmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except:
        return False

def get_cookies():
    """محاولة استخراج الكوكيز من متصفح المستخدم (إذا كان متاحاً)"""
    # هذه محاولة لاستخراج الكوكيز تلقائياً من Chrome/Firefox
    # قد لا تعمل في بيئة السيرفر، لذا نضبطها اختيارياً
    browsers = ['chrome', 'firefox', 'edge', 'brave', 'opera']
    for browser in browsers:
        try:
            result = subprocess.run(['yt-dlp', '--cookies-from-browser', browser, '--cookies', 'cookies.txt'], 
                                  capture_output=True, text=True)
            if os.path.exists('cookies.txt'):
                return 'cookies.txt'
        except:
            continue
    return None

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_quality = types.InlineKeyboardButton("🎚️ الجودة", callback_data="quality")
    btn_update = types.InlineKeyboardButton("🔄 تحديث", callback_data="update")
    btn_info = types.InlineKeyboardButton("ℹ️ معلومات", callback_data="info")
    btn_channel = types.InlineKeyboardButton("📢 قناتنا", url=CHANNEL_URL)
    markup.add(btn_quality, btn_update, btn_info, btn_channel)
    
    bot.reply_to(message, 
        f"🎬 **بوت التحميل الاحترافي**\n\n"
        f"📌 أرسل رابط فيديو من أي موقع\n"
        f"⚡ يدعم: YouTube, TikTok, Instagram, Twitter, Facebook, Vimeo, SoundCloud\n"
        f"🎵 يدعم تحميل الصوت MP3\n"
        f"📁 يدحم تحميل القوائم (Playlists)\n\n"
        f"👑 **المطور:** Gibran\n"
        f"📢 **قناتنا:** {CHANNEL_URL}",
        reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📖 **كيفية الاستخدام**\n\n"
        "1️⃣ أرسل رابط الفيديو\n"
        "2️⃣ اختر الجودة المطلوبة من الأزرار\n"
        "3️⃣ انتظر قليلاً\n\n"
        "🎚️ **الأزرار المتاحة:**\n"
        "• /start - القائمة الرئيسية\n"
        "• /audio - تحميل صوت MP3\n"
        "• /update - تحديث yt-dlp\n\n"
        "🌐 **المواقع المدعومة:**\n"
        "YouTube • TikTok • Instagram • Twitter • Facebook • Vimeo • SoundCloud\n"
        "و 1800+ موقع آخر"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['audio'])
def audio_mode(message):
    bot.reply_to(message, "🎵 **وضع الصوت MP3**\nأرسل رابط الفيديو لاستخراج الصوت منه")

@bot.message_handler(commands=['update'])
def update_command(message):
    msg = bot.reply_to(message, "⏳ جاري تحديث yt-dlp...")
    if update_yt_dlp():
        bot.edit_message_text("✅ تم تحديث yt-dlp إلى أحدث إصدار", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ فشل التحديث، تأكد من اتصال الإنترنت", message.chat.id, msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('quality_'))
def set_quality(call):
    quality = call.data.split('_')[1]
    user_data[call.from_user.id] = {'quality': quality}
    bot.answer_callback_query(call.id, f"✅ تم ضبط الجودة: {quality}")

@bot.message_handler(func=lambda m: True)
def download(message):
    url = message.text.strip()
    
    if not url.startswith('http'):
        bot.reply_to(message, "❌ أرسل رابط صحيح يبدأ بـ http://")
        return
    
    # التحقق من وضع الصوت
    is_audio = message.text.startswith('/audio') or message.text.lower() == 'audio'
    if is_audio:
        url = message.text.split()[1] if len(message.text.split()) > 1 else message.text
    
    msg = bot.reply_to(message, "⏳ جاري التحضير للتحميل...")
    
    # تحديث yt-dlp قبل كل تحميل (اختياري)
    update_yt_dlp()
    
    # إعدادات التحميل المتقدمة
    quality = user_data.get(message.from_user.id, {}).get('quality', 'best')
    
    if quality == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    else:
        ydl_opts = {
            'format': quality,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    # محاولة استخدام الكوكيز إذا كانت متاحة
    cookies_file = get_cookies()
    if cookies_file:
        ydl_opts['cookiefile'] = cookies_file
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    try:
        bot.edit_message_text("⏳ جاري التحميل... قد يستغرق وقتاً", message.chat.id, msg.message_id)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # تعديل المسار لملفات MP3
            if quality == 'audio':
                file_path = file_path.replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            file_size = os.path.getsize(file_path) / (1024 * 1024)
            
            with open(file_path, 'rb') as f:
                if quality == 'audio':
                    bot.send_audio(message.chat.id, f, 
                        caption=f"✅ **تم التحميل**\n🎵 {info['title'][:50]}\n💾 {file_size:.1f} ميجا\n\n👑 المطور: Gibran\n📢 قناتنا: {CHANNEL_URL}")
                else:
                    bot.send_video(message.chat.id, f, 
                        caption=f"✅ **تم التحميل**\n🎬 {info['title'][:50]}\n💾 {file_size:.1f} ميجا\n🎚️ الجودة: {quality}\n\n👑 المطور: Gibran\n📢 قناتنا: {CHANNEL_URL}")
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
            
    except Exception as e:
        error_msg = str(e)[:200]
        bot.edit_message_text(
            f"❌ **فشل التحميل**\n\n"
            f"**السبب المحتمل:**\n"
            f"• الموقع يطلب التحقق (CAPTCHA) - قد تحتاج لتسجيل الدخول\n"
            f"• الرابط غير صالح أو الفيديو محذوف\n"
            f"• الموقع غير مدعوم حالياً\n\n"
            f"**الحلول:**\n"
            f"1️⃣ أعد المحاولة لاحقاً\n"
            f"2️⃣ استخدم رابطاً من مصدر مختلف\n"
            f"3️⃣ أرسل /update لتحديث الأداة\n\n"
            f"**الخطأ:** {error_msg}",
            message.chat.id, msg.message_id, parse_mode="Markdown"
        )
        print(f"Error: {error_msg}")

# قاموس لتخزين إعدادات المستخدم
user_data = {}

print("✅ البوت الاحترافي شغال...")
print(f"📊 FFmpeg موجود: {check_ffmpeg()}")
bot.infinity_polling()
