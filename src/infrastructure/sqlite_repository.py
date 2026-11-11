import json
import sqlite3


class SQLiteOrderRepository:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            status TEXT NOT NULL
        )""")

    def save_order(self, payload: dict) -> dict:
        encoded = json.dumps(payload, ensure_ascii=False)
        with self.connection as db:
            cursor = db.execute("INSERT INTO orders (payload, status) VALUES (?, 'created')", (encoded,))
        return {"id": cursor.lastrowid, **json.loads(encoded), "status": "created"}

    def get_order(self, order_id: int) -> dict | None:
        row = self.connection.execute("SELECT id, payload, status FROM orders WHERE id = ?", (order_id,)).fetchone()
        return self._decode(row) if row is not None else None

    def list_orders(self) -> list[dict]:
        rows = self.connection.execute("SELECT id, payload, status FROM orders ORDER BY id")
        return [self._decode(row) for row in rows]

    def cancel_order(self, order_id: int) -> bool:
        with self.connection as db:
            cursor = db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ? AND status = 'created'", (order_id,))
        return cursor.rowcount == 1

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _decode(row: tuple) -> dict:
        order_id, payload, status = row
        return {"id": order_id, **json.loads(payload), "status": status}
