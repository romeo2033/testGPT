import telebot
from telebot import types

import text
import gpt
from extensions import *

# Создание объекта бота
bot = telebot.TeleBot(TOKEN)

# Начальная функция
@bot.message_handler(commands=['start'])
def start_bot(message):
    register_user(message)

    # Создание кнопок
    markup = types.InlineKeyboardMarkup()
    ai_btn = types.InlineKeyboardButton("🤖 Написать ИИ", callback_data="new_chat")
    topic_btn = types.InlineKeyboardButton("💡 ИИ по темам", callback_data="new_chat_topic")
    balance_btn = types.InlineKeyboardButton("⭐️ Баланс", callback_data="balance")
    help_btn = types.InlineKeyboardButton("🆘️ Помощь", callback_data="help")
    # Оформление кнопок по рядам
    markup.row(ai_btn)
    markup.row(topic_btn)
    markup.row(balance_btn, help_btn)

    # Отправка сообщения
    send_or_edit(message, bot, text.hello, markup)

# Считыватель команды /balance
@bot.message_handler(commands=['balance'])
# Перенаправка на соответсвующую функцию
def redirect_to_balance(message):
    balance(message)

# Считыватель команды /ask
@bot.message_handler(commands=['ask'])
def redirect_to_gpt(message):
    ai_chat(message)

# Перенаправка на функцию помощи
@bot.callback_query_handler(func=lambda call: call.data == "help")
def redirect_to_help(call):
    help_message(call)

# Перенаправка "домой"
@bot.callback_query_handler(func=lambda call: call.data == 'home')
def home(call):
    start_bot(call)

# Считыватель команды /help
@bot.message_handler(commands=['help'])
# Функция вывода текста помощи
def help_message(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
    send_or_edit(message,bot,text.help_text,markup=markup)

# Функция проверки баланса пользователя
@bot.callback_query_handler(func=lambda call: call.data == 'balance')
def balance(call):
    user_balance = check_balance(call)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
    markup.add(types.InlineKeyboardButton('💰 Пополнить баланс', callback_data="will_top_up"))

    send_or_edit(call, bot, f'*⭐️ Твой баланс:* {user_balance}', markup=markup)

# Новый чат с ИИ без использования тем общения
@bot.callback_query_handler(func=lambda call: call.data == 'new_chat')
def ai_chat(call):
    user_balance = check_balance(call)

    # Проверка, есть ли у пользователя достаточный баланс
    if user_balance < 5:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
        message_text = text.not_enough_balance(user_balance)
        send_or_edit(call, bot, message_text, markup)
    else:
        msg = send_or_edit(call, bot, 'Супер! Напиши мне свой вопрос.')
        bot.register_next_step_handler(msg, send_message_to_gpt)

# Отправка сообщения ИИ
def send_message_to_gpt(message):
    chat_id = get_id(message)
    bot.delete_message(chat_id=chat_id, message_id=message.message_id-1)

    # Проверка, что пользователь ввел текст, а не другой формат (фото, видео и тд)
    if message.content_type == 'text':
        answer = gpt.get_ai_answer(message.text, 'default')
        if answer.startswith('🤯'):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
            answer += '\n\nК сожалению сейчас бот не поддерживает контекст. Можешь вернуться на главную и задать еще один вопрос.'
            # Проверка, если пользователь должен быть награжден
            is_rewarded = gpt_used(message)
            if is_rewarded:
                bot.send_message(chat_id, '❤️ Спасибо, что пользуешься мной!\n\n*За 5 использований, ты получаешь 1 монету!*', parse_mode='Markdown')
    else:
        markup = None
        answer = 'Недопустимый формат!\n\nДопускается только текст!'
        bot.send_message(chat_id, answer, reply_markup=markup, parse_mode='Markdown')
        ai_chat(message)
        return

    bot.send_message(chat_id, answer, reply_markup=markup)

# Функция выбора темы общения с ботом
@bot.callback_query_handler(func=lambda call: call.data == 'new_chat_topic')
def choose_topic(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('👨‍💼 Бизнесмен', callback_data="topic_chat_businessman"))
    markup.add(types.InlineKeyboardButton('👶 Ребенок', callback_data="topic_chat_kid"))
    markup.add(types.InlineKeyboardButton('👨‍🎓 Историк', callback_data="topic_chat_history"))

    send_or_edit(call, bot, '*Выбери кто будет с тобой общаться:*', markup=markup)

# Новый чат с ботом на выбранную тему
@bot.callback_query_handler(func=lambda call: call.data.startswith('topic_chat'))
def ai_topic_chat(call):
    user_balance = check_balance(call)
    topic = call.data.split('_')[2]

    if user_balance < 5:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
        message_text = text.not_enough_balance(user_balance)
        send_or_edit(call, bot, message_text, markup)
    else:
        msg = send_or_edit(call, bot, 'Супер! Напиши мне свой вопрос.')
        bot.register_next_step_handler(msg, send_message_to_gpt_topic, topic)

def send_message_to_gpt_topic(message, topic):
    chat_id = get_id(message)
    bot.delete_message(chat_id=chat_id, message_id=message.message_id-1)

    if message.content_type == 'text':
        answer = gpt.get_ai_answer(message.text, topic)
        if answer.startswith('🤯 '):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
            answer += '\n\nК сожалению сейчас бот не поддерживает контекст. Можешь вернуться на главную и задать еще один вопрос.'
            is_rewarded = gpt_used(message)
            if is_rewarded:
                bot.send_message(chat_id, '❤️ Спасибо, что пользуешься мной!\n\n*За 5 использований, ты получаешь 1 монету!*', parse_mode='Markdown')
    else:
        markup = None
        answer = 'Недопустимый формат!\n\nДопускается только текст!'
        bot.send_message(chat_id, answer, reply_markup=markup, parse_mode='Markdown')
        ai_chat(message)
        return

    bot.send_message(chat_id, answer, reply_markup=markup)

# Функция выбора суммы пополнения баланса
@bot.callback_query_handler(func=lambda call: call.data == 'will_top_up')
def top_up_amount(call):
    chat_id = get_id(call)
    user_balance = check_balance(call)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('⭐️ 5', callback_data="top_up_5"))
    markup.add(types.InlineKeyboardButton('⭐️ 10', callback_data="top_up_10"))
    markup.add(types.InlineKeyboardButton('⭐️ 100', callback_data="top_up_100"))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data="balance"))

    bot.edit_message_text(chat_id=chat_id, text=f'*🫰 Твой текущий баланс: {user_balance}*\n\nВыбери сумму пополнения 👇', message_id=call.message.message_id, reply_markup=markup, parse_mode='Markdown')

# Пополнение баланса
@bot.callback_query_handler(func=lambda call: call.data.startswith('top_up_'))
def top_up_balance(call):
    chat_id = get_id(call)
    amount = int(call.data.split('_')[2])
    top_up(call, amount)
    user_balance = check_balance(call)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🏠 На главную', callback_data="home"))
    markup.add(types.InlineKeyboardButton('💰 Добавить ещё!', callback_data="will_top_up"))

    bot.edit_message_text(chat_id=chat_id, text=f'*✅ Баланс успешно пополнен!*\n\nСейчас он составляет: {user_balance}', message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)

# Отправка любого сообщения пользователям от имени бота через файл dispatch.py
def send_any_message(chat_id, message_text):
    bot.send_message(chat_id, message_text, parse_mode='Markdown')
    logger.info(f'Message: "{message_text}" sent to User ID: {chat_id}')

# Запуск бота
if __name__ == '__main__':
    logger.info('Bot started')
    bot.infinity_polling(allowed_updates=['message', 'callback_query'], none_stop = True)
    logger.info('Bot stopped')