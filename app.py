import os
import logging
import asyncio
from threading import Thread
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Загружаем переменные окружения
load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1915339238 # <--- ЗАМЕНИТЕ НА СВОЙ ID (число)
PORT = int(os.environ.get('PORT', 8080)) # Порт, который даст Render

# Состояния для опроса

Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8 = range(8)

questions = {
    0: {
	"text": "1. Если бы у вас была полная свобода выбора, во сколько бы вы ложились спать?",
	"options": ["21:00–22:30", "22:30–00:00", "00:00–01:30", "После 01:30"],
	"scores": [1, 2, 3, 4],
    },
    1: {
	"text": "2. Если бы у вас была полная свобода выбора, во сколько бы вы просыпались?",
	"options": ["До 6:00", "6:00–7:30", "7:30–9:00", "После 9:00"],
	"scores": [1, 2, 3, 4],
    },
    2: {
	"text": "3. Сколько часов сна вам обычно требуется, чтобы выспаться?",
	"options": ["Менее 6 часов", "6–7 часов", "7–8 часов", "Более 8 часов"],
	"scores": [1, 2, 3, 4],
    },
    3: {
	"text": "4. В какое время суток вы чувствуете наибольший прилив энергии?",
	"options": ["Утро (до 12:00)", "День (12:00–17:00)", "Вечер (17:00–22:00)", "Ночь (после 22:00)"],
	"scores": [1, 2, 3, 4],
    },
    4: {
	"text": "5. Как легко вы просыпаетесь утром в рабочий день?",
	"options": ["Очень легко, сам до будильника", "Довольно легко, с первым будильником", "Тяжеловато, нужно несколько сигналов", "Очень тяжело, разбитость"],
	"scores": [1, 2, 3, 4],
    },
    5: {
	"text": "6. Как вы чувствуете себя в середине дня (после обеда)?",
	"options": ["Полон сил, могу работать", "Немного спада, но терпимо", "Заметный спад, хочется прилечь", "Сильная сонливость"],
	"scores": [1, 2, 3, 4],
    },
    6: {
	"text": "7. Если важная умственная работа, в какое время вы её сделаете лучше?",
	"options": ["Сразу после пробуждения", "В первой половине дня", "Во второй половине дня", "Поздно вечером или ночью"],
	"scores": [1, 2, 3, 4],
    },
    7: {
	"text": "8. Как часто вы чувствуете усталость или сонливость в течение дня?",
	"options": ["Почти никогда, всегда бодр", "Редко, только после нагрузок", "Иногда, особенно после обеда", "Часто, постоянно хочется спать"],
	"scores": [1, 2, 3, 4],
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (ваша функция start)
    pass

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, q_index: int, next_state: int | None) -> int:
    # ... (ваша функция handle_answer)
    pass

# --- Все ваши обработчики q1_handler, q2_handler, ... , cancel ---
async def q1_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 0, Q2)

async def q2_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 1, Q3)

async def q3_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 2, Q4)

async def q4_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 3, Q5)

async def q5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 4, Q6)

async def q6_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 5, Q7)

async def q7_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 6, Q8)

async def q8_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await handle_answer(update, context, 7, None)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Тест отменён.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

# Функция для создания и запуска бота в отдельном потоке
def run_bot():
    import asyncio
    # Создаем новый цикл событий для этого потока
    loop = asyncio.set_event_loop()
    asyncio.set_event_loop(loop)

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            Q1: [MessageHandler(filters.TEXT & ~filters.COMMAND, q1_handler)],
            Q2: [MessageHandler(filters.TEXT & ~filters.COMMAND, q2_handler)],
            Q3: [MessageHandler(filters.TEXT & ~filters.COMMAND, q3_handler)],
            Q4: [MessageHandler(filters.TEXT & ~filters.COMMAND, q4_handler)],
            Q5: [MessageHandler(filters.TEXT & ~filters.COMMAND, q5_handler)],
            Q6: [MessageHandler(filters.TEXT & ~filters.COMMAND, q6_handler)],
            Q7: [MessageHandler(filters.TEXT & ~filters.COMMAND, q7_handler)],
            Q8: [MessageHandler(filters.TEXT & ~filters.COMMAND, q8_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    logging.info("Бот запущен и работает...")
    application.run_polling()

# --- Flask приложение для Render ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает!", 200

@app.route('/health')
def health():
    # Render будет проверять этот адрес, чтобы убедиться, что всё работает
    return "OK", 200

# Функция, которая запустит бота в фоновом потоке при старте Flask
def start_bot():
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logging.info("Поток бота запущен")

# Запускаем бота в отдельном потоке сразу при старте
start_bot()

# Эта часть выполняется только если мы запускаем скрипт напрямую
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)