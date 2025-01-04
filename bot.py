
import os
import threading
from flask import Flask
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler

# Telegram Bot Setup
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Simple /start command
def start(update: Update, context):
    update.message.reply_text("Привет! Я ваш бот!")

dispatcher.add_handler(CommandHandler("start", start))

# Start bot in a separate thread
def run_bot():
    updater.start_polling()
    updater.idle()

threading.Thread(target=run_bot).start()

# Flask server setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
