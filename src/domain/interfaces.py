from typing import Protocol

from src.domain.customer import EmailRecipient


class OrderReader(Protocol):
    def get_order(self, order_id: int) -> dict | None: ...

    def list_orders(self) -> list[dict]: ...


class OrderWriter(Protocol):
    def save_order(self, payload: dict) -> dict: ...

    def cancel_order(self, order_id: int) -> bool: ...


class OrderRepository(OrderReader, OrderWriter, Protocol):
    """Контракт хранилища для сценариев записи и чтения заказов."""


class OrderNotifier(Protocol):
    def notify(self, order: dict, customer: EmailRecipient) -> None: ...


class InvoiceGenerator(Protocol):
    def generate(self, order: dict) -> None: ...


class AuditLog(Protocol):
    def write(self, action: str, order_id: int) -> None: ...
