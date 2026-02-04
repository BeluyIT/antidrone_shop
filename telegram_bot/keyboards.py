"""
Keyboard layouts for the bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from config import MANAGER_USERNAME, SITE_URL, TELEGRAM_CHANNEL


def get_start_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard."""
    keyboard = [
        [KeyboardButton("📦 Нове замовлення")],
        [KeyboardButton("💬 Зв'язок з менеджером")],
        [KeyboardButton("🌐 Каталог"), KeyboardButton("📱 Telegram канал")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_start_inline_keyboard() -> InlineKeyboardMarkup:
    """Start message inline buttons."""
    keyboard = [
        [InlineKeyboardButton("🌐 Перейти до каталогу", url=SITE_URL)],
        [InlineKeyboardButton("💬 Написати менеджеру", url=f"https://t.me/{MANAGER_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("📱 Наш канал", url=f"https://t.me/{TELEGRAM_CHANNEL.replace('@', '')}")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Order confirmation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Все вірно", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Змінити", callback_data="confirm_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_keyboard() -> ReplyKeyboardMarkup:
    """Payment method selection keyboard."""
    keyboard = [
        [KeyboardButton("💳 ПриватБанк"), KeyboardButton("💳 ПУМБ")],
        [KeyboardButton("💳 A-Bank"), KeyboardButton("🏢 ФОП")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_manager_keyboard(order_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Manager action keyboard for orders chat."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Підтвердити", callback_data=f"mgr_confirm_{order_id}_{user_id}"),
            InlineKeyboardButton("❌ Відхилити", callback_data=f"mgr_reject_{order_id}_{user_id}"),
        ],
        [
            InlineKeyboardButton("📦 Надіслати ТТН", callback_data=f"mgr_ttn_{order_id}_{user_id}"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Cancel action keyboard."""
    keyboard = [
        [InlineKeyboardButton("❌ Скасувати замовлення", callback_data="cancel_order")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard() -> InlineKeyboardMarkup:
    """Skip photo keyboard."""
    keyboard = [
        [InlineKeyboardButton("⏭️ Надіслати без скріну", callback_data="skip_photo")]
    ]
    return InlineKeyboardMarkup(keyboard)
