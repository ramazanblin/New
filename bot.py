import os
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Flask-приложение
app = Flask(__name__)

# Telegram Bot
TOKEN = os.getenv("TOKEN")
bot_application = ApplicationBuilder().token(TOKEN).build()

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я ваш бот!")

bot_application.add_handler(CommandHandler("start", start))

# Асинхронный запуск Telegram-бота
async def run_bot():
    await bot_application.initialize()
    await bot_application.start()
    await bot_application.updater.start_polling()

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    import asyncio
    # Запускаем Telegram-бота и Flask-сервер
    asyncio.run(run_bot())
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
