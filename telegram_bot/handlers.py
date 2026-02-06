"""
Message and callback handlers for the bot.
"""
import base64
import json
import logging
import re
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from config import (
    ORDERS_CHAT_ID, MANAGER_USERNAME, SITE_URL,
    TELEGRAM_CHANNEL, PAYMENT_DETAILS
)
from states import (
    OrderState, get_user_data, clear_user_data
)
from keyboards import (
    get_start_keyboard, get_start_inline_keyboard,
    get_confirmation_keyboard, get_payment_keyboard,
    get_manager_keyboard, get_cancel_keyboard, get_skip_keyboard
)

logger = logging.getLogger(__name__)

# ConversationHandler states
WAITING_PAYMENT_PROOF = 1

# Order counter (in production use database)
ORDER_COUNTER_START = 1000
order_counter = ORDER_COUNTER_START

MENU_NEW_ORDER = "📦 Нове замовлення"
MENU_CONTACT_MANAGER = "💬 Зв'язок з менеджером"
MENU_CATALOG = "🌐 Каталог"
MENU_CHANNEL = "📱 Telegram канал"


def get_next_order_id() -> int:
    """Generate next order ID."""
    global order_counter
    order_counter += 1
    return order_counter


def validate_phone(phone: str) -> str | None:
    """
    Validate and normalize Ukrainian phone number.
    Returns normalized phone or None if invalid.
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)

    # Check various formats
    patterns = [
        r'^\+380\d{9}$',      # +380XXXXXXXXX
        r'^380\d{9}$',         # 380XXXXXXXXX
        r'^0\d{9}$',           # 0XXXXXXXXX
    ]

    for pattern in patterns:
        if re.match(pattern, cleaned):
            # Normalize to +380 format
            if cleaned.startswith('+380'):
                return cleaned
            elif cleaned.startswith('380'):
                return '+' + cleaned
            elif cleaned.startswith('0'):
                return '+38' + cleaned
    return None


def parse_deep_link(start_param: str) -> list | None:
    """Parse order data from deep link parameter."""
    try:
        # Decode base64
        decoded = base64.urlsafe_b64decode(start_param + '==').decode('utf-8')
        data = json.loads(decoded)
        if isinstance(data, list) and len(data) > 0:
            return data
        return None
    except Exception as e:
        logger.error(f"Failed to parse deep link: {e}")
        return None


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    user_data = get_user_data(user.id)

    # Check for deep link with order data
    if context.args:
        start_param = context.args[0]
        items = parse_deep_link(start_param)

        if items:
            user_data.reset()
            user_data.set_items_from_data(items)
            user_data.state = OrderState.WAITING_FIRST_NAME

            items_text = user_data.get_items_text()
            await update.message.reply_text(
                f"🛒 *Ваше замовлення:*\n\n"
                f"{items_text}\n\n"
                f"💰 *Загальна сума:* {user_data.total:,.0f} грн\n\n"
                f"Для оформлення замовлення, будь ласка, введіть ваше *ім'я*:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_cancel_keyboard()
            )
            return

    # Regular start - show welcome message
    user_data.reset()
    await update.message.reply_text(
        f"👋 Вітаємо, *{user.first_name}*!\n\n"
        f"Я бот магазину *ANTIDRONE.CC* — професійні системи протидії БПЛА.\n\n"
        f"🔹 Щоб оформити замовлення, перейдіть на сайт, додайте товари в кошик "
        f"і натисніть «Оформити замовлення».\n\n"
        f"🔹 Або зв'яжіться з менеджером напряму: {MANAGER_USERNAME}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_start_keyboard()
    )
    await update.message.reply_text(
        "Оберіть дію:",
        reply_markup=get_start_inline_keyboard()
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages based on current state."""
    user = update.effective_user
    user_data = get_user_data(user.id)
    text = update.message.text.strip()

    # Handle menu buttons
    if text == MENU_NEW_ORDER:
        await update.message.reply_text(
            f"🛒 Щоб оформити замовлення:\n\n"
            f"1️⃣ Перейдіть на сайт {SITE_URL}\n"
            f"2️⃣ Додайте товари в кошик\n"
            f"3️⃣ Натисніть «Оформити замовлення»\n\n"
            f"Бот автоматично отримає ваше замовлення!",
            reply_markup=get_start_inline_keyboard()
        )
        return

    if text == MENU_CONTACT_MANAGER:
        await update.message.reply_text(
            f"📞 Наш менеджер: {MANAGER_USERNAME}\n\n"
            f"Напишіть йому напряму для консультації або уточнення деталей замовлення."
        )
        return

    if text == MENU_CATALOG:
        await update.message.reply_text(
            f"🌐 Перейти до каталогу:\n{SITE_URL}"
        )
        return

    if text == MENU_CHANNEL:
        await update.message.reply_text(
            f"📱 Наш Telegram канал: {TELEGRAM_CHANNEL}\n\n"
            f"Підписуйтесь, щоб бути в курсі новинок!"
        )
        return

    # Handle order flow states
    if user_data.state == OrderState.WAITING_FIRST_NAME:
        if len(text) < 2:
            await update.message.reply_text("❌ Ім'я занадто коротке. Введіть ваше ім'я:")
            return

        user_data.first_name = text
        user_data.state = OrderState.WAITING_LAST_NAME
        await update.message.reply_text(
            f"✅ Ім'я: *{text}*\n\nТепер введіть ваше *прізвище*:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_cancel_keyboard()
        )
        return

    if user_data.state == OrderState.WAITING_LAST_NAME:
        if len(text) < 2:
            await update.message.reply_text("❌ Прізвище занадто коротке. Введіть ваше прізвище:")
            return

        user_data.last_name = text
        user_data.state = OrderState.WAITING_PHONE
        await update.message.reply_text(
            f"✅ Прізвище: *{text}*\n\n"
            f"Введіть ваш *номер телефону* у форматі +380XXXXXXXXX:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_cancel_keyboard()
        )
        return

    if user_data.state == OrderState.WAITING_PHONE:
        normalized_phone = validate_phone(text)
        if not normalized_phone:
            await update.message.reply_text(
                "❌ Невірний формат номера.\n\n"
                "Введіть номер у форматі:\n"
                "• +380XXXXXXXXX\n"
                "• 380XXXXXXXXX\n"
                "• 0XXXXXXXXX"
            )
            return

        user_data.phone = normalized_phone
        user_data.state = OrderState.WAITING_CITY
        await update.message.reply_text(
            f"✅ Телефон: *{normalized_phone}*\n\n"
            f"Введіть *місто* та *відділення Нової Пошти* для доставки:\n"
            f"_(наприклад: Київ, відділення №25)_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_cancel_keyboard()
        )
        return

    if user_data.state == OrderState.WAITING_CITY:
        if len(text) < 3:
            await update.message.reply_text("❌ Вкажіть місто та відділення НП:")
            return

        user_data.city = text
        user_data.state = OrderState.WAITING_CONFIRMATION

        summary = user_data.get_summary()
        await update.message.reply_text(
            f"📋 *Перевірте дані замовлення:*\n\n{summary}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_confirmation_keyboard()
        )
        return

    if user_data.state == OrderState.WAITING_TTN:
        # Manager entering TTN
        ttn = text.strip()
        if not re.match(r'^\d{14}$', ttn):
            await update.message.reply_text(
                "❌ Невірний формат ТТН. Введіть 14 цифр:"
            )
            return

        # Get client user_id from context
        client_user_id = context.user_data.get('ttn_client_id')
        order_id = context.user_data.get('ttn_order_id')

        if client_user_id:
            try:
                await context.bot.send_message(
                    chat_id=client_user_id,
                    text=f"📦 *Ваше замовлення #{order_id} відправлено!*\n\n"
                         f"ТТН Нової Пошти: `{ttn}`\n\n"
                         f"Відстежити посилку:\n"
                         f"https://novaposhta.ua/tracking/?cargo_number={ttn}",
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text(f"✅ ТТН {ttn} надіслано клієнту!")
            except Exception as e:
                logger.error(f"Failed to send TTN to client: {e}")
                await update.message.reply_text(f"⚠️ Не вдалося надіслати клієнту. ТТН: {ttn}")

        user_data.state = OrderState.COMPLETED
        context.user_data.clear()
        return

    # Unknown state - reset
    await update.message.reply_text(
        "Оберіть дію з меню або оформіть замовлення на сайті.",
        reply_markup=get_start_keyboard()
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline buttons."""
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_data = get_user_data(user.id)
    data = query.data

    # Cancel order
    if data == "cancel_order":
        clear_user_data(user.id)
        await query.edit_message_text(
            "❌ Замовлення скасовано.\n\n"
            "Ви можете оформити нове замовлення на сайті."
        )
        return

    # Order confirmation
    if data == "confirm_yes":
        user_data.state = OrderState.WAITING_PAYMENT_METHOD
        await query.edit_message_text(
            f"📋 *Замовлення підтверджено!*\n\n"
            f"💰 Сума до оплати: *{user_data.total:,.0f} грн*\n\n"
            f"Оберіть спосіб оплати:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_payment_keyboard()
        )
        return

    if data == "confirm_no":
        user_data.state = OrderState.WAITING_FIRST_NAME
        await query.edit_message_text(
            "🔄 Давайте введемо дані заново.\n\n"
            "Введіть ваше *ім'я*:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_cancel_keyboard()
        )
        return

    # Payment method selection
    if data.startswith("pay_"):
        method = data.replace("pay_", "")
        user_data.payment_method = method
        user_data.state = OrderState.WAITING_PAYMENT_PROOF

        payment = PAYMENT_DETAILS.get(method, {})

        if method == "fop":
            details = payment.get('details', {})
            text = (
                f"🏢 *Безготівковий розрахунок (ФОП)*\n\n"
                f"*Реквізити для оплати:*\n"
                f"▫️ Отримувач: {details.get('name')}\n"
                f"▫️ ЄДРПОУ: `{details.get('edrpou')}`\n"
                f"▫️ МФО: `{details.get('mfo')}`\n"
                f"▫️ Р/р: `{details.get('account')}`\n"
                f"▫️ Банк: {details.get('bank')}\n\n"
                f"💰 *Сума:* {user_data.total:,.0f} грн\n"
                f"📝 *Призначення:* Оплата за товар\n\n"
                f"Після оплати надішліть скріншот платіжки 👇"
            )
        else:
            text = (
                f"💳 *{payment.get('name')}*\n\n"
                f"*Реквізити для оплати:*\n"
                f"▫️ Картка: `{payment.get('card')}`\n"
                f"▫️ Отримувач: {payment.get('holder')}\n\n"
                f"💰 *Сума:* {user_data.total:,.0f} грн\n\n"
                f"Після оплати надішліть скріншот чеку 👇"
            )

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_skip_keyboard()
        )
        return

    # Skip photo
    if data == "skip_photo":
        await send_order_to_group(update, context, user_data, photo_id=None)
        return

    # Manager actions
    if data.startswith("mgr_"):
        await handle_manager_action(update, context, data)
        return


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle payment proof photo."""
    user = update.effective_user
    user_data = get_user_data(user.id)

    if user_data.state != OrderState.WAITING_PAYMENT_PROOF:
        return

    # Get photo file_id
    photo = update.message.photo[-1]  # Largest size
    photo_id = photo.file_id

    await send_order_to_group(update, context, user_data, photo_id)


async def send_order_to_group(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_data,
    photo_id: str | None
):
    """Send completed order to managers group."""
    user = update.effective_user
    order_id = get_next_order_id()
    user_data.order_id = order_id
    user_data.payment_proof_id = photo_id

    payment = PAYMENT_DETAILS.get(user_data.payment_method, {})
    payment_name = payment.get('name', user_data.payment_method)

    now = datetime.now().strftime("%d.%m.%Y о %H:%M")

    order_text = (
        f"🔔 *НОВЕ ЗАМОВЛЕННЯ #{order_id}*\n\n"
        f"👤 *Клієнт:*\n"
        f"├ Ім'я: {user_data.first_name} {user_data.last_name}\n"
        f"├ Телефон: {user_data.phone}\n"
        f"├ Місто: {user_data.city}\n"
        f"└ Telegram: @{user.username or 'немає'} (ID: {user.id})\n\n"
        f"🛒 *Товари:*\n{user_data.get_items_text()}\n\n"
        f"💰 *Сума:* {user_data.total:,.0f} грн\n"
        f"💳 *Оплата:* {payment_name}\n"
        f"📸 *Скрін:* {'є' if photo_id else 'немає'}\n\n"
        f"⏰ *Дата:* {now}"
    )

    manager_keyboard = get_manager_keyboard(order_id, user.id)

    try:
        if photo_id:
            msg = await context.bot.send_photo(
                chat_id=ORDERS_CHAT_ID,
                photo=photo_id,
                caption=order_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=manager_keyboard
            )
        else:
            msg = await context.bot.send_message(
                chat_id=ORDERS_CHAT_ID,
                text=order_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=manager_keyboard
            )

        user_data.message_id = msg.message_id
        logger.info(f"Order #{order_id} sent to group. User: {user.id}")

    except Exception as e:
        logger.error(f"Failed to send order to group: {e}")

    # Confirm to user
    user_data.state = OrderState.COMPLETED

    if update.message:
        await update.message.reply_text(
            f"✅ *Замовлення #{order_id} прийнято!*\n\n"
            f"Менеджер перевірить оплату і зв'яжеться з вами.\n\n"
            f"📞 Для термінових питань: {MANAGER_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_start_keyboard()
        )
    else:
        await update.callback_query.edit_message_text(
            f"✅ *Замовлення #{order_id} прийнято!*\n\n"
            f"Менеджер перевірить оплату і зв'яжеться з вами.\n\n"
            f"📞 Для термінових питань: {MANAGER_USERNAME}",
            parse_mode=ParseMode.MARKDOWN
        )

    clear_user_data(user.id)


async def handle_manager_action(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    data: str
):
    """Handle manager actions on orders."""
    query = update.callback_query
    parts = data.split('_')

    if len(parts) < 4:
        return

    action = parts[1]  # confirm, reject, ttn
    order_id = int(parts[2])
    client_user_id = int(parts[3])

    if action == "confirm":
        try:
            await context.bot.send_message(
                chat_id=client_user_id,
                text=f"✅ *Оплата замовлення #{order_id} підтверджена!*\n\n"
                     f"Очікуйте ТТН для відстеження посилки.\n"
                     f"Дякуємо за покупку! 🎉",
                parse_mode=ParseMode.MARKDOWN
            )
            await query.answer("✅ Клієнта повідомлено про підтвердження!")

            # Update message in group
            new_text = query.message.text or query.message.caption or ""
            new_text += "\n\n✅ *ПІДТВЕРДЖЕНО*"

            if query.message.photo:
                await query.edit_message_caption(
                    caption=new_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_manager_keyboard(order_id, client_user_id)
                )
            else:
                await query.edit_message_text(
                    text=new_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_manager_keyboard(order_id, client_user_id)
                )

        except Exception as e:
            logger.error(f"Failed to notify client: {e}")
            await query.answer("⚠️ Не вдалося повідомити клієнта", show_alert=True)

    elif action == "reject":
        try:
            await context.bot.send_message(
                chat_id=client_user_id,
                text=f"⚠️ *Замовлення #{order_id} потребує уточнення*\n\n"
                     f"Менеджер зв'яжеться з вами найближчим часом.\n"
                     f"Або напишіть самі: {MANAGER_USERNAME}",
                parse_mode=ParseMode.MARKDOWN
            )
            await query.answer("❌ Клієнта повідомлено!")

            new_text = query.message.text or query.message.caption or ""
            new_text += "\n\n❌ *ПОТРЕБУЄ УТОЧНЕННЯ*"

            if query.message.photo:
                await query.edit_message_caption(
                    caption=new_text,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await query.edit_message_text(
                    text=new_text,
                    parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            logger.error(f"Failed to notify client: {e}")
            await query.answer("⚠️ Не вдалося повідомити клієнта", show_alert=True)

    elif action == "ttn":
        # Store client info for TTN input
        manager_data = get_user_data(query.from_user.id)
        manager_data.state = OrderState.WAITING_TTN
        context.user_data['ttn_client_id'] = client_user_id
        context.user_data['ttn_order_id'] = order_id

        await query.answer()
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"📦 Введіть номер ТТН для замовлення #{order_id}:\n"
                 f"_(14 цифр)_",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_payment_proof(update, context):
    """Handle payment proof photo from user."""
    if not update.message.photo:
        await update.message.reply_text("Надішліть фото чека.")
        return WAITING_PAYMENT_PROOF

    # Очищаємо від HTML тегів
    def clean_html(text):
        return re.sub(r'<[^>]+>', '', str(text))

    name = clean_html(context.user_data.get('name', ''))
    surname = clean_html(context.user_data.get('surname', ''))
    phone = clean_html(context.user_data.get('phone', ''))
    city = clean_html(context.user_data.get('city', ''))
    branch = clean_html(context.user_data.get('branch', ''))
    payment = clean_html(context.user_data.get('payment_method', ''))

    msg = (
        "🔔 НОВЕ ЗАМОВЛЕННЯ\n\n"
        f"👤 {name} {surname}\n"
        f"📱 {phone}\n"
        f"📍 {city}, НП №{branch}\n\n"
        "🛒 Товари:\n"
    )

    for i, item in enumerate(context.user_data['order_items'], 1):
        item_name = clean_html(item['name'])
        item_sku = clean_html(item['sku'])
        msg += f"{i}. {item_name} ({item_sku})\n   {item['price']}грн × {item['quantity']} = {item['price']*item['quantity']}грн\n"

    msg += f"\n💰 {context.user_data['order_total']} грн\n💳 {payment}"

    await context.bot.send_message(chat_id=-1003809201269, text=msg)
    await context.bot.send_photo(chat_id=-1003809201269, photo=update.message.photo[-1].file_id, caption="📸 Чек")

    await update.message.reply_text("✅ Замовлення прийнято!\n\nМенеджер зв'яжеться найближчим часом.\n\n@DoubleVasya")

    return ConversationHandler.END
