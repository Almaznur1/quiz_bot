import logging
import random
import redis
import argparse
from dotenv import load_dotenv
from os import getenv
from get_quiz_data import get_quiz_data
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, CallbackContext,
                          MessageHandler, Filters, ConversationHandler)


logger = logging.getLogger('tg_bot')

CHOOSING, ANSWER_WAITING = range(2)


def start(update: Update, context: CallbackContext, reply_markup):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! Я бот для викторин. Нажми "Новый вопрос" для начала!',
        reply_markup=reply_markup
    )
    return CHOOSING


def handle_new_question_request(
        update: Update, context: CallbackContext, db, question, reply_markup
        ):
    db.set(update.effective_chat.id, question)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question,
        reply_markup=reply_markup
    )
    return ANSWER_WAITING


def handle_solution_attempt(
        update: Update, context: CallbackContext, db, quiz_data, reply_markup
        ):
    question = db.get(update.effective_chat.id)

    if '.' in quiz_data[question]:
        index = quiz_data[question].index('.')
        right_answer = quiz_data[question][:index]
    elif '(' in quiz_data[question]:
        index = quiz_data[question].index('(')
        right_answer = quiz_data[question][:index]

    if right_answer == update.message.text:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            reply_markup=reply_markup
        )
        return CHOOSING
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Неправильно… Попробуешь ещё раз?',
            reply_markup=reply_markup
        )
        return ANSWER_WAITING


def handle_give_up_button(
        update: Update, context: CallbackContext, db, quiz_data, reply_markup
        ):
    question = db.get(update.effective_chat.id)
    answer = quiz_data[question]
    context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Правильный ответ:\n{answer}',
            reply_markup=reply_markup
        )
    return CHOOSING


def cancel(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Спасибо за участие, до скорой встречи!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    parser = argparse.ArgumentParser(
        description='Telegram bot for quizzes')
    parser.add_argument('--path',
                        type=str,
                        default='quiz_questions.txt',
                        help='specify the quiz data path')
    args = parser.parse_args()

    load_dotenv()
    tg_bot_token = getenv('TG_BOT_TOKEN')
    redis_host = getenv('REDIS_HOST')
    redis_port = getenv('REDIS_PORT')
    redis_password = getenv('REDIS_PASSWORD')

    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    keyboard = [
        ['Новый вопрос', 'Сдаться'],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    db = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True
    )

    quiz_data = get_quiz_data(args.path)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler(
                'start',
                lambda update, context: start(
                    update, context,
                    reply_markup=reply_markup
                )
            )
        ],

        states={
            CHOOSING: [
                MessageHandler(
                    Filters.text('Новый вопрос'),
                    lambda update, context: handle_new_question_request(
                        update, context,
                        db=db,
                        question=random.choice(list(quiz_data.keys())),
                        reply_markup=reply_markup
                    )
                ),
            ],

            ANSWER_WAITING: [
                MessageHandler(
                    Filters.text('Сдаться'),
                    lambda update, context: handle_give_up_button(
                        update, context,
                        db=db,
                        quiz_data=quiz_data,
                        reply_markup=reply_markup
                    )
                ),
                MessageHandler(
                    Filters.text,
                    lambda update, context: handle_solution_attempt(
                        update, context,
                        db=db,
                        quiz_data=quiz_data,
                        reply_markup=reply_markup
                    )
                )
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()


if __name__ == '__main__':
    main()
