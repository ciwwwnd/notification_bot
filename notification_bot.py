import requests
import telegram
import time
import os
import dotenv
import logging
logging.basicConfig(level=logging.DEBUG)


def main():
    dotenv.load_dotenv()
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]
    devman_token = os.environ["DEVMAN_TOKEN"]
    
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': devman_token
    }
    timestamp = time.time()
    params = {
        'timestamp': timestamp
    }

    while True:
        try:
            bot = telegram.Bot(token=token)
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            lessons = response.json()
            if lessons['status'] == 'found':
                params['timestamp'] = lessons['last_attempt_timestamp']
                send_messages(bot, lessons['new_attempts'], chat_id)
            else:
                params['timestamp'] = lessons['timestamp_to_request']
        except requests.exceptions.ConnectionError:
            time.sleep(30)
        except requests.exceptions.HTTPError:  
            logging.error('HTTPError')
        except Exception:
            logging.debug('Exception')


def send_messages(bot, attempts, chat_id):
    for attempt in attempts:
        if attempt['is_negative']:
            message = """У вас проверили работу «{}». К сожалению, в работе есть ошибки.""".format(
                attempt['lesson_title'])
        else:
            message = """У вас проверили работу «{}». Преподавателю все понравилось, можно приступать к следующему уроку!""".format(
                attempt['lesson_title'])
        bot.send_message(chat_id=chat_id, text=message)


if __name__ == '__main__':
    main()