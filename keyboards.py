from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru"))
    builder.add(InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"))
    builder.adjust(1)  # по одной кнопке в ряд
    return builder.as_markup()