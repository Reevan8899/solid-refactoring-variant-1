from src.domain.calculation import OrderCalculator
from src.domain.customer import customer_for
from src.domain.validation import OrderValidator
from src.infrastructure.audit import ListAuditLog
from src.infrastructure.invoice import PdfInvoiceGenerator
from src.infrastructure.notifier import OutboxNotifier
from src.infrastructure.sqlite_repository import SQLiteOrderRepository


class OrderService:
    def __init__(self, database=":memory:"):
        self.outbox = []
        self.audit_log = []
        self.invoices = {}
        self.repository = SQLiteOrderRepository(database)
        self.calculator = OrderCalculator()
        self.validator = OrderValidator()
        self.notifier = OutboxNotifier(self.outbox)
        self.audit = ListAuditLog(self.audit_log)
        self.invoice_generator = PdfInvoiceGenerator(self.invoices)

    def process_order(self, data: dict) -> float:
        self.validator.validate(data)
        total = self.calculator.total(data["items"], data.get("user_type", "regular"))
        payload = {"user_id": data["user_id"], "total": total, "items": data["items"]}
        order = self.repository.save_order(payload)
        self.notifier.notify(order, customer_for(data))
        self.audit.write("created", order["id"])
        self.invoice_generator.generate(order)
        return total

    def get_order(self, order_id: int) -> dict | None:
        return self.repository.get_order(order_id)

    def list_orders(self) -> list[dict]:
        return self.repository.list_orders()

    def cancel_order(self, order_id: int) -> bool:
        if not self.repository.cancel_order(order_id):
            return False
        self.audit.write("cancelled", order_id)
        return True

    def close(self) -> None:
        self.repository.close()
