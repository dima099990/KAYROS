from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import language_keyboard
from openai_client import get_ai_response
import database as db

router = Router()

class ChooseLanguage(StatesGroup):
    waiting_for_language = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = await db.get_user_language(user_id)

    if language:
        # Язык уже выбран
        welcome_text = "С возвращением! Я готов помочь с автоматизацией бизнеса. Напиши свой вопрос." if language == "ru" else "Welcome back! I'm ready to help with business automation. Ask your question."
        await message.answer(welcome_text)
    else:
        # Новый пользователь
        await state.set_state(ChooseLanguage.waiting_for_language)
        await message.answer(
            "👋 Добро пожаловать! Выберите язык / Welcome! Choose your language:",
            reply_markup=language_keyboard()
        )

@router.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]  # 'ru' или 'en'

    # Сохраняем пользователя в БД
    await db.create_user(user_id, lang)

    # Подтверждение
    confirm_text = f"Вы выбрали русский язык. Теперь вы можете задать вопрос." if lang == "ru" else f"You selected English. Now you can ask a question."
    await callback.message.edit_text(confirm_text)

    await state.clear()
    await callback.answer()

@router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text

    # Получаем язык пользователя из БД
    language = await db.get_user_language(user_id)
    if not language:
        await message.answer("Пожалуйста, начните с команды /start, чтобы выбрать язык.\nPlease start with /start to choose language.")
        return

    # Сохраняем сообщение пользователя
    await db.save_message(user_id, text, role="user")

    # Отправляем "печатает..."
    await message.bot.send_chat_action(chat_id=user_id, action="typing")

    # Получаем ответ от AI
    response = await get_ai_response(text, language)

    # Сохраняем ответ бота
    await db.save_message(user_id, response, role="assistant")

    # Отправляем ответ
    await message.answer(response)