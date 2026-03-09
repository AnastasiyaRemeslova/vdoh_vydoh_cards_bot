import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, JobQueue
from datetime import time

TOKEN = os.getenv("TOKEN")
CARDS_DIR = "cards"
USERS_FILE = "users.txt"  # файл для хранения chat_id

def get_card_markup():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Получить карточку", callback_data="get_card")]]
    )

# Сохраняем chat_id пользователя
def add_user(chat_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("")
    with open(USERS_FILE, "r") as f:
        users = set(line.strip() for line in f)
    if str(chat_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{chat_id}\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_user(chat_id)
    await update.message.reply_text(
        "Нажмите кнопку, чтобы получить карточку",
        reply_markup=get_card_markup()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    add_user(chat_id)

    if query.data == "get_card":
        cards = os.listdir(CARDS_DIR)
        if not cards:
            await query.message.reply_text("Карточки не найдены!")
            return
        card = random.choice(cards)
        with open(os.path.join(CARDS_DIR, card), "rb") as img:
            await query.message.reply_photo(img)
        await query.message.reply_text(
            "Нажмите кнопку, чтобы получить следующую карточку",
            reply_markup=get_card_markup()
        )

# Рассылка всем пользователям
async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(USERS_FILE):
        return
    with open(USERS_FILE, "r") as f:
        users = [line.strip() for line in f if line.strip()]
    for chat_id in users:
        try:
            await context.bot.send_message(
                chat_id=int(chat_id),
                text="Новая карточка доступна! Нажмите кнопку, чтобы получить её.",
                reply_markup=get_card_markup()
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение {chat_id}: {e}")

# Создаём приложение
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

# JobQueue на 10 утра
job_queue = app.job_queue
job_queue.run_daily(daily_reminder, time(hour=10, minute=0))

# Запуск
app.run_polling()