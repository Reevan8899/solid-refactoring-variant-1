from src.domain.interfaces import OrderOperations


class ReadOnlyOrderView(OrderOperations):
    def __init__(self, repository):
        self.repository = repository

    def get_order(self, order_id):
        return self.repository.get_order(order_id)

    def list_orders(self):
        return self.repository.list_orders()

    def unsupported(self, *args):
        raise NotImplementedError("Этот просмотр поддерживает только чтение")

    save_order = cancel_order = notify = generate = write = unsupported
