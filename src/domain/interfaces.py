from abc import ABC, abstractmethod


class OrderOperations(ABC):
    @abstractmethod
    def get_order(self, order_id): ...

    @abstractmethod
    def list_orders(self): ...

    @abstractmethod
    def save_order(self, payload): ...

    @abstractmethod
    def cancel_order(self, order_id): ...

    @abstractmethod
    def notify(self, order, customer): ...

    @abstractmethod
    def generate(self, order): ...

    @abstractmethod
    def write(self, action, order_id): ...
