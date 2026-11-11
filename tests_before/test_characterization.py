"""Контракт процессора. Один и тот же набор работает на обеих версиях."""

from contextlib import closing

import pytest

from order_processor import OrderProcessor


@pytest.fixture
def processor():
    with closing(OrderProcessor()) as instance:
        yield instance


@pytest.mark.parametrize(("user_type", "expected"), [
    ("regular", 237.5), ("vip", 225.0), ("premium", 212.5), ("student", 200.0), ("unknown", 250.0),
])
def test_discounts_and_total(processor, user_type, expected):
    data = {"user_id": 1, "user_type": user_type, "items": [{"price": 100, "quantity": 2}, {"price": 50, "quantity": 1}]}
    assert processor.process_order(data) == pytest.approx(expected)
    assert processor.get_order(1) == {"id": 1, "user_id": 1, "total": expected, "items": data["items"], "status": "created"}


def test_default_discount_rounding_and_zero_price(processor):
    assert processor.process_order({"user_id": 1, "items": [{"price": 10.123, "quantity": 1}]}) == 9.62
    assert processor.process_order({"user_id": 1, "items": [{"price": 0, "quantity": 1}]}) == 0.0


@pytest.mark.parametrize(("data", "field"), [
    (None, "словарём"), ({"items": []}, "user_id"), ({"user_id": True, "items": []}, "user_id"),
    ({"user_id": 1, "items": []}, "items"), ({"user_id": 1, "items": [1]}, "items"),
    ({"user_id": 1, "items": [{"price": -1, "quantity": 1}]}, "price"),
    ({"user_id": 1, "items": [{"price": float("nan"), "quantity": 1}]}, "price"),
    ({"user_id": 1, "items": [{"price": 1, "quantity": True}]}, "quantity"),
    ({"user_id": 1, "items": [{"price": 1, "quantity": 1}], "email": " "}, "email"),
    ({"user_id": 1, "items": [{"price": 1, "quantity": 1}], "user_type": []}, "user_type"),
])
def test_invalid_input_has_no_side_effects(processor, data, field):
    with pytest.raises(ValueError, match=field):
        processor.process_order(data)
    assert processor.list_orders() == []
    assert processor.outbox == [] and processor.audit_log == [] and processor.invoices == {}


def test_notification_audit_and_pdf(processor):
    processor.process_order({"user_id": 2, "items": [{"price": 20, "quantity": 1}]})
    processor.process_order({"user_id": 2, "user_type": "premium", "email": " custom@example.test ", "items": [{"price": 20, "quantity": 1}]})
    assert processor.outbox == [
        {"to": "user-2@example.test", "subject": "Order #1", "order_id": 1},
        {"to": "custom@example.test", "subject": "Premium order #2", "order_id": 2},
    ]
    assert processor.audit_log == ["created:1", "created:2"]
    assert set(processor.invoices) == {1, 2}
    assert all(pdf.startswith(b"%PDF-") and pdf.rstrip().endswith(b"%%EOF") for pdf in processor.invoices.values())


def test_cancellation_changes_status_once(processor):
    assert processor.get_order(1) is None and processor.cancel_order(1) is False
    processor.process_order({"user_id": 1, "items": [{"price": 100, "quantity": 1}]})
    assert processor.cancel_order(1) is True
    assert processor.get_order(1)["status"] == "cancelled"
    assert processor.cancel_order(1) is False
    assert processor.audit_log == ["created:1", "cancelled:1"]


def test_items_are_saved_as_snapshot(processor):
    item = {"price": 50, "quantity": 1, "sku": "abc"}
    processor.process_order({"user_id": 1, "items": [item]})
    item["quantity"] = 5
    order = processor.get_order(1)
    assert order["items"] == [{"price": 50, "quantity": 1, "sku": "abc"}]
    order["items"][0]["quantity"] = 6
    assert processor.get_order(1)["items"][0]["quantity"] == 1


def test_reopen_storage_preserves_orders_and_id_sequence(tmp_path):
    database = tmp_path / "orders.sqlite3"
    with closing(OrderProcessor(database)) as first:
        first.process_order({"user_id": 3, "items": [{"price": 1, "quantity": 1}]})
        first.cancel_order(1)
    with closing(OrderProcessor(database)) as second:
        assert second.get_order(1)["status"] == "cancelled"
        second.process_order({"user_id": 4, "items": [{"price": 1, "quantity": 1}]})
        assert [order["id"] for order in second.list_orders()] == [1, 2]
