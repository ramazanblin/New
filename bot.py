
import os
import threading
from flask import Flask
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler

# Telegram Bot Setup
TOKEN = os.getenv("TOKEN")

# Создаем объект приложения
application = Application.builder().token(TOKEN).build()

# Simple /start command
def start(update: Update, context):
    update.message.reply_text("Привет! Я ваш бот!")

application.add_handler(CommandHandler("start", start))

# Start bot in a separate thread
def run_bot():
    application.run_polling()

threading.Thread(target=run_bot).start()

# Flask server setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
