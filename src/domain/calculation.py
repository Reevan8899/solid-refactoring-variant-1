class OrderCalculator:
    def total(self, items: list[dict], user_type: str) -> float:
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
