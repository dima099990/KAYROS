from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import language_keyboard
from openai_client import get_ai_response

# Хранилище данных пользователей (вместо БД)
# Структура: {user_id: {'language': 'ru' or 'en', 'history': []}}
user_data = {}

router = Router()

# Состояния (используем только для первого выбора языка)
class ChooseLanguage(StatesGroup):
    waiting_for_language = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in user_data:
        # Язык уже выбран, приветствуем и предлагаем сразу писать
        lang = user_data[user_id]['language']
        welcome = "С возвращением! Я готов помочь с автоматизацией бизнеса. Напиши свой вопрос." if lang == "ru" else "Welcome back! I'm ready to help with business automation. Ask your question."
        await message.answer(welcome)
    else:
        # Новый пользователь — выбираем язык
        await state.set_state(ChooseLanguage.waiting_for_language)
        await message.answer(
            "👋 Добро пожаловать! Выберите язык / Welcome! Choose your language:",
            reply_markup=language_keyboard()
        )

@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]  # 'ru' или 'en'

    # Сохраняем язык пользователя
    user_data[user_id] = {'language': lang, 'history': []}

    # Подтверждение выбора
    confirm_text = f"Вы выбрали русский язык. Теперь вы можете задать вопрос." if lang == "ru" else f"You selected English. Now you can ask a question."
    await callback.message.edit_text(confirm_text)

    # Сбрасываем состояние (больше не ждём выбора языка)
    await state.clear()
    await callback.answer()

@router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text

    # Проверяем, выбран ли язык
    if user_id not in user_data:
        # Если язык не выбран, отправляем команду /start
        await message.answer("Пожалуйста, начните с команды /start, чтобы выбрать язык.\nPlease start with /start to choose language.")
        return

    lang = user_data[user_id]['language']
    # Отправляем "печатает..." чтобы пользователь ждал
    await message.bot.send_chat_action(chat_id=user_id, action="typing")

    # Получаем ответ от AI
    response = await get_ai_response(text, lang)

    # Отправляем ответ
    await message.answer(response)

    # Опционально сохраняем историю (здесь опустим для простоты)