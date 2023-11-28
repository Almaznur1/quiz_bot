import random
import logging
from dotenv import load_dotenv
from os import getenv
from 

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id


def echo(event, vk_api):

    vk_api.messages.send(
        user_id=event.user_id,
        message=,
        random_id=random.randint(1, 1000)
    )


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    vk_api_key = getenv('VK_API_KEY')
    redis_host = getenv('REDIS_HOST')
    redis_port = getenv('REDIS_PORT')
    redis_password = getenv('REDIS_PASSWORD')

    quiz_data = get_quiz_data()
    vk_session = vk.VkApi(token=vk_api_key)
    vk_api = vk_session.get_api()

    # keyboard = VkKeyboard(one_time=True)
    keyboard = VkKeyboard()

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    vk_api.messages.send(
        peer_id=657767863,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Привет! Я бот для викторин. Нажми "Новый вопрос" для начала!'
    )

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':



if __name__ == "__main__":
    main()
