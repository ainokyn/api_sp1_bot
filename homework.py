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


def parse_homework_status(homework):
    """This function gets the project name and the status of the work."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None and homework_status is None:
        logger.error('Отсутствует имя или статус работы.')
    if homework_status == 'rejected':
        verdict = 'К сожалению, в работе нашлись ошибки.'
    elif homework_status == 'reviewing':
        verdict = 'Твоя работа взята на ревью.'
    elif homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, работа зачтена!'
    else:
        logger.error('Неизвестный статус работы.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    """This function receives a json response about homework."""
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, headers=headers, params=payload)
    except requests.RequestException as e:
        logger.error(f'Возникла проблема с запросом: {e}')
    return homework_statuses.json()


def send_message(message):
    """This function sends a message to telegram."""
    logger.info('Сообщение отправлено')
    try:
        return bot.send_message(chat_id=CHAT_ID, text=message)
    except BadRequest as e:
        logger.error(f'Проблема с chat_id: {e}')


def main():
    """A function that performs the main functionality of the bot."""
    logger.debug('Программа стартует')
    current_timestamp = int(time.time())
    while True:
        try:
            homework = get_homeworks(current_timestamp)
            if homework.get('homeworks'):
                send_message(message=parse_homework_status(
                    homework.get('homeworks')[0]))
                current_timestamp = homework.get('current status')
                time.sleep(5 * 60)
        except Exception as e:
            logger.error(e)
            bot.send_message(text=f'Бот упал с ошибкой: {e}', chat_id=CHAT_ID)
            time.sleep(5)


if __name__ == '__main__':
    main()
