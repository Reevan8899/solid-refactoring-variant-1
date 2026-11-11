from pathlib import Path

from src.application.order_service import OrderService
from src.domain.calculation import OrderCalculator
from src.domain.discount_strategies import DiscountStrategyFactory
from src.domain.validation import OrderValidator
from src.infrastructure.audit import ListAuditLog
from src.infrastructure.invoice import PdfInvoiceGenerator
from src.infrastructure.notifier import OutboxNotifier
from src.infrastructure.sqlite_repository import SQLiteOrderRepository


class OrderProcessor(OrderService):
    """Публичная точка входа со сборкой SQLite и локальных адаптеров."""

    def __init__(self, database: str | Path = ":memory:"):
        self.outbox: list[dict] = []
        self.audit_log: list[str] = []
        self.invoices: dict[int, bytes] = {}
        self._sqlite = SQLiteOrderRepository(database)
        super().__init__(
            repository=self._sqlite,
            calculator=OrderCalculator(DiscountStrategyFactory()),
            validator=OrderValidator(),
            notifier=OutboxNotifier(self.outbox),
            audit=ListAuditLog(self.audit_log),
            invoice_generator=PdfInvoiceGenerator(self.invoices),
        )

    def close(self) -> None:
        self._sqlite.close()
