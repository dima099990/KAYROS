from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import (
    main_menu_keyboard, products_keyboard, product_detail_keyboard, cart_keyboard,
    profile_keyboard, language_choice_keyboard, confirm_delete_keyboard
)
from openai_client import get_ai_response
import database as db

router = Router()

# Состояния FSM
class DialogStates(StatesGroup):
    main_menu = State()
    in_tariffs = State()
    in_profile = State()
    waiting_confirm_delete = State()
    viewing_cart = State()

# Данные тарифов
TARIFFS = {
    'start': {
        'ru': {'name': 'START', 'description': 'Базовая автоматизация бизнеса\n\n✔ Приём заявок 24/7\n✔ Мгновенные автоответы клиентам\n✔ Сбор и структурирование клиентской базы\n✔ Базовая автоворонка продаж', 'price': 100},
        'en': {'name': 'START', 'description': 'Basic business automation\n\n✔ 24/7 lead capture\n✔ Instant auto-replies\n✔ Customer database structuring\n✔ Basic sales funnel', 'price': 100}
    },
    'business': {
        'ru': {'name': 'BUSINESS', 'description': 'Система привлечения и удержания клиентов\n\n✔ Всё из START\n✔ Система прогрева клиентов\n✔ Автоматические рассылки\n✔ Возврат старых клиентов\n✔ Настройка рекламного трафика', 'price': 250},
        'en': {'name': 'BUSINESS', 'description': 'Client acquisition & retention system\n\n✔ All from START\n✔ Lead nurturing\n✔ Automated newsletters\n✔ Returning customers\n✔ Ad traffic setup', 'price': 250}
    },
    'premium': {
        'ru': {'name': 'PREMIUM', 'description': 'Максимальная автоматизация\n\n✔ Всё из START и BUSINESS\n✔ Полная интеграция бизнес-процессов\n✔ Онлайн-оплата через API\n✔ Интеграция с CRM\n✔ Индивидуальная стратегия', 'price': 500},
        'en': {'name': 'PREMIUM', 'description': 'Maximum automation\n\n✔ All from START & BUSINESS\n✔ Full business process integration\n✔ Online payments via API\n✔ CRM integration\n✔ Custom strategy', 'price': 500}
    }
}

# Вспомогательная функция для показа главного меню
async def show_main_menu(callback_or_message, language: str, edit: bool = True):
    text = "Главное меню:" if language == 'ru' else "Main menu:"
    markup = main_menu_keyboard(language)
    if isinstance(callback_or_message, CallbackQuery):
        if edit:
            await callback_or_message.message.edit_text(text, reply_markup=markup)
        else:
            await callback_or_message.message.answer(text, reply_markup=markup)
        await callback_or_message.answer()
    else:
        await callback_or_message.answer(text, reply_markup=markup)

async def show_profile(callback: CallbackQuery, language: str, edit: bool = True):
    user_id = callback.from_user.id
    orders = await db.get_user_orders(user_id)
    orders_count = len(orders)
    text = (f"👤 Профиль\n\nЯзык: {'Русский' if language == 'ru' else 'English'}\n"
            f"Заказов: {orders_count}") if language == 'ru' else (
        f"👤 Profile\n\nLanguage: {'Russian' if language == 'ru' else 'English'}\n"
        f"Orders: {orders_count}")
    markup = profile_keyboard(language)
    if edit:
        await callback.message.edit_text(text, reply_markup=markup)
    else:
        await callback.message.answer(text, reply_markup=markup)
    await callback.answer()

# Вспомогательная функция для показа деталей товара
async def show_product_detail_by_tariff(callback: CallbackQuery, tariff_key: str, language: str):
    tariff_info = TARIFFS[tariff_key][language]
    cart_items = await db.get_cart(callback.from_user.id)
    in_cart = any(item[0] == tariff_key for item in cart_items)
    text = f"*{tariff_info['name']}*\n\n{tariff_info['description']}\n\n💰 Цена: ${tariff_info['price']}"
    markup = product_detail_keyboard(tariff_key, language, in_cart)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode='Markdown')

# ---------- Команды ----------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = await db.get_user_language(user_id)
    if language:
        await show_main_menu(message, language, edit=False)
        await state.set_state(DialogStates.main_menu)
    else:
        await message.answer(
            "👋 Добро пожаловать! Выберите язык / Welcome! Choose your language:",
            reply_markup=language_choice_keyboard()
        )

@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = await db.get_user_language(user_id)
    if language:
        await show_main_menu(message, language, edit=False)
        await state.set_state(DialogStates.main_menu)
    else:
        await message.answer("Сначала используйте /start для выбора языка.")

# ---------- Выбор языка при старте ----------
@router.callback_query(F.data.startswith("lang_"))
async def process_initial_language(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split("_")[1]
    await db.create_user(user_id, lang)
    await callback.message.edit_text(
        "Язык сохранён. Открываю главное меню..." if lang == 'ru' else "Language saved. Opening main menu..."
    )
    await show_main_menu(callback, lang, edit=True)
    await state.set_state(DialogStates.main_menu)

# ---------- Смена языка ----------
@router.callback_query(F.data == "profile_change_lang")
async def change_language_start(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    text = "Выберите язык:" if language == 'ru' else "Choose language:"
    await callback.message.edit_text(text, reply_markup=language_choice_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("setlang_"))
async def process_language_change(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    new_lang = callback.data.split("_")[1]
    await db.update_user_language(user_id, new_lang)
    await callback.message.edit_text(
        "Язык обновлён!" if new_lang == 'ru' else "Language updated!"
    )
    # Возвращаемся в профиль
    await show_profile(callback, new_lang, edit=True)
    await state.set_state(DialogStates.in_profile)

# ---------- Навигация по меню ----------
@router.callback_query(F.data == "menu_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    await show_main_menu(callback, language, edit=True)
    await state.set_state(DialogStates.main_menu)

@router.callback_query(F.data == "menu_products")
async def show_products(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    text = "Выберите товар для просмотра:" if language == 'ru' else "Choose a product to view:"
    await callback.message.edit_text(text, reply_markup=products_keyboard(language))
    await callback.answer()

@router.callback_query(F.data == "menu_cart")
async def show_cart(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    cart_items = await db.get_cart(user_id)

    if not cart_items:
        text = "🛒 Корзина пуста." if language == 'ru' else "🛒 Cart is empty."
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀ Главное меню" if language == 'ru' else "◀ Main menu", callback_data="menu_main")]
        ])
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()
        return

    total = 0
    lines = []
    for tariff, quantity in cart_items:
        price = TARIFFS[tariff][language]['price']
        total += price * quantity
        lines.append(f"• {TARIFFS[tariff][language]['name']} x{quantity} = ${price * quantity}")

    summary = "\n".join(lines)
    text = (f"🛒 *Ваша корзина:*\n\n{summary}\n\n💰 *Общая сумма: ${total}*") if language == 'ru' else \
           (f"🛒 *Your cart:*\n\n{summary}\n\n💰 *Total: ${total}*")
    markup = cart_keyboard(language, cart_items)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode='Markdown')
    await callback.answer()
    await state.set_state(DialogStates.viewing_cart)

@router.callback_query(F.data == "menu_profile")
async def show_profile_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    await show_profile(callback, language, edit=True)
    await state.set_state(DialogStates.in_profile)

@router.callback_query(F.data == "menu_help")
async def show_help(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    contact_text = (
        "📞 Служба поддержки: @support_username\n"
        "Или напишите на email: support@example.com"
    ) if language == 'ru' else (
        "📞 Support: @support_username\n"
        "Or email: support@example.com"
    )
    # Возвращаем в главное меню после просмотра контактов
    markup = main_menu_keyboard(language)
    await callback.message.edit_text(contact_text, reply_markup=markup)
    await callback.answer()
# ---------- Товары и корзина ----------
@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    tariff_key = callback.data.split("_")[1]
    await show_product_detail_by_tariff(callback, tariff_key, language)

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    tariff_key = callback.data.split("_")[3]  # add_to_cart_tariff -> ['add', 'to', 'cart', 'start']
    await db.add_to_cart(user_id, tariff_key)

    tariff_info = TARIFFS[tariff_key][language]
    text = f"✅ {tariff_info['name']} добавлен в корзину!" if language == 'ru' else f"✅ {tariff_info['name']} added to cart!"
    await callback.answer(text, show_alert=False)

    # Обновляем текущее сообщение (детали товара)
    await show_product_detail_by_tariff(callback, tariff_key, language)

@router.callback_query(F.data.startswith("remove_from_cart_"))
async def remove_from_cart_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    tariff_key = callback.data.split("_")[3]  # remove_from_cart_tariff
    await db.remove_from_cart(user_id, tariff_key, remove_all=False)

    await callback.answer("Товар удалён" if language == 'ru' else "Item removed", show_alert=False)
    # Обновляем корзину
    await show_cart(callback, state)

@router.callback_query(F.data == "cart_clear")
async def clear_cart_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    await db.clear_cart(user_id)
    await callback.answer("Корзина очищена" if language == 'ru' else "Cart cleared", show_alert=False)
    await show_cart(callback, state)

@router.callback_query(F.data == "cart_checkout")
async def checkout_from_cart(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    cart_items = await db.get_cart(user_id)
    if not cart_items:
        await callback.answer("Корзина пуста" if language == 'ru' else "Cart is empty", show_alert=True)
        return

    items_for_order = []
    total = 0
    for tariff, quantity in cart_items:
        price = TARIFFS[tariff][language]['price']
        total += price * quantity
        items_for_order.append((tariff, quantity, price))

    order_id = await db.create_order(user_id, items_for_order, total)
    await db.clear_cart(user_id)

    text = (
        f"✅ *Заказ №{order_id} оформлен!*\n\n"
        f"Сумма к оплате: ${total}\n"
        f"В ближайшее время с вами свяжется менеджер для уточнения деталей."
    ) if language == 'ru' else (
        f"✅ *Order #{order_id} created!*\n\n"
        f"Total: ${total}\n"
        f"Manager will contact you shortly."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои заказы" if language == 'ru' else "📋 My orders", callback_data="profile_orders")],
        [InlineKeyboardButton(text="◀ Главное меню" if language == 'ru' else "◀ Main menu", callback_data="menu_main")]
    ])
    await callback.message.edit_text(text, reply_markup=markup, parse_mode='Markdown')
    await callback.answer()
    await state.set_state(DialogStates.main_menu)

# ---------- Профиль: заказы и удаление ----------
@router.callback_query(F.data == "profile_orders")
async def show_orders(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    orders = await db.get_user_orders(user_id)
    if not orders:
        text = "У вас пока нет заказов." if language == 'ru' else "You have no orders yet."
    else:
        lines = []
        for o in orders:
            o_id, status, total_amount, created = o
            status_text = {
                'pending': '⏳ Ожидает оплаты',
                'paid': '✅ Оплачен',
                'cancelled': '❌ Отменён'
            }.get(status, status)
            lines.append(f"#{o_id} - {status_text} (${total_amount})")
        text = "📋 *Ваши заказы:*\n\n" + "\n".join(lines) if language == 'ru' else "📋 *Your orders:*\n\n" + "\n".join(lines)
    markup = profile_keyboard(language)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode='Markdown')
    await callback.answer()

@router.callback_query(F.data == "profile_delete_confirm")
async def confirm_delete_profile(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    text = "Вы уверены, что хотите удалить свой профиль? Все данные будут безвозвратно удалены." if language == 'ru' else "Are you sure you want to delete your profile? All data will be permanently lost."
    await callback.message.edit_text(text, reply_markup=confirm_delete_keyboard(language))
    await state.set_state(DialogStates.waiting_confirm_delete)
    await callback.answer()

@router.callback_query(F.data == "profile_delete_confirm_yes")
async def delete_profile(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)  # ещё доступен до удаления
    await db.delete_user(user_id)
    await callback.message.edit_text(
        "Профиль удалён. Чтобы начать заново, отправьте /start" if language == 'ru' else "Profile deleted. To start over, send /start"
    )
    await state.clear()

@router.callback_query(F.data == "profile")
async def back_to_profile(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = await db.get_user_language(user_id)
    if language:
        await show_profile(callback, language, edit=True)
        await state.set_state(DialogStates.in_profile)
    else:
        await callback.message.edit_text("Ошибка. Начните с /start")
        await state.clear()

# ---------- Текстовые сообщения (AI) ----------
@router.message()
async def handle_text_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    language = await db.get_user_language(user_id)
    if not language:
        await message.answer("Пожалуйста, начните с команды /start, чтобы выбрать язык.\nPlease start with /start to choose language.")
        return

    await db.save_message(user_id, message.text, role="user")
    await message.bot.send_chat_action(chat_id=user_id, action="typing")
    response = await get_ai_response(message.text, language)
    await db.save_message(user_id, response, role="assistant")
    await message.answer(response)

    # Кнопка для возврата в меню
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☰ Меню" if language == 'ru' else "☰ Menu", callback_data="menu_main")]
    ])
    await message.answer("👇", reply_markup=markup)