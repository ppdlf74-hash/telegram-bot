import telebot
from telebot import types
import json
import os
import threading
import time
import re

TOKEN = "8623317435:AAGY6NdHBjwJD7GSaWGQSENe6q2f6-P3Hwk"
ADMIN_ID = 7719104236
ADMIN_USERNAME = "VIlianov_Varik"

WEBAPP_URL = "https://tiny-tanuki-47a560.netlify.app"

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# -----------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(users, f, indent=4)
    except:
        pass

users = load_data()

# -----------------------
def get_user(uid):
    uid = str(uid)

    if uid not in users:
        users[uid] = {
            "allowed": False,
            "ai_access": False,
            "balance": 0,
            "refs": [],
            "ref_by": None,
            "casino": None,
            "email": None,
            "status": "none",
            "casino_count": 0
        }

    return users[uid]

# -----------------------
def check_access(uid):
    return get_user(uid)["allowed"]

# -----------------------
def main_menu(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 ВІДКРИТИ AI")
    markup.add("🏆 ПІДКЛЮЧИТИ КАЗИНО")
    markup.add("👥 РЕФЕРАЛКА")
    markup.add("❓ FAQ")

    if uid == ADMIN_ID:
        markup.add("⚙️ АДМІНКА")

    return markup

# -----------------------
def admin_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ ДОДАТИ ЮЗЕРА")
    markup.add("🚀 ВИДАТИ AI")
    markup.add("💰 БОНУС")
    markup.add("📩 РОЗСИЛКА")
    markup.add("🔙 НАЗАД")
    return markup

# -----------------------
pending = {}
admin_state = {}

# -----------------------
def is_email(text):
    return re.match(r"[^@]+@[^@]+\.[^@]+", text)

# -----------------------
def reminder(uid):
    while True:
        time.sleep(900)

        user = get_user(uid)

        if user.get("status") == "done":
            break

        try:
            bot.send_message(uid, "⏳ AI ще створює акаунт, зачекайте...")
        except:
            break

# -----------------------
casinos = ["🦍 Gorilla","🎯 GG Bet","🔥 Top Match","🎰 Parik 24","💣 Beton","⚡ First"]

casino_images = {
    "🦍 Gorilla": "images/gorilla.jpg",
    "🎯 GG Bet": "images/ggbet.jpg",
    "🔥 Top Match": "images/topmatch.jpg",
    "🎰 Parik 24": "images/parik.jpg",
    "💣 Beton": "images/beton.jpg",
    "⚡ First": "images/first.jpg"
}

casino_links = {
    "🦍 Gorilla": "https://gorilla.ua",
    "🎯 GG Bet": "https://ggbet.ua",
    "🔥 Top Match": "https://topmatch1.online",
    "🎰 Parik 24": "https://parik-24.one",
    "💣 Beton": "https://beton.ua",
    "⚡ First": "https://first.ua"
}

# -----------------------
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.chat.id
    user = get_user(uid)

    parts = message.text.split()
    if len(parts) > 1:
        ref = parts[1]
        if ref != str(uid):
            user["ref_by"] = ref
            if ref in users:
                users[ref]["refs"].append(str(uid))

    save_data()

    if not check_access(uid):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "✉️ НАПИСАТИ АДМІНУ",
            url=f"https://t.me/{ADMIN_USERNAME}"
        ))

        bot.send_message(uid,
            f"❌ Доступ закритий\nНапиши адміну: @{ADMIN_USERNAME}",
            reply_markup=markup
        )
        return

    bot.send_message(uid, "🔥 Доступ дозволено", reply_markup=main_menu(uid))

# -----------------------
@bot.message_handler(commands=['give'])
def give_access(message):
    if message.chat.id != ADMIN_ID:
        return

    try:
        _, uid, password = message.text.split()
        user = get_user(uid)

        if not user.get("casino"):
            bot.send_message(message.chat.id, "❌ У юзера не вибрано казино")
            return

        link = casino_links.get(user.get("casino"), "https://google.com")

        bot.send_message(uid,
f"""✅ КАЗИНО ПІДКЛЮЧЕНО

🌐 Посилання на казино:
{link}

📩 Email: {user['email']}
🔐 Пароль: {password}

👉 Увійдіть в казино та пройдіть верифікацію
(пароль можна змінити, бот не має доступу до ваших даних)

💰 Після цього внесіть депозит
та відкриється доступ до AI 🚀
""")

        if int(uid) in pending:
            del pending[int(uid)]

        user["status"] = "done"
        save_data()

        bot.send_message(message.chat.id, "✅ Надіслано")

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Помилка: {e}")

# -----------------------
@bot.message_handler(func=lambda m: m.text == "⚙️ АДМІНКА")
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "⚙️ Адмінка", reply_markup=admin_menu())

# -----------------------
@bot.message_handler(func=lambda m: m.text == "➕ ДОДАТИ ЮЗЕРА")
def add_user(message):
    admin_state[message.chat.id] = "add"
    bot.send_message(message.chat.id, "Введи ID:")

# -----------------------
@bot.message_handler(func=lambda m: m.text == "🚀 ВИДАТИ AI")
def give_ai(message):
    admin_state[message.chat.id] = "ai"
    bot.send_message(message.chat.id, "Введи ID:")

# -----------------------
@bot.message_handler(func=lambda m: m.text == "💰 БОНУС")
def bonus(message):
    admin_state[message.chat.id] = "bonus"
    bot.send_message(message.chat.id, "Введи: ID СУМА")

# -----------------------
@bot.message_handler(func=lambda m: m.text == "📩 РОЗСИЛКА")
def mail(message):
    admin_state[message.chat.id] = "mail"
    bot.send_message(message.chat.id, "Введи текст:")

# -----------------------
@bot.message_handler(func=lambda m: m.chat.id in admin_state)
def admin_logic(message):
    state = admin_state[message.chat.id]

    if state == "add":
        uid = message.text
        get_user(uid)["allowed"] = True
        save_data()
        bot.send_message(message.chat.id, "✅ Додано")

    elif state == "ai":
        uid = message.text
        get_user(uid)["ai_access"] = True
        save_data()
        bot.send_message(uid, "🚀 AI відкрито")
        bot.send_message(message.chat.id, "✅ OK")

    elif state == "bonus":
        try:
            uid, amount = message.text.split()
            amount = int(amount)
        except:
            bot.send_message(message.chat.id, "❌ Формат: ID СУМА")
            return

        get_user(uid)["balance"] += amount
        save_data()
        bot.send_message(uid, f"💰 +{amount}")
        bot.send_message(message.chat.id, "✅ OK")

    elif state == "mail":
        for uid in users:
            try:
                bot.send_message(uid, message.text)
            except:
                pass
        bot.send_message(message.chat.id, "✅ DONE")

    del admin_state[message.chat.id]

# -----------------------
@bot.message_handler(func=lambda m: m.text == "🏆 ПІДКЛЮЧИТИ КАЗИНО")
def casino_menu(message):
    if not check_access(message.chat.id):
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for c in casinos:
        markup.add(c)
    markup.add("🔙 НАЗАД")

    bot.send_message(message.chat.id, "Оберіть казино:", reply_markup=markup)

# -----------------------
@bot.message_handler(func=lambda m: m.text in casinos)
def select_casino(message):
    uid = message.chat.id

    if not check_access(uid):
        return

    if uid in pending:
        bot.send_message(uid, "⏳ Ви вже подали заявку")
        return

    pending[uid] = message.text

    img = casino_images.get(message.text)

    try:
        bot.send_photo(uid, open(img, "rb"), caption="📩 Введіть email:")
    except:
        bot.send_message(uid, "📩 Введіть email:")

# -----------------------
@bot.message_handler(func=lambda m: m.chat.id in pending and is_email(m.text))
def get_email(message):
    uid = message.chat.id
    user = get_user(uid)

    user["casino"] = pending[uid]
    user["email"] = message.text
    user["status"] = "pending"
    user["casino_count"] += 1

    save_data()

    bot.send_message(ADMIN_ID,
        f"🆕 ЗАЯВКА\nID: {uid}\nCasino: {user['casino']}\nEmail: {user['email']}\n\n👉 /give {uid} PASSWORD"
    )

    bot.send_message(uid,
    "🤖 AI створює для вас акаунт...\n\n⏳ Зачекайте, це може зайняти кілька хвилин")

    threading.Thread(target=reminder, args=(uid,), daemon=True).start()

# -----------------------
@bot.message_handler(func=lambda m: m.chat.id in pending)
def wrong_email(message):
    bot.send_message(message.chat.id, "❌ Введіть коректний email")

# -----------------------
@bot.message_handler(func=lambda m: m.text == "👥 РЕФЕРАЛКА")
def ref(message):
    if not check_access(message.chat.id):
        return

    user = get_user(message.chat.id)
    link = f"https://t.me/{bot.get_me().username}?start={message.chat.id}"

    bot.send_message(message.chat.id,
f"""🔗 {link}

👥 Запрошено: {len(user['refs'])}
💰 Баланс: {user['balance']}

💸 Для виводу коштів потрібно:
- або 5 рефералів
- або щоб ваш реферал зробив 5 підключень казино
"""
    )

# -----------------------
@bot.message_handler(func=lambda m: m.text == "🚀 ВІДКРИТИ AI")
def ai(message):
    uid = message.chat.id

    if not check_access(uid):
        return

    if not get_user(uid)["ai_access"]:
        bot.send_message(uid, "❌ Немає AI доступу")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "🚀 OPEN AI",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    ))

    bot.send_message(uid, "AI запускається:", reply_markup=markup)

# -----------------------
@bot.message_handler(func=lambda m: m.text == "❓ FAQ")
def faq(message):
    bot.send_message(message.chat.id, """🔹 Що таке AIbetGenius Bot?

AIbetGenius Bot — це інтелектуальний бот, який аналізує слот-ігри та надає рекомендації для більш обдуманої гри.

---

🔹 Що вміє бот?

- 📊 Аналізує поведінку слотів
- 🧠 Підбирає алгоритми гри на основі даних
- 📈 Дає рекомендації щодо стратегії
- 🔐 Працює з вашим акаунтом для персоналізації

---

 🔹 Як почати користуватись?

1. Натисніть /start
2. Оберіть потрібну функцію в меню
3. За потреби підключіть акаунт

---

 🔹 Чи можна підключити акаунт казино?

Так, бот дозволяє підключити ваш акаунт для більш точного аналізу та персональних рекомендацій.

---

🔹 Чи безпечні мої дані?

Так:

- Ваші персональні дані не передаються третім особам
- Фінансова інформація захищена
- Бот використовує тільки необхідні дані вашого акаунта

---

🔹 Чи гарантує бот виграш?

Ні. AIbetGenius Bot надає аналітику та рекомендації, але не гарантує виграш.

---

🔹 Для кого цей бот?

Для користувачів, які хочуть використовувати аналітику та сучасні інструменти AI для прийняття рішень у грі.
""")

# -----------------------
@bot.message_handler(func=lambda m: m.text == "🔙 НАЗАД")
def back(message):
    bot.send_message(message.chat.id, "Меню", reply_markup=main_menu(message.chat.id))

# -----------------------
bot.polling(none_stop=True)
