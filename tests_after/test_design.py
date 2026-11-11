from contextlib import closing
from unittest.mock import Mock

import pytest

from legacy.bad_code import OrderProcessor as LegacyProcessor
from order_processor import OrderProcessor
from src.application.order_service import OrderService
from src.application.order_view import ReadOnlyOrderView
from src.domain.calculation import OrderCalculator
from src.domain.customer import PremiumUser, User
from src.domain.discount_strategies import DiscountStrategyFactory
from src.domain.interfaces import AuditLog, InvoiceGenerator, OrderNotifier, OrderReader
from src.domain.validation import OrderValidator
from src.infrastructure.in_memory_repository import InMemoryOrderRepository
from src.infrastructure.notifier import OutboxNotifier


@pytest.mark.parametrize(("user_type", "rate"), [
    ("regular", 0.05), ("vip", 0.10), ("premium", 0.15), ("student", 0.20), ("unknown", 0.0),
])
def test_builtin_discounts(user_type, rate):
    assert DiscountStrategyFactory().create(user_type).discount() == rate


def test_registering_new_strategy_does_not_require_a_calculator_change():
    class PartnerDiscount:
        def discount(self):
            return 0.25

    factory = DiscountStrategyFactory()
    factory.register("partner", PartnerDiscount)
    calculator = OrderCalculator(factory)
    assert calculator.total([{"price": 100, "quantity": 1}], "partner") == 75.0
    assert DiscountStrategyFactory().create("partner").discount() == 0.0
    with pytest.raises(ValueError, match="уникальным"):
        factory.register("partner", PartnerDiscount)
    with pytest.raises(ValueError, match="непустым"):
        factory.register("", PartnerDiscount)


@pytest.mark.parametrize(("user_class", "subject"), [(User, "Order #7"), (PremiumUser, "Premium order #7")])
def test_notifier_accepts_both_recipient_types(user_class, subject):
    outbox = []
    recipient = user_class("recipient@example.test")
    assert isinstance(recipient.get_email(), str)
    OutboxNotifier(outbox).notify({"id": 7}, recipient)
    assert outbox == [{"to": "recipient@example.test", "subject": subject, "order_id": 7}]


def test_readonly_view_uses_a_reader_only():
    reader = Mock(spec_set=OrderReader)
    reader.get_order.return_value = {"id": 1}
    reader.list_orders.return_value = [{"id": 1}]
    view = ReadOnlyOrderView(reader)
    assert view.get_order(1) == {"id": 1}
    assert view.list_orders() == [{"id": 1}]
    reader.get_order.assert_called_once_with(1)
    reader.list_orders.assert_called_once_with()


def test_service_runs_with_injected_repository_and_adapters():
    repo = InMemoryOrderRepository()
    notifier = Mock(spec_set=OrderNotifier)
    audit = Mock(spec_set=AuditLog)
    invoice = Mock(spec_set=InvoiceGenerator)
    service = OrderService(
        repository=repo, validator=OrderValidator(), calculator=OrderCalculator(DiscountStrategyFactory()),
        notifier=notifier, audit=audit, invoice_generator=invoice,
    )
    item = {"price": 100, "quantity": 2}
    assert service.process_order({"user_id": 3, "user_type": "vip", "items": [item]}) == 180.0
    order = service.get_order(1)
    item["quantity"] = 9
    assert service.list_orders() == [order] and order["items"][0]["quantity"] == 2
    assert notifier.notify.call_args.args[1].get_email() == "user-3@example.test"
    invoice.generate.assert_called_once_with(order)
    assert service.cancel_order(1) and not service.cancel_order(1) and not service.cancel_order(2)
    assert service.get_order(1)["status"] == "cancelled"
    assert [call.args for call in audit.write.call_args_list] == [("created", 1), ("cancelled", 1)]


def test_old_sqlite_file_and_pdf_are_compatible(tmp_path):
    data = {"user_id": 1, "user_type": "premium", "items": [{"price": 20, "quantity": 1}]}
    database = tmp_path / "old.sqlite3"
    with closing(LegacyProcessor(database)) as old, closing(OrderProcessor()) as new:
        assert old.process_order(data) == new.process_order(data)
        assert old.invoices[1] == new.invoices[1]
        assert old.outbox == new.outbox
        original = old.get_order(1)
    with closing(OrderProcessor(database)) as processor:
        assert processor.get_order(1) == original
        processor.process_order(data)
        assert [row["id"] for row in processor.list_orders()] == [1, 2]
