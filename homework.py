import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import BadRequest

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s',
    handlers=[logging.FileHandler('log.log', mode='a'),
              logging.StreamHandler(sys.stdout)]
)
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
bot = Bot(token=TELEGRAM_TOKEN)
good_status = {'reviewing': 'Твоя работа взята на ревью.',
               'rejected': 'К сожалению, в работе нашлись ошибки.',
               'approved': 'Ревьюеру всё понравилось, работа зачтена!'}
bad_status = {None: 'Объект отсутствует',
              " ": 'Объект пустая строка'}


def parse_homework_status(homework):
    """This function gets the project name and the status of the work."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    print(homework_status)
    time.sleep(600)
    if homework_status in good_status:
        verdict = good_status[homework_status]
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    if homework_status not in good_status:
        if homework_status in bad_status:
            logger.error('Проблема со статусом работы.')
            error = bad_status[homework_status]
            print(error)
            bot.send_message(text=f'Бот упал с ошибкой: {error}', chat_id=CHAT_ID)
            return f'У вас ошибка "{error}"!'
        else:
            logger.error('Неизвестная ошибка статуса работы.')
            return 'Неизвестная ошибка статуса работы.'
    if homework_name in bad_status:
        logger.error('Проблема с именем работы.')
        error = bad_status[homework_name]
        print(error)
        bot.send_message(text=f'Бот упал с ошибкой: {error}', chat_id=CHAT_ID)
        return f'У вас ошибка "{error}"!'


def get_homeworks(current_timestamp):
    """This function receives a json response about homework."""
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
        print(headers, payload, homework_statuses)
        bot.send_message(text=f'Статус работы: {homework_statuses.text}', chat_id=CHAT_ID)
        bot.send_message(text=f'{headers}, {payload}', chat_id=CHAT_ID)
        time.sleep(600)
    except requests.RequestException as e:
        print(e)
        logger.error(f'Возникла проблема с запросом: {e}')
        return {}
    return homework_statuses.json()


def send_message(message):
    """This function sends a message to telegram."""
    logger.info('Сообщение отправлено')
    try:
        print(CHAT_ID, message)
        return bot.send_message(chat_id=CHAT_ID, text=message)
    except BadRequest as e:
        logger.error(f'Проблема с chat_id: {e}')
        print(e)
        bot.send_message(text=f'Бот упал с ошибкой: {e}', chat_id=CHAT_ID)


def main():
    """A function that performs the main functionality of the bot."""
    logger.debug('Программа стартует')
    current_timestamp = int(time.time())
    while True:
        try:
            homework = get_homeworks(current_timestamp)
            bot.send_message(text=f'{homework}', chat_id=CHAT_ID)
            time.sleep(600)
            if homework.get('homeworks'):
                send_message(message=parse_homework_status(
                    homework.get('homeworks')[0]))
                current_timestamp = homework.get('current_date')
                time.sleep(1200)
        except Exception as e:
            logger.error(e)
            print(e)
            bot.send_message(text=f'Бот упал с ошибкой: {e}', chat_id=CHAT_ID)
            time.sleep(1200)


if __name__ == '__main__':
    main()
