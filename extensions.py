"""Файл с методами и функциями, необходимыми для работы бота"""

import sqlite3
import logging
from config import *

# Создание Логгера, для вывода информации о работе бота в файл
logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename='gptBot.log', level=logging.INFO, format=FORMAT)

# Получение ID пользователя независимо от способа вызова функции
def get_id(message):
    try:
        chat_id = message.message.chat.id
    except AttributeError:
        chat_id = message.chat.id
    return chat_id

# Функция для изменения сообщения бота или отправки нового, если до этого бот не присылал ничего
def send_or_edit(call, bot, text, markup=None):
    chat_id = get_id(call)

    try:
        msg = bot.edit_message_text(chat_id=chat_id, text=text, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)
    except:
        msg = bot.send_message(chat_id=chat_id, text=text, parse_mode='Markdown', reply_markup=markup)

    return msg

# Функция проверки баланса "Монет" у пользователя
def check_balance(message):
    chat_id = get_id(message)
    # Подключение к БД
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT money_balance FROM users WHERE user_id = ?''', (chat_id,))
        user_balance = cursor.fetchone()[0]
    return user_balance

# Функция регистрации пользователя в боте
def register_user(message):
    chat_id = get_id(message)
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO users (user_id) VALUES (?)''', (chat_id,))

# Функция при успешном использовании ИИ
def gpt_used(message):
    chat_id = get_id(message)
    # Списание Монет и увеличение кол-ва попыток использования для пользователя
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET money_balance = money_balance - 5, usage_times = usage_times + 1 WHERE user_id = ?''', (chat_id,))

    # Проверка, если пользователь использовал ИИ >5 раз и начисление ему подарочных монет
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT usage_times FROM users WHERE user_id = ?''', (chat_id,))
        times = cursor.fetchone()
    if times[0] >= 5:
        with sqlite3.connect(db) as conn:
            cursor = conn.cursor()
            cursor.execute('''UPDATE users SET usage_times = 0 WHERE user_id = ?''', (chat_id,))
        top_up(message, 1)
        return 1


# Пополнение баланса пользователя на заданную сумму в amount
def top_up(message, amount):
    chat_id = get_id(message)
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET money_balance = money_balance + ? WHERE user_id = ?''', (amount, chat_id,))