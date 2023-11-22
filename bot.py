import logging
from dotenv import load_dotenv
from os import getenv
from telegram import Update
from telegram.ext import (Updater, CommandHandler, CallbackContext,
                          MessageHandler, Filters)


logger = logging.getLogger('tg_bot')


def get_quiz_questions():
    questions = []
    with open('quiz_questions.txt', 'r', encoding='koi8-r') as file:
        while line := file.readline():
            if line.startswith('Вопрос '):
                question = ''
                while question_line := file.readline():
                    if question_line == '\n':
                        break
                    question += question_line.replace('\n', ' ')
            elif line.startswith('Ответ:'):
                answer = file.readline().strip()
                questions.append(
                    {
                        'question': question,
                        'answer': answer,
                    }
                )
    return questions


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Здравствуйте'
    )


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text
    )


def main():
    load_dotenv()
    tg_bot_token = getenv('TG_BOT_TOKEN')
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(
        Filters.text & (~Filters.command),
        echo
    )
    dispatcher.add_handler(echo_handler)
    updater.start_polling()


if __name__ == '__main__':
    main()
