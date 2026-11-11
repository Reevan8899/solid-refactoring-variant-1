from typing import Protocol


class EmailRecipient(Protocol):
    def get_email(self) -> str:
        """Возвращает строковый адрес получателя."""

    def subject(self, order_id: int) -> str:
        """Возвращает тему подтверждения заказа."""


class User:
    def __init__(self, email: str):
        self.email = email

    def get_email(self) -> str:
        return self.email

    def subject(self, order_id: int) -> str:
        return f"Order #{order_id}"


class PremiumUser(User):
    def subject(self, order_id: int) -> str:
        return f"Premium order #{order_id}"


def customer_for(data: dict) -> EmailRecipient:
    email = data.get("email", f"user-{data['user_id']}@example.test").strip()
    return PremiumUser(email) if data.get("user_type") == "premium" else User(email)
