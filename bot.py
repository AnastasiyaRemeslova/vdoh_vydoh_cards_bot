import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = os.getenv("TOKEN")
CARDS_DIR = "cards"
USERS_FILE = "users.txt"

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

# Команда /start
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    add_user(chat_id)
    update.message.reply_text(
        "Нажмите кнопку, чтобы получить карточку",
        reply_markup=get_card_markup()
    )

# Обработка кнопки
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat.id
    add_user(chat_id)

    if query.data == "get_card":
        cards = os.listdir(CARDS_DIR)
        if not cards:
            query.message.reply_text("Карточки не найдены!")
            return
        card = random.choice(cards)
        with open(os.path.join(CARDS_DIR, card), "rb") as img:
            query.message.reply_photo(img)
        query.message.reply_text(
            "Нажмите кнопку, чтобы получить следующую карточку",
            reply_markup=get_card_markup()
        )

# Рассылка всем пользователям (JobQueue в PTB 13)
def daily_reminder(context: CallbackContext):
    if not os.path.exists(USERS_FILE):
        return
    with open(USERS_FILE, "r") as f:
        users = [line.strip() for line in f if line.strip()]
    for chat_id in users:
        try:
            context.bot.send_message(
                chat_id=int(chat_id),
                text="Новая карточка доступна! Нажмите кнопку, чтобы получить её.",
                reply_markup=get_card_markup()
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение {chat_id}: {e}")

# Создаём Updater
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

# Обработчики
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(button_handler))

# Настройка ежедневного напоминания через JobQueue
job_queue = updater.job_queue
job_queue.run_daily(daily_reminder, time(hour=10, minute=0))

# Запуск бота
updater.start_polling()
updater.idle()