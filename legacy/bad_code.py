"""Учебный исходник варианта 1 для рефакторинга SOLID."""

import json
import math
import sqlite3
from abc import ABC, abstractmethod
from io import BytesIO

from reportlab.pdfgen import canvas


class User:
    def __init__(self, email):
        self.email = email

    def get_email(self) -> str:
        return self.email

    def subject(self, order_id):
        return f"Order #{order_id}"


class PremiumUser(User):
    # LSP: наследник нарушает обещание get_email() -> str.
    def get_email(self):
        return {"email": self.email}

    def subject(self, order_id):
        return f"Premium order #{order_id}"


class IOrderOperations(ABC):
    # ISP: операции записи, чтения, отчёта и уведомлений связаны одним интерфейсом.
    @abstractmethod
    def get_order(self, order_id): ...

    @abstractmethod
    def list_orders(self): ...

    @abstractmethod
    def save_order(self, data, total): ...

    @abstractmethod
    def cancel_order(self, order_id): ...

    @abstractmethod
    def notify(self, order, customer): ...

    @abstractmethod
    def generate_invoice(self, order): ...

    @abstractmethod
    def audit(self, action, order_id): ...


class ReadOnlyOrderView(IOrderOperations):
    def __init__(self, source):
        self.source = source

    def get_order(self, order_id):
        return self.source.get_order(order_id)

    def list_orders(self):
        return self.source.list_orders()

    def unsupported(self, *args):
        raise NotImplementedError("Этот просмотр поддерживает только чтение")

    save_order = cancel_order = notify = generate_invoice = audit = unsupported


class LegacyDatabase:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            status TEXT NOT NULL
        )""")


class OrderProcessor(IOrderOperations):
    # SRP: здесь одновременно правила заказа, SQL, уведомления, журнал и PDF.
    def __init__(self, database=":memory:"):
        # DIP: процессор напрямую создаёт конкретный драйвер хранения.
        self.db = LegacyDatabase(database)
        self.outbox = []
        self.audit_log = []
        self.invoices = {}

    def validate(self, data):
        if not isinstance(data, dict):
            raise ValueError("Заказ должен быть словарём")
        user_id = data.get("user_id")
        if type(user_id) is not int or user_id <= 0:
            raise ValueError("user_id должен быть положительным целым числом")
        items = data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("items должен быть непустым списком")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Каждый элемент items должен быть словарём")
            price = item.get("price")
            if type(price) not in (int, float) or price < 0 or price > 10**9 or not math.isfinite(price):
                raise ValueError("price должен быть конечным числом от 0 до 1000000000")
            quantity = item.get("quantity")
            if type(quantity) is not int or not 1 <= quantity <= 10**6:
                raise ValueError("quantity должен быть целым числом от 1 до 1000000")
        if not isinstance(data.get("user_type", "regular"), str):
            raise ValueError("user_type должен быть строкой")
        if "email" in data and (not isinstance(data["email"], str) or not data["email"].strip()):
            raise ValueError("email должен быть непустой строкой")

    def calculate_total(self, items, user_type):
        # OCP: для нового тарифа требуется менять этот метод.
        if user_type == "regular":
            discount = 0.05
        elif user_type == "vip":
            discount = 0.10
        elif user_type == "premium":
            discount = 0.15
        elif user_type == "student":
            discount = 0.20
        else:
            discount = 0.0
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        return round(subtotal * (1 - discount), 2)

    def save_order(self, data, total):
        payload = json.dumps({"user_id": data["user_id"], "total": total, "items": data["items"]}, ensure_ascii=False)
        with self.db.connection as db:
            cursor = db.execute("INSERT INTO orders (payload, status) VALUES (?, 'created')", (payload,))
        return {"id": cursor.lastrowid, **json.loads(payload), "status": "created"}

    def get_order(self, order_id):
        row = self.db.connection.execute("SELECT id, payload, status FROM orders WHERE id = ?", (order_id,)).fetchone()
        if row is None:
            return None
        return {"id": row[0], **json.loads(row[1]), "status": row[2]}

    def list_orders(self):
        return [
            {"id": row[0], **json.loads(row[1]), "status": row[2]}
            for row in self.db.connection.execute("SELECT id, payload, status FROM orders ORDER BY id")
        ]

    def cancel_order(self, order_id):
        with self.db.connection as db:
            cursor = db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ? AND status = 'created'", (order_id,))
        if cursor.rowcount != 1:
            return False
        self.audit("cancelled", order_id)
        return True

    def notify(self, order, customer):
        address = customer.get_email()
        if isinstance(address, dict):
            address = address["email"]
        self.outbox.append({"to": address, "subject": customer.subject(order["id"]), "order_id": order["id"]})

    def audit(self, action, order_id):
        self.audit_log.append(f"{action}:{order_id}")

    def generate_invoice(self, order):
        target = BytesIO()
        document = canvas.Canvas(target, invariant=1)
        document.drawString(72, 760, f"Order #{order['id']}")
        document.drawString(72, 738, f"Total: {order['total']:.2f}")
        document.save()
        self.invoices[order["id"]] = target.getvalue()

    def process_order(self, data):
        self.validate(data)
        kind = data.get("user_type", "regular")
        total = self.calculate_total(data["items"], kind)
        order = self.save_order(data, total)
        email = data.get("email", f"user-{data['user_id']}@example.test").strip()
        customer = PremiumUser(email) if kind == "premium" else User(email)
        self.notify(order, customer)
        self.audit("created", order["id"])
        self.generate_invoice(order)
        return total

    def close(self):
        self.db.connection.close()
