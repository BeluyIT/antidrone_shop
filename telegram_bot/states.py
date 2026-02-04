"""
FSM States for order processing.
"""
from enum import IntEnum, auto


class OrderState(IntEnum):
    """States for order flow."""

    # Collecting customer info
    ASK_NAME = 0
    ASK_SURNAME = 1
    ASK_PHONE = 2
    ASK_CITY = 3
    ASK_BRANCH = 4

    # Confirmation
    CONFIRM_DATA = 5

    # Comment
    ASK_COMMENT = 6

    # Payment (for future use)
    PAYMENT_METHOD = 7
    WAITING_PAYMENT_PROOF = 8

    # Completed
    COMPLETED = 9


# Export constants for backwards compatibility
ASK_NAME = OrderState.ASK_NAME
ASK_SURNAME = OrderState.ASK_SURNAME
ASK_PHONE = OrderState.ASK_PHONE
ASK_CITY = OrderState.ASK_CITY
ASK_BRANCH = OrderState.ASK_BRANCH
CONFIRM_DATA = OrderState.CONFIRM_DATA
ASK_COMMENT = OrderState.ASK_COMMENT
PAYMENT_METHOD = OrderState.PAYMENT_METHOD
WAITING_PAYMENT_PROOF = OrderState.WAITING_PAYMENT_PROOF
COMPLETED = OrderState.COMPLETED


class UserData:
    """Store user order data."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all user data."""
        self.state = OrderState.ASK_NAME
        self.order_id = None
        self.items = []
        self.total = 0
        self.name = None
        self.surname = None
        self.phone = None
        self.city = None
        self.branch = None
        self.comment = None
        self.payment_method = None
        self.payment_proof_id = None
        self.message_id = None

    def set_items_from_data(self, items_data: list):
        """Parse items from deep link data."""
        self.items = items_data
        self.total = sum(
            (item.get('price', 0) * item.get('qty', 1))
            for item in items_data
        )

    def get_items_text(self) -> str:
        """Format items list for message."""
        lines = []
        for i, item in enumerate(self.items, 1):
            name = item.get('name', 'Товар')
            sku = item.get('sku', '—')
            qty = item.get('qty', 1)
            price = item.get('price', 0)
            line_total = price * qty
            lines.append(f"{i}. {name}\n   SKU: {sku} | {qty} шт × {price} грн = {line_total} грн")
        return '\n'.join(lines)

    def get_summary(self) -> str:
        """Get order summary text."""
        return (
            f"📋 *Дані замовлення:*\n\n"
            f"👤 *Клієнт:*\n"
            f"   Ім'я: {self.name} {self.surname}\n"
            f"   Телефон: {self.phone}\n\n"
            f"📦 *Доставка:*\n"
            f"   Місто: {self.city}\n"
            f"   Відділення НП: №{self.branch}\n\n"
            f"🛒 *Товари:*\n{self.get_items_text()}\n\n"
            f"💰 *Сума:* {self.total:,.0f} грн"
        )


# Storage for user sessions
user_sessions: dict[int, UserData] = {}


def get_user_data(user_id: int) -> UserData:
    """Get or create user session."""
    if user_id not in user_sessions:
        user_sessions[user_id] = UserData()
    return user_sessions[user_id]


def clear_user_data(user_id: int):
    """Clear user session."""
    if user_id in user_sessions:
        user_sessions[user_id].reset()
