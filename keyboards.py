from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == 'ru':
        builder.row(InlineKeyboardButton(text="🛍 Ассортимент", callback_data="menu_products"))
        builder.row(InlineKeyboardButton(text="🛒 Корзина", callback_data="menu_cart"))
        builder.row(InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile"))
        builder.row(InlineKeyboardButton(text="❓ Помощь", callback_data="menu_help"))
    else:
        builder.row(InlineKeyboardButton(text="🛍 Products", callback_data="menu_products"))
        builder.row(InlineKeyboardButton(text="🛒 Cart", callback_data="menu_cart"))
        builder.row(InlineKeyboardButton(text="👤 Profile", callback_data="menu_profile"))
        builder.row(InlineKeyboardButton(text="❓ Help", callback_data="menu_help"))
    return builder.as_markup()

def products_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == 'ru':
        builder.row(InlineKeyboardButton(text="START - Базовая автоматизация", callback_data="product_start"))
        builder.row(InlineKeyboardButton(text="BUSINESS - Привлечение клиентов", callback_data="product_business"))
        builder.row(InlineKeyboardButton(text="PREMIUM - Максимальная автоматизация", callback_data="product_premium"))
        builder.row(InlineKeyboardButton(text="◀ Назад", callback_data="menu_main"))
    else:
        builder.row(InlineKeyboardButton(text="START - Basic automation", callback_data="product_start"))
        builder.row(InlineKeyboardButton(text="BUSINESS - Client acquisition", callback_data="product_business"))
        builder.row(InlineKeyboardButton(text="PREMIUM - Maximum automation", callback_data="product_premium"))
        builder.row(InlineKeyboardButton(text="◀ Back", callback_data="menu_main"))
    return builder.as_markup()

def product_detail_keyboard(tariff: str, language: str, in_cart: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == 'ru':
        if not in_cart:
            builder.row(InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_to_cart_{tariff}"))
        else:
            builder.row(InlineKeyboardButton(text="✅ Уже в корзине (добавить ещё)", callback_data=f"add_to_cart_{tariff}"))
        builder.row(InlineKeyboardButton(text="◀ К списку товаров", callback_data="menu_products"))
    else:
        if not in_cart:
            builder.row(InlineKeyboardButton(text="➕ Add to cart", callback_data=f"add_to_cart_{tariff}"))
        else:
            builder.row(InlineKeyboardButton(text="✅ Already in cart (add more)", callback_data=f"add_to_cart_{tariff}"))
        builder.row(InlineKeyboardButton(text="◀ Back to products", callback_data="menu_products"))
    return builder.as_markup()

def cart_keyboard(language: str, items: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for tariff, quantity in items:
        builder.row(InlineKeyboardButton(
            text=f"❌ {tariff.upper()} (x{quantity})",
            callback_data=f"remove_from_cart_{tariff}"
        ))
    builder.row(InlineKeyboardButton(
        text="🗑 Очистить корзину" if language == 'ru' else "🗑 Clear cart",
        callback_data="cart_clear"
    ))
    builder.row(InlineKeyboardButton(
        text="💳 Оформить заказ" if language == 'ru' else "💳 Checkout",
        callback_data="cart_checkout"
    ))
    builder.row(InlineKeyboardButton(
        text="◀ Главное меню" if language == 'ru' else "◀ Main menu",
        callback_data="menu_main"
    ))
    return builder.as_markup()

def profile_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == 'ru':
        builder.row(InlineKeyboardButton(text="🌐 Сменить язык", callback_data="profile_change_lang"))
        builder.row(InlineKeyboardButton(text="🗑 Удалить профиль", callback_data="profile_delete_confirm"))
        builder.row(InlineKeyboardButton(text="📋 Мои заказы", callback_data="profile_orders"))
        builder.row(InlineKeyboardButton(text="◀ Главное меню", callback_data="menu_main"))
    else:
        builder.row(InlineKeyboardButton(text="🌐 Change language", callback_data="profile_change_lang"))
        builder.row(InlineKeyboardButton(text="🗑 Delete profile", callback_data="profile_delete_confirm"))
        builder.row(InlineKeyboardButton(text="📋 My orders", callback_data="profile_orders"))
        builder.row(InlineKeyboardButton(text="◀ Main menu", callback_data="menu_main"))
    return builder.as_markup()

def language_choice_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Русский 🇷🇺", callback_data="lang_ru"))
    builder.add(InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"))
    builder.adjust(1)
    return builder.as_markup()

def confirm_delete_keyboard(language: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if language == 'ru':
        builder.row(InlineKeyboardButton(text="✅ Да, удалить", callback_data="profile_delete_confirm_yes"))
        builder.row(InlineKeyboardButton(text="❌ Нет, вернуться", callback_data="profile"))
    else:
        builder.row(InlineKeyboardButton(text="✅ Yes, delete", callback_data="profile_delete_confirm_yes"))
        builder.row(InlineKeyboardButton(text="❌ No, go back", callback_data="profile"))
    return builder.as_markup()