from src.domain.interfaces import OrderReader


class ReadOnlyOrderView:
    def __init__(self, repository: OrderReader):
        self.repository = repository

    def get_order(self, order_id: int) -> dict | None:
        return self.repository.get_order(order_id)

    def list_orders(self) -> list[dict]:
        return self.repository.list_orders()
