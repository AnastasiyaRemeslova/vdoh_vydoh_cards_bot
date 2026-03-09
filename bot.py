import os
import random
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = "8687686811:AAFodDPyMBlYGBChIimWkZvrvnf6YEJYx38"
CARDS_FOLDER = "cards"

# Список пользователей, которые начали бота
users = set()

# --- Функция отправки сообщения с кнопкой ---
async def send_invite_message(chat_id, bot):
    keyboard = [[InlineKeyboardButton("Получить карточку", callback_data="draw_card")]]
    markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(
        chat_id=chat_id,
        text="Нажмите кнопку, чтобы получить карточку",
        reply_markup=markup
    )

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    users.add(chat_id)  # сохраняем ID пользователя
    await send_invite_message(chat_id, context.bot)

# --- Обработчик кнопки ---
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Случайная карта
    cards = os.listdir(CARDS_FOLDER)
    card = random.choice(cards)

    with open(f"{CARDS_FOLDER}/{card}", "rb") as img:
        await query.message.reply_photo(img)

    # Отправляем напоминание о возможности вытянуть следующую карту
    chat_id = query.from_user.id
    await send_invite_message(chat_id, context.bot)

# --- Создаём приложение ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_callback))

# --- JobQueue для ежедневного сообщения ---
job_queue = app.job_queue

async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in users:
        await send_invite_message(chat_id, context.bot)

# Запуск ежедневного сообщения в 10:00
job_queue.run_daily(daily_reminder, time(hour=10, minute=0))

# --- Запуск бота ---
app.run_polling()