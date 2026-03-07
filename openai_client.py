from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


##

async def get_ai_response(user_message: str, language: str) -> str:
    # Простая заглушка: возвращает эхо или шаблонный ответ
    if language == "ru":
        return f"📢 (Демо-режим) Ваш запрос: '{user_message}'. В реальности здесь будет ответ от AI."
    else:
        return f"📢 (Demo mode) Your request: '{user_message}'. In production, AI response will be here."
##

# async def get_ai_response(user_message: str, language: str) -> str:
#     """
#     Отправляет запрос в OpenAI и возвращает ответ.
#     language может быть 'ru' или 'en' — используется в system prompt.
#     """
#     system_content = (
#         "Ты — полезный ассистент, который помогает с вопросами по автоматизации бизнеса. "
#         "Отвечай вежливо и по делу."
#         if language == "ru" else
#         "You are a helpful assistant specializing in business automation. "
#         "Answer politely and to the point."
#     )
#     try:
#         response = await client.chat.completions.create(
#             model="gpt-3.5-turbo",  # или "gpt-4", если есть доступ
#             messages=[
#                 {"role": "system", "content": system_content},
#                 {"role": "user", "content": user_message}
#             ],
#             temperature=0.7,
#             max_tokens=500
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"⚠️ Ошибка при обращении к AI: {e}" if language == "ru" else f"⚠️ AI error: {e}"