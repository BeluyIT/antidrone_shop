#!/usr/bin/env python3
"""Minimal ANTIDRONE Telegram bot for /start + order intake flow."""
import base64
import json
import logging
from typing import Any

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, LOG_FILE, ORDERS_CHAT_ID, MANAGER_USERNAME, SITE_URL

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
    ],
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

ASK_NAME, ASK_PHONE, ASK_CITY, ASK_COMMENT = range(4)
STATE_KEY = "order_state"


def build_start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[
            KeyboardButton("📦 Нове замовлення"),
            KeyboardButton("💬 Менеджер"),
            KeyboardButton("🌐 Сайт"),
        ]],
        resize_keyboard=True,
    )


def build_site_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🌐 Перейти на сайт", url=SITE_URL)]])


def decode_payload(payload: str) -> list[dict[str, Any]] | None:
    try:
        padding = '=' * (-len(payload) % 4)
        decoded_raw = base64.urlsafe_b64decode(payload + padding).decode('utf-8')
        data = json.loads(decoded_raw)
        if isinstance(data, list) and data:
            logger.info("Decoded payload ok")
            return data
    except Exception as exc:
        logger.info("Decoded payload failed: %s", exc)
    return None


def format_items(items: list[dict[str, Any]]) -> tuple[str, int]:
    total = 0
    lines = []
    for item in items:
        name = str(item.get('name') or 'Товар')
        sku = str(item.get('sku') or '—')
        qty = int(item.get('qty') or 0)
        price = int(item.get('price') or 0)
        total += price * qty
        lines.append(f"• {name} | SKU: {sku} | x{qty} | {price} грн")
    return "\n".join(lines), total


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Start handler called")
    payload = " ".join(context.args).strip() if context.args else ""
    base_text = "Бот працює ✅"

    if payload:
        items = decode_payload(payload)
        if items:
            context.user_data.clear()
            context.user_data["order_items"] = items
            items_text, total = format_items(items)
            context.user_data["order_total"] = total
            context.user_data["order_payload_raw"] = payload
            context.user_data["order_active"] = True
            context.user_data[STATE_KEY] = ASK_NAME

            text = (
                f"{base_text}\n"
                f"Payload: {payload}\n\n"
                f"Отримано замовлення:\n{items_text}\n\n"
                f"Разом: {total} грн\n\n"
                f"Введіть ваше ім'я:"
            )
            await update.message.reply_text(text)
            return

        text = f"{base_text}\nPayload: {payload}\nНе вдалося розкодувати payload."
        await update.message.reply_text(text, reply_markup=build_start_keyboard())
        return

    await update.message.reply_text(base_text, reply_markup=build_start_keyboard())
    return


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get("order_active"):
        return
    text = (update.message.text or "").strip()
    if text == "📦 Нове замовлення":
        await update.message.reply_text(
            f"Щоб оформити замовлення:\n"
            f"1. Перейдіть на сайт {SITE_URL}\n"
            f"2. Додайте товари в кошик\n"
            f"3. Натисніть «Оформити замовлення»",
            reply_markup=build_site_keyboard(),
        )
        return
    if text == "💬 Менеджер":
        await update.message.reply_text(f"Менеджер: {MANAGER_USERNAME}")
        return
    if text == "🌐 Сайт":
        await update.message.reply_text("Сайт:", reply_markup=build_site_keyboard())


async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = (update.message.text or "").strip()
    if len(name) < 2:
        await update.message.reply_text("Ім'я занадто коротке. Введіть ім'я:")
        return
    context.user_data["name"] = name
    context.user_data[STATE_KEY] = ASK_PHONE
    await update.message.reply_text("Введіть телефон:")
    return


async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone = (update.message.text or "").strip()
    if len(phone) < 5:
        await update.message.reply_text("Невірний телефон. Введіть телефон:")
        return
    context.user_data["phone"] = phone
    context.user_data[STATE_KEY] = ASK_CITY
    await update.message.reply_text("Введіть місто та відділення НП:")
    return


async def ask_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = (update.message.text or "").strip()
    if len(city) < 2:
        await update.message.reply_text("Вкажіть місто та відділення НП:")
        return
    context.user_data["city"] = city
    context.user_data[STATE_KEY] = ASK_COMMENT
    await update.message.reply_text("Коментар (або «-»):")
    return


async def ask_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    comment = (update.message.text or "").strip()
    context.user_data["comment"] = comment

    items = context.user_data.get("order_items", [])
    items_text, total = format_items(items) if items else ("—", 0)
    name = context.user_data.get("name", "—")
    phone = context.user_data.get("phone", "—")
    city = context.user_data.get("city", "—")

    order_text = (
        "Нове замовлення\n\n"
        f"Клієнт: {name}\n"
        f"Телефон: {phone}\n"
        f"Місто/НП: {city}\n"
        f"Коментар: {comment or '-'}\n\n"
        f"Позиції:\n{items_text}\n\n"
        f"Разом: {total} грн"
    )

    await context.bot.send_message(chat_id=ORDERS_CHAT_ID, text=order_text)
    await update.message.reply_text("Замовлення прийнято ✅ менеджер зв'яжеться")

    context.user_data.clear()
    return


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.user_data.get(STATE_KEY)
    if state == ASK_NAME:
        await ask_name(update, context)
        return
    if state == ASK_PHONE:
        await ask_phone(update, context)
        return
    if state == ASK_CITY:
        await ask_city(update, context)
        return
    if state == ASK_COMMENT:
        await ask_comment(update, context)
        return
    await menu_handler(update, context)


async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Update: %s", update.to_dict())


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Error while handling update %s", update, exc_info=context.error)


async def post_init(application) -> None:
    await application.bot.delete_webhook(drop_pending_updates=True)


def main() -> None:
    logger.info("Starting ANTIDRONE Order Bot (debug baseline)...")

    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, log_update), group=1)
    application.add_error_handler(error_handler)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
