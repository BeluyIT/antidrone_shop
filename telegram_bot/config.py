"""
Bot configuration settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot credentials
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ORDERS_CHAT_ID = int(os.getenv('ORDERS_CHAT_ID', '0'))

# Contact info
MANAGER_USERNAME = os.getenv('MANAGER_USERNAME', '')
SITE_URL = os.getenv('SITE_URL', '')
TELEGRAM_CHANNEL = os.getenv('TELEGRAM_CHANNEL', '')

# Payment details
PAYMENT_DETAILS = {
    'privat': {
        'name': 'ПриватБанк',
        'card': '1234 5678 9012 3456',
        'holder': 'Іванов І.І.',
    },
    'pumb': {
        'name': 'ПУМБ',
        'card': '2345 6789 0123 4567',
        'holder': 'Іванов І.І.',
    },
    'alfa': {
        'name': 'A-Bank',
        'card': '3456 7890 1234 5678',
        'holder': 'Іванов І.І.',
    },
    'fop': {
        'name': 'ФОП (безготівковий розрахунок)',
        'details': {
            'name': 'ФОП Іванов Іван Іванович',
            'edrpou': '1234567890',
            'mfo': '305299',
            'account': 'UA123456789012345678901234567',
            'bank': 'АТ КБ "ПриватБанк"',
        }
    }
}

# Logging
LOG_FILE = 'telegram_bot/orders.log'
