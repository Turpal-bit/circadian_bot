import os
import logging
import asyncio
from flask import Flask, request
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Токен и ID администратора (уже вставлены)
TOKEN = "8543435743:AAFgYVdA2H5QWfH9_xuTeOLUbKrtzVQTRws"
ADMIN_ID = 1915339238
PORT = int(os.environ.get('PORT', 8080))

# Состояния для опроса
Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8 = range(8)

# ---------- Словарь вопросов ----------
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

# ---------- Функции-обработчики ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Этот тест определит твой циркадный хронотип.\n"
        "Отвечай на вопросы, выбирая вариант из кнопок.",
        reply_markup=ReplyKeyboardRemove()
    )
    q = questions[0]
    await update.message.reply_text(
        q["text"],
        reply_markup=ReplyKeyboardMarkup(
            [[opt] for opt in q["options"]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return Q1

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, q_index: int, next_state: int | None) -> int:
    user_answer = update.message.text
    q_data = questions[q_index]
    valid_options = q_data["options"]

    if user_answer not in valid_options:
        await update.message.reply_text(
            "Пожалуйста, выберите вариант из кнопок.",
            reply_markup=ReplyKeyboardMarkup(
                [[opt] for opt in valid_options],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        return q_index
    if 'answers' not in context.user_data:
        context.user_data['answers'] = {}
    idx = valid_options.index(user_answer)
    score = q_data["scores"][idx]
    context.user_data['answers'][f'q{q_index+1}'] = {'text': user_answer, 'score': score}

    if next_state is None:
        answers = context.user_data['answers']
        energy_score = answers.get('q3', {}).get('score', 0) + answers.get('q6', {}).get('score', 0) + answers.get('q8', {}).get('score', 0)
        time_score = answers.get('q1', {}).get('score', 0) + answers.get('q2', {}).get('score', 0) + answers.get('q4', {}).get('score', 0) + answers.get('q5', {}).get('score', 0) + answers.get('q7', {}).get('score', 0)

        if energy_score <= 6:
            chronotype = "Колибри"
            description = "Вы очень активны, спите мало и редко устаёте. Не забывайте отдыхать!"
        else:
            if time_score <= 9:
                chronotype = "Жаворонок"
                description = "Вы любите рано вставать, пик активности — утро. Планируйте важное на первую половину дня."
            elif time_score <= 14:
                chronotype = "Голубь"
                description = "Ваш пик — днём. Хорошо адаптируетесь, но соблюдайте режим."
            else:
                chronotype = "Сова"
                description = "Активны вечером/ночью, утром тяжело. Планируйте сложные задачи на вечер."

       await update.message.reply_text(
           f" **Ваш хронотип: {chronotype}**\n\n{description}",
           reply_markup=ReplyKeyboardRemove(),
           parse_mode='Markdown'
       )

       user = update.effective_user
       admin_msg = (
           f"Новый результат:\n"
           f"Пользователь: {user.full_name} (@{user.username})\n"
           f"ID: {user.id}\n"
           f"Хронотип: {chronotype}\n"
           f"Баллы энергии: {energy_score}\n"
           f"Баллы времени: {time_score}\n"
           f"Детали: {answers}"
      )
      try:
         await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
      except Exception as e:
          logging.error(f"Не удалось отправить админу: {e}")

      context.user_data.clear()
      return ConversationHandler.END
  else:
      next_q = questions[next_state]
      await update.message.reply_text(
          next_q["text"],
          reply_markup=ReplyKeyboardMarkup(
              [[opt] for opt in next_q["options"]],
              one_time_keyboard=True,
              resize_keyboard=True
          )
      )
      return next_state

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

# ---------- СОЗДАЁМ ПРИЛОЖЕНИЕ БОТА ----------

application = Application.builder().token(TOKEN).build()

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

async def init_app():
    await application.initialize()
    logging.info("✅ Application initialized")

asyncio.run(init_app())

# ---------- FLASK ПРИЛОЖЕНИЕ ----------

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.run(application.process_update(update))
    return 'OK', 200

@app.route('/')
def index():
    return 'Бот работает!', 200

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)