import math


class OrderValidator:
    def validate(self, data: dict) -> None:
        if not isinstance(data, dict):
            raise ValueError("Заказ должен быть словарём")
        user_id = data.get("user_id")
        if type(user_id) is not int or user_id <= 0:
            raise ValueError("user_id должен быть положительным целым числом")
        items = data.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError("items должен быть непустым списком")
        for item in items:
            self._validate_item(item)
        self._validate_contact(data)

    @staticmethod
    def _validate_contact(data: dict) -> None:
        if not isinstance(data.get("user_type", "regular"), str):
            raise ValueError("user_type должен быть строкой")
        if "email" in data and (not isinstance(data["email"], str) or not data["email"].strip()):
            raise ValueError("email должен быть непустой строкой")

    @staticmethod
    def _validate_item(item: dict) -> None:
        if not isinstance(item, dict):
            raise ValueError("Каждый элемент items должен быть словарём")
        price = item.get("price")
        if type(price) not in (int, float) or price < 0 or price > 10**9 or not math.isfinite(price):
            raise ValueError("price должен быть конечным числом от 0 до 1000000000")
        quantity = item.get("quantity")
        if type(quantity) is not int or not 1 <= quantity <= 10**6:
            raise ValueError("quantity должен быть целым числом от 1 до 1000000")
