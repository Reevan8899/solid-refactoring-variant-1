from src.domain.discount_strategies import DiscountStrategyFactory


class OrderCalculator:
    def __init__(self, factory: DiscountStrategyFactory):
        self.factory = factory

    def total(self, items: list[dict], user_type: str) -> float:
        discount = self.factory.create(user_type).discount()
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        return round(subtotal * (1 - discount), 2)
