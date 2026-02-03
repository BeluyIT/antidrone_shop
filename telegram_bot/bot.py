#!/usr/bin/env python3
"""
Minimal ANTIDRONE Telegram bot for connectivity checks.
"""
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from config import BOT_TOKEN, LOG_FILE

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    payload = " ".join(context.args).strip()
    text = "Бот працює ✅"
    if payload:
        text += f"\nPayload: {payload}"
    if update.message:
        await update.message.reply_text(text)
    elif update.effective_chat:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


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
    application.add_handler(MessageHandler(filters.ALL, log_update), group=1)
    application.add_error_handler(error_handler)

    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
