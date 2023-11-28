import random
import logging
import redis
from dotenv import load_dotenv
from os import getenv
from common_functions import get_quiz_data

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


def send_message(event, vk_api, message):
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        random_id=get_random_id()
    )


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    vk_api_key = getenv('VK_API_KEY')
    vk_user_id = getenv('VK_USER_ID')
    redis_host = getenv('REDIS_HOST')
    redis_port = getenv('REDIS_PORT')
    redis_password = getenv('REDIS_PASSWORD')

    db = redis.Redis(
      host=redis_host,
      port=redis_port,
      password=redis_password,
      decode_responses=True
      )

    quiz_data = get_quiz_data()
    vk_session = vk.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    vk_api.messages.send(
        peer_id=vk_user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Привет! Я бот для викторин. Нажми "Новый вопрос" для начала!'
    )

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                question = random.choice(list(quiz_data.keys()))
                db.set(event.user_id, question)
                send_message(event, vk_api, question)

            elif not (question := db.get(event.user_id)):
                continue

            elif event.text == quiz_data[question]:
                message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
                send_message(event, vk_api, message)

            elif event.text == 'Сдаться':
                message = f'Правильный ответ:\n{quiz_data[question]}'
                send_message(event, vk_api, message)

            else:
                message = 'Неправильно… Попробуешь ещё раз?'
                send_message(event, vk_api, message)


if __name__ == "__main__":
    main()
