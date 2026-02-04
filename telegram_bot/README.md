# ANTIDRONE Telegram Bot

Telegram бот для приймання замовлень з сайту ANTIDRONE.CC.

## Можливості

- Приймання замовлень через deep link з сайту
- Збір даних клієнта (ПІБ, телефон, місто)
- Вибір способу оплати (ПриватБанк, ПУМБ, Альфа-Банк, ФОП)
- Приймання скріншотів оплати
- Надсилання замовлень в групу менеджерів
- Підтвердження/відхилення замовлень
- Надсилання ТТН клієнтам

## Встановлення

### 1. Створіть віртуальне середовище

```bash
cd telegram_bot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows
```

### 2. Встановіть залежності

```bash
pip install -r requirements.txt
```

### 3. Налаштуйте змінні середовища

```bash
cp .env.example .env
```

Відредагуйте `.env`:

```env
BOT_TOKEN=your_bot_token_here
ORDERS_CHAT_ID=-1001234567890
```

### 4. Запустіть бота

```bash
python bot.py
```

## Інтеграція з сайтом

### Оновлення cart.js

У файлі `static/js/cart.js` оновіть функцію `checkoutToTelegram()`:

```javascript
window.checkoutToTelegram = (event) => {
    if (event) event.preventDefault();

    const cart = getCart();
    const items = Object.values(cart.items || {});

    if (!items.length) {
        alert('Кошик порожній!');
        return false;
    }

    // Prepare data for bot
    const orderData = items.map(item => ({
        id: item.id,
        name: item.name,
        sku: item.sku || '',
        price: Number(item.price) || 0,
        qty: Number(item.qty) || 1,
    }));

    // Encode to base64 for deep link
    const encoded = btoa(JSON.stringify(orderData))
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

    // Open Telegram bot with order data
    const botUsername = 'antidrone_order_bot'; // Замініть на username вашого бота
    window.open(`https://t.me/${botUsername}?start=${encoded}`, '_blank');

    return false;
};
```

## Структура проєкту

```
telegram_bot/
├── bot.py           # Головний файл запуску
├── config.py        # Конфігурація (токени, реквізити)
├── handlers.py      # Обробники команд та повідомлень
├── keyboards.py     # Клавіатури та кнопки
├── states.py        # FSM стани та сесії користувачів
├── requirements.txt # Залежності Python
├── .env.example     # Приклад змінних середовища
├── orders.log       # Лог замовлень (створюється автоматично)
└── README.md        # Документація
```

## Команди бота

- `/start` - Початок роботи / головне меню
- `/start <order_data>` - Оформлення замовлення (deep link)

## Flow замовлення

```
1. Клієнт на сайті → Кошик → "Оформити замовлення"
   ↓
2. Відкривається Telegram бот з deep link
   ↓
3. Бот показує товари, просить дані:
   - Ім'я
   - Прізвище
   - Телефон (+380...)
   - Місто + відділення НП
   ↓
4. Клієнт обирає спосіб оплати
   ↓
5. Бот показує реквізити
   ↓
6. Клієнт надсилає скрін оплати
   ↓
7. Замовлення надходить в групу менеджерів
   ↓
8. Менеджер натискає:
   - [✅ Підтвердити] → клієнту: "Оплата підтверджена!"
   - [❌ Відхилити] → клієнту: "Потрібне уточнення"
   - [📦 ТТН] → вводить ТТН → клієнту: "📦 ТТН: 12345678901234"
```

## Налаштування реквізитів

Відредагуйте `config.py`:

```python
PAYMENT_DETAILS = {
    'privat': {
        'name': 'ПриватБанк',
        'card': '1234 5678 9012 3456',
        'holder': 'Ваше Ім'я',
    },
    # ...
}
```

## Логування

Всі замовлення логуються в `orders.log`:

```
2024-01-15 14:30:22 - Order #1001 sent to group. User: 123456789
```

## Production

Для production рекомендується:

1. **Systemd service** (Linux):

```ini
# /etc/systemd/system/antidrone-bot.service
[Unit]
Description=ANTIDRONE Telegram Bot
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/telegram_bot
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable antidrone-bot
sudo systemctl start antidrone-bot
```

2. **Docker**:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

## Підтримка

- Менеджер: @DoubleVasya
- Сайт: https://new-birth.xyz
- Канал: @antidrone_ukraine
