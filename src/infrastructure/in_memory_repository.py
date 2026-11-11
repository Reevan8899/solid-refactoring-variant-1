from copy import deepcopy


class InMemoryOrderRepository:
    """Репозиторий для тестирования сервиса без SQLite."""

    def __init__(self):
        self._orders: dict[int, dict] = {}

    def save_order(self, payload: dict) -> dict:
        order_id = len(self._orders) + 1
        order = {"id": order_id, **deepcopy(payload), "status": "created"}
        self._orders[order_id] = order
        return deepcopy(order)

    def get_order(self, order_id: int) -> dict | None:
        return deepcopy(self._orders.get(order_id))

    def list_orders(self) -> list[dict]:
        return deepcopy(list(self._orders.values()))

    def cancel_order(self, order_id: int) -> bool:
        order = self._orders.get(order_id)
        if order is None or order["status"] != "created":
            return False
        order["status"] = "cancelled"
        return True
