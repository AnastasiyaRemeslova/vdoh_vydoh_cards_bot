import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Кнопка для получения карточки
keyboard = [["Получить карточку"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Нажмите кнопку, чтобы получить карточку",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Получить карточку", callback_data="get_card")]]
        )
    )

# Обработка нажатия на кнопку
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "get_card":
        cards = os.listdir("cards")
        card = random.choice(cards)
        with open(f"cards/{card}", "rb") as img:
            await query.message.reply_photo(img)
        # Напоминание, что можно вытянуть следующую карту
        await query.message.reply_text(
            "Нажмите кнопку, чтобы получить следующую карточку",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Получить карточку", callback_data="get_card")]]
            )
        )

# Создаём приложение
app = ApplicationBuilder().token(TOKEN).build()

# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), start))  # на случай, если пользователь пишет текст
app.add_handler(MessageHandler(filters.StatusUpdate.ALL, start))
app.add_handler(telegram.ext.CallbackQueryHandler(button_handler))

# Запуск бота с polling
app.run_polling()