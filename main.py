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
    default_data = {'users': {}, 'tasks': [], 'task_id': 0, 'codes': {}, 'orders': [], 'order_id': 0}
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

# أسعار الخدمات
PRICES = {
    'tt_follow_real': {'name': 'متابعين تيك توك حقيقيين فوري', 'price': 12},
    'tt_like_vip': {'name': 'اعجابات تيك توك VIP ثابت حقيقي', 'price': 4},
    'tt_view_real': {'name': 'مشاهدات تيك توك حقيقي', 'price': 2},
    'ig_follow_vip': {'name': 'متابعين انستغرام VIP ثابت فوري', 'price': 18},
    'tg_members_life': {'name': 'مشتركين تلجرام مدى الحياة', 'price': 12},
}

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
    markup.add(types.InlineKeyboardButton('🤖 لوحة الأدمن', callback_data='admin_panel'))
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
    user = get_user(user_id)

    if call.data == 'check_sub':
        if check_subscription(user_id):
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
        markup.row(types.InlineKeyboardButton('تلجرام ✈️', callback_data='cat_telegram'),
                   types.InlineKeyboardButton('انستغرام 📸', callback_data='cat_instagram'))
        markup.row(types.InlineKeyboardButton('تيك توك 🎵', callback_data='cat_tiktok'),
                   types.InlineKeyboardButton('فيس بوك 📘', callback_data='cat_facebook'))
        markup.row(types.InlineKeyboardButton('يوتيوب ▶️', callback_data='cat_youtube'),
                   types.InlineKeyboardButton('تويتر 𝕏', callback_data='cat_twitter'))
        markup.add(types.InlineKeyboardButton('⬅️ رجوع', callback_data='back_main'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'cat_tiktok':
        text = "| مرحباً بك في قسم : تيك توك 🟡\n| اختر ما تريد من الخدمات : ⬇️ 🟩"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('🚀 متابعين تيك توك حقيقيين فوري - 12 نقطة', callback_data='order_tt_follow_real'))
        markup.add(types.InlineKeyboardButton('☑️ اعجابات فيديو تيك توك VIP - 4 نقطة', callback_data='order_tt_like_vip'))
        markup.add(types.InlineKeyboardButton('✅ مشاهدات تيك توك حقيقي - 2 نقطة', callback_data='order_tt_view_real'))
        markup.add(types.InlineKeyboardButton('⬅️ رجوع', callback_data='services'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'cat_instagram':
        text = "| مرحباً بك في قسم : انستغرام 🟡\n| اختر ما تريد من الخدمات : ⬇️ 🟩"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('🚀 متابعين انستغرام VIP ثابت فوري - 18 نقطة', callback_data='order_ig_follow_vip'))
        markup.add(types.InlineKeyboardButton('⬅️ رجوع', callback_data='services'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data == 'cat_telegram':
        text = "| مرحباً بك في قسم : تلجرام 🟡\n| اختر ما تريد من الخدمات : ⬇️ 🟩"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton('♻️ مشتركين تلجرام مدى الحياة - 12 نقطة', callback_data='order_tg_members_life'))
        markup.add(types.InlineKeyboardButton('⬅️ رجوع', callback_data='services'))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    # ======== معالجة الطلبات الفعلية ========
    elif call.data.startswith('order_'):
        service_key = call.data.replace('order_', '')
        if service_key in PRICES:
            service = PRICES[service_key]
            if user['points'] < service['price']:
                bot.answer_callback_query(call.id, f"❌ رصيدك غير كافي!\nتحتاج {service['price']} نقطة", show_alert=True)
                return

            user_state[user_id] = {'action': 'waiting_link', 'service': service_key}
            bot.edit_message_text(
                f"📝 **{service['name']}**\n\n"
                f"💰 السعر: `{service['price']}` نقطة\n"
                f"💎 رصيدك الحالي: `{user['points']}` نقطة\n\n"
                f"أرسل **رابط الحساب/المنشور** الآن:",
                call.message.chat.id, call.message.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.answer_callback_query(call.id, "⚠️ هذه الخدمة قيد التطوير", show_alert=True)

    elif call.data == 'back_main':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_main_menu(call.message.chat.id, user_id)

    elif call.data == 'admin_panel':
        if user_id == ADMIN_ID:
            orders_text = f"📊 **لوحة الأدمن**\n\nإجمالي الطلبات: `{len(data['orders'])}`\n\n"
            if data['orders']:
                for order in data['orders'][-5:]:
                    orders_text += f"#{order['id']} - {order['service_name']}\n👤 {order['user_id']}\n🔗 {order['link']}\n📅 {order['date']}\n\n"
            else:
                orders_text += "لا توجد طلبات بعد"
            bot.edit_message_text(orders_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "❌ للأدمن فقط", show_alert=True)

    else:
        bot.answer_callback_query(call.id, "⚠️ هذه الخدمة قيد التطوير", show_alert=True)

@bot.message_handler(func=lambda message: user_state.get(message.from_user.id, {}).get('action') == 'waiting_link')
def process_link(message):
    user_id = message.from_user.id
    uid = str(user_id)
    user = get_user(user_id)
    state = user_state[user_id]
    service_key = state['service']
    service = PRICES[service_key]

    if user['points'] < service['price']:
        bot.send_message(message.chat.id, "❌ رصيدك غير كافي!")
        user_state.pop(user_id)
        send_main_menu(message.chat.id, user_id)
        return

    # خصم النقاط
    user['points'] -= service['price']

    # تسجيل الطلب
    data['order_id'] += 1
    order = {
        'id': data['order_id'],
        'user_id': user_id,
        'username': message.from_user.username or 'بدون يوزر',
        'service': service_key,
        'service_name': service['name'],
        'link': message.text,
        'price': service['price'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'status': 'قيد التنفيذ'
    }
    data['orders'].append(order)
    user['my_orders'].append(order['id'])
    save_data(data)

    # رسالة للمستخدم
    bot.send_message(
        message.chat.id,
        f"✅ **تم استلام طلبك بنجاح**\n\n"
        f"🆔 رقم الطلب: `#{order['id']}`\n"
        f"📦 الخدمة: {service['name']}\n"
        f"🔗 الرابط: {message.text}\n"
        f"💰 المبلغ المخصوم: `{service['price']}` نقطة\n"
        f"💎 رصيدك المتبقي: `{user['points']}` نقطة\n\n"
        f"⏳ جاري التنفيذ خلال 24 ساعة",
        parse_mode='Markdown'
    )

    # إشعار للأدمن
    bot.send_message(
        ADMIN_ID,
        f"🔔 **طلب جديد**\n\n"
        f"🆔 رقم الطلب: `#{order['id']}`\n"
        f"👤 المستخدم: `{user_id}`\n"
        f"📦 الخدمة: {service['name']}\n"
        f"🔗 الرابط: {message.text}\n"
        f"💰 السعر: `{service['price']}` نقطة",
        parse_mode='Markdown'
    )

    user_state.pop(user_id)
    send_main_menu(message.chat.id, user_id)

keep_alive()
print("البوت شغال...")
bot.infinity_polling()
