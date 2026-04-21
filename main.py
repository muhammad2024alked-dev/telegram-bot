import telebot
from telebot import types
import json
import os
from datetime import datetime
from flask import Flask
from threading import Thread

TOKEN = "8649552323:AAGjBQfQTNZWpbeq4cCE57IXzq6Sv1WVBsM"
ADMIN_ID = 8294457238
CHANNEL_ID = "@moamealked"
CHANNEL_LINK = "https://t.me/moamealked"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'bot_data.json'
user_state = {}

# ======== سيرفر Flask عشان Render ========
app = Flask('')

@app.route('/')
def home():
    return "البوت شغال 100% ✅"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ==========================================

def load_data():
    default_data = {'users': {}, 'tasks': [], 'task_id': 0, 'codes': {}, 'orders': []}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

def get_user(user_id):
    uid = str(user_id)
    if uid not in data['users']:
        if user_id == ADMIN_ID:
            start_points = 999999999
        else:
            start_points = 0
        data['users'][uid] = {
            'points': start_points,
            'completed_tasks': [],
            'my_orders': [],
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'subscribed': False
        }
        save_data(data)
    return data['users'][uid]

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

def send_subscription_message(chat_id):
    text = f"""⚠️ **يجب الاشتراك في القناة أولاً**

اشترك في قناتنا واحصل على **100 كوينز مجاناً** 🎁

بعد الاشتراك اضغط /start مرة تانية"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📢 اشترك في القناة', url=CHANNEL_LINK))
    markup.add(types.InlineKeyboardButton('✅ تحققت من الاشتراك', callback_data='check_sub'))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

def send_main_menu(chat_id, user_id):
    user = get_user(user_id)
    text = f"""مرحبا بيك في بوت محمد القاضي - جميع خدمات الرشق حقيقية وليست وهمية

| الآيدي الخاص بك : `{user_id}` |
| عدد نقاطك : `{user['points']}` نقطة |
"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('🛒 الخدمات', callback_data='services'))
    markup.add(types.InlineKeyboardButton('👤 تمويل قناتك', callback_data='fund_channel'))
    markup.row(types.InlineKeyboardButton('💎 تجميع نقاط', callback_data='collect'),
               types.InlineKeyboardButton('🔄 تحويل نقاط', callback_data='transfer'))
    markup.row(types.InlineKeyboardButton('🎟️ استخدام كود', callback_data='use_code'),
               types.InlineKeyboardButton('💳 الحساب', callback_data='account'))
    markup.row(types.InlineKeyboardButton('🔍 فحص الطلب', callback_data='check'),
               types.InlineKeyboardButton('📅 طلباتي', callback_data='my_orders'))
    markup.row(types.InlineKeyboardButton('💰 شحن نقاط', callback_data='charge'),
               types.InlineKeyboardButton('📊 اكتمال الطلبات', callback_data='completed'))
    markup.row(types.InlineKeyboardButton('🤖 تحديثات البوت', callback_data='updates'),
               types.InlineKeyboardButton('⚠️ شروط الاستخدام', callback_data='terms'))
    markup.add(types.InlineKeyboardButton('⭐ نجوم 🎁 جوائز 🪙 رصيد 1️⃣ ارقام', callback_data='stars'))
    markup.add(types.InlineKeyboardButton('✅ طلبات انجزناها 2601569 طلب', callback_data='stats'))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not check_subscription(user_id) and user_id!= ADMIN_ID:
        send_subscription_message(message.chat.id)
        return

    if not user.get('subscribed', False) and user_id!= ADMIN_ID:
        user['points'] += 100
        user['subscribed'] = True
        save_data(data)
        bot.send_message(message.chat.id, "🎁 **مبروك!**\n\nتم إضافة 100 كوينز لرصيدك لأنك اشتركت في القناة ✅", parse_mode='Markdown')

    send_main_menu(message.chat.id, user_id)

@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    user_id = call.from_user.id
    uid = str(user_id)

    if call.data == 'check_sub':
        if check_subscription(user_id):
            user = get_user(user_id)
            if not user.get('subscribed', False):
                user['points'] += 100
                user['subscribed'] = True
                save_data(data)
                bot.answer_callback_query(call.id, "✅ تم التحقق! مبروك 100 كوينز", show_alert=True)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            send_main_menu(call.message.chat.id, user_id)
        else:
            bot.answer_callback_query(call.id, "❌ انت لسه مشتركتش في القناة", show_alert=True)
        return

    if not check_subscription(user_id) and user_id!= ADMIN_ID:
        bot.answer_callback_query(call.id, "⚠️ لازم تشترك في القناة الأول", show_alert=True)
        return

    if call.data == 'services':
        text = "• أهلاً بك في قسم الخدمات 🟥\n• اختر الخدمة التي تريدها ⬇️"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton('🎁 الخدمات المجانية', callback_data='free_services'))
        markup.row(types.InlineKeyboardButton('تلجرام ✈️', callback_data='cat_telegram'),
                   types.InlineKeyboardButton('انستغرام 📸', callback_data='cat_instagram'))
        markup.row(types.InlineKeyboardButton('تيك توك 🎵', callback_data='cat_tiktok'),
                   types.InlineKeyboardButton('فيس بوك 📘', callback_data='cat_facebook'))
        markup.row(types.InlineKeyboardButton('يوتيوب ▶️', callback_data='cat_youtube'),
                   types.InlineKeyboardButton('تويتر 𝕏', callback_data='cat_twitter'))
        markup.row(types.InlineKeyboardButton('واتساب 💬', callback_data='cat_whatsapp'),
                   types.InlineKeyboardButton('سناب 👻', callback_data='cat_snapchat'))
        markup.row(types.InlineKeyboardButton('ثريدز 🧵', callback_data='cat_threads'),
                   types.InlineKeyboardButton('دعم حقيقي 🧑‍💻', callback_data='cat_support'))
        markup.row(types.InlineKeyboardButton('تفاعلات تلجرام 💖', callback_data='cat_tg_react'),
                   types.InlineKeyboardButton('كيك 🟢', callback_data='cat_kick'))
        markup.row(types.InlineKeyboardButton('تويتش 🟣', callback_data='cat_twitch'),
                   types.InlineKeyboardButton('كواي 🟧', callback_data='cat_kwai'))
        markup.add(types.InlineKeyboardButton('سبوتيفاي 🟢', callback_data='cat_spotify'))
        markup.add(types.InlineKeyboardButton('📢 قسم الإعلانات', callback_data='ads_section'))
        markup.add(types.InlineKeyboardButton('⬅️ رجوع', callback_data='back_main'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'back_main':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_main_menu(call.message.chat.id, user_id)

    else:
        bot.answer_callback_query(call.id, "⚠️ هذه الخدمة قيد التطوير", show_alert=True)

# شغل السيرفر أولاً
keep_alive()
print("البوت شغال...")
bot.infinity_polling()
