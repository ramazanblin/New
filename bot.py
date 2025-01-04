
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
from datetime import datetime, timedelta
import asyncio

# Ваш токен от BotFather
import os
TOKEN = os.getenv("TOKEN")

# Состояния для ConversationHandler
SET_WEIGHT, SET_COURSE_DURATION = range(2)

# Хранилище данных пользователя
user_data = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу вам рассчитать дозировку системных ретиноидов (Роаккутан, Акнекутан, Сотрет) и напомнить о приеме лекарства.\n"
        "Вот что я умею:\n"
        "/calculate_dose - Рассчитать суточную и кумулятивную дозу\n"
        "/set_reminder - Установить напоминание о приеме\n"
        "/help - Показать справку"
    )

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Команды:\n"
        "/calculate_dose - Рассчитать суточную дозировку и кумулятивную дозу за курс\n"
        "/set_reminder - Установить напоминание о приеме лекарства\n"
    )

# Запрос веса
async def calculate_dose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ваш вес в килограммах:")
    return SET_WEIGHT

# Расчет дозировки
async def set_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
        user_data[update.effective_user.id] = {"weight": weight}

        # Рассчитываем дозировки
        dose_low = 0.5 * weight  # 0.5 мг/кг
        dose_medium = 0.8 * weight  # 0.8 мг/кг (средняя)
        dose_high = 1.0 * weight  # 1.0 мг/кг

        # Средняя доза для расчета
        daily_dose = dose_medium

        # Сохраняем данные
        user_data[update.effective_user.id]["daily_dose"] = daily_dose

        await update.message.reply_text(
            f"Для вашего веса ({weight} кг):\n"
            f"- Легкая степень акне: {dose_low:.2f} мг/день\n"
            f"- Средняя степень акне (рекомендуемая): {dose_medium:.2f} мг/день\n"
            f"- Тяжелая степень акне: {dose_high:.2f} мг/день\n\n"
            f"Средняя доза (0.8 мг/кг): {daily_dose:.2f} мг/день.\n"
            "Теперь укажите длительность лечения в месяцах:"
        )
        return SET_COURSE_DURATION
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите ваш вес числом.")
        return SET_WEIGHT

# Расчет кумулятивной дозы
async def set_course_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        months = int(update.message.text)
        user_id = update.effective_user.id
        weight = user_data[user_id]["weight"]
        daily_dose = user_data[user_id]["daily_dose"]

        # Расчет дозировки за курс
        days_in_month = 30  # Упрощенно
        total_days = months * days_in_month
        cumulative_dose = daily_dose * total_days

        # Рекомендуемая кумулятивная доза
        recommended_cumulative_dose = 150 * weight

        await update.message.reply_text(
            f"Длительность курса: {months} месяцев.\n"
            f"Кумулятивная доза за курс: {cumulative_dose:.2f} мг.\n"
            f"Рекомендуемая кумулятивная доза: {recommended_cumulative_dose:.2f} мг (150 мг/кг).\n"
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Введите длительность курса числом (например, 6).")
        return SET_COURSE_DURATION

# Установка напоминания
async def set_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напоминание будет настроено. Принимать таблетки нужно 2 раза в день: утром и вечером.\n"
        "Напоминания будут приходить за час до приема (например, в 8:00 и 20:00)."
    )
    asyncio.create_task(send_reminders(update, context))
    return ConversationHandler.END

# Напоминания
async def send_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    times = [(8, 0), (20, 0)]  # Время напоминаний: 8:00 и 20:00
    while True:
        now = datetime.now()
        for hour, minute in times:
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if reminder_time > now:
                await asyncio.sleep((reminder_time - now).total_seconds())
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text="Напоминание: пора принять таблетки!"
                )
        await asyncio.sleep(60)  # Проверяем каждый час

# Главная функция
def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Обработчик расчета дозировки
    dose_conv = ConversationHandler(
        entry_points=[CommandHandler("calculate_dose", calculate_dose)],
        states={
            SET_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_weight)],
            SET_COURSE_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_course_duration)
            ],
        },
        fallbacks=[],
    )
    app.add_handler(dose_conv)

    # Напоминания
    app.add_handler(CommandHandler("set_reminder", set_reminder))

    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()
