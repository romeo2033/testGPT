"""Файл для отправки любого сообщения пользователям от имени бота"""

from telebot.apihelper import ApiTelegramException
from extensions import logger
from main import send_any_message
from config import db
import sqlite3

# Функция отправки сообщения принимающая ID пользователя и текст сообщения
def send_message(user, text):
    try:
        send_any_message(user, text)
    except ApiTelegramException as e:
        logger.error(f'Message: "{text}" for UserID: {user} was not sent due to: {e}')

# Текст сообщения
message_text = "Hello World"

"""Отправка сообщения всем пользователям бота"""
# with sqlite3.connect(db) as conn:
#     cursor = conn.cursor()
#     cursor.execute('''SELECT user_id FROM users''')
#     user_ids = cursor.fetchall()
#     for user_id in user_ids:
#         send_message(user_id[0], message_text)

"""Отправка сообщения по выбранному ID"""
# usr_id = 123456
# send_message(usr_id, message_text)



