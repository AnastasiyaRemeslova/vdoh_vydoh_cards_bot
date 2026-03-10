import os
import random
from fastapi import FastAPI, Request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
app = FastAPI()

telegram_app = Application.builder().token(TOKEN).build()


async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Получить карточку", callback_data="card")]
    ]

    await update.message.reply_text(
        "Нажмите кнопку, чтобы получить карточку",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def send_card(update: Update, context):
    query = update.callback_query
    await query.answer()

    cards = os.listdir("cards")
    card = random.choice(cards)

    with open(f"cards/{card}", "rb") as img:
        await query.message.reply_photo(img)


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(send_card))


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return {"ok": True}