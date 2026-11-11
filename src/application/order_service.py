from src.domain.calculation import OrderCalculator
from src.domain.customer import customer_for
from src.domain.interfaces import AuditLog, InvoiceGenerator, OrderNotifier, OrderRepository
from src.domain.validation import OrderValidator


class OrderService:
    def __init__(
        self,
        *,
        repository: OrderRepository,
        calculator: OrderCalculator,
        validator: OrderValidator,
        notifier: OrderNotifier,
        audit: AuditLog,
        invoice_generator: InvoiceGenerator,
    ):
        self.repository = repository
        self.calculator = calculator
        self.validator = validator
        self.notifier = notifier
        self.audit = audit
        self.invoice_generator = invoice_generator

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
