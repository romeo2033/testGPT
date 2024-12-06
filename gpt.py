"""Файл содержащий инструкции боту для связи с ChatGPT"""

import openai
from config import openaiTOKEN
from extensions import logger

# Создание объекта client
client = openai.OpenAI(api_key=openaiTOKEN)

# Функция для отправки запроса и получение ответа от ИИ
def get_ai_answer(message, topic):
  # Словарь {Тема:СообщенияДляИИ}
  topics = {
    'default': [
          {"role": "system", "content": 'Привет, ты очень полезный ассистент!'},
          {"role": "user", "content": message}
      ],
    'businessman' : [
        {"role": "system", "content": 'Привет, ты очень грамотный бизнесмен, готовый дать ответы на все вопросы.'},
        {"role": "user", "content": message}
      ],
    'kid': [
      {"role": "system", "content": 'Привет, представь что ты ребенок и общаешься с другим ребенком. Веди себя задорно, но этично.'},
      {"role": "user", "content": message}
    ],
    'history': [
      {"role": "system", "content": 'Привет, ты доктор наук по истории и готов дать студенту ответ на любой его вопрос.'},
      {"role": "user", "content": message}
    ]
  }

  try:
    # Отправка запроса к ИИ
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=topics[topic],
      max_tokens=1000
    )
    # Получение кол-ва использованных токенов
    # tokens_used = completion.usage.total_tokens

    # Получение текста ответа от ИИ
    answer = completion.choices[0].message.content
  # В случае ошибки при связи с сервером
  except Exception as e:
    logger.error(f'Error while getting GPT answer: {e}')
    answer = "🤯 Неполадки с нейромозгом...\n\nПопробуй ещё раз позже!"

  return answer


