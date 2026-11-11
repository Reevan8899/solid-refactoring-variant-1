class User:
    def __init__(self, email: str):
        self.email = email

    def get_email(self) -> str:
        return self.email

    def subject(self, order_id: int) -> str:
        return f"Order #{order_id}"


class PremiumUser(User):
    def get_email(self):
        return {"email": self.email}

    def subject(self, order_id: int) -> str:
        return f"Premium order #{order_id}"


def customer_for(data: dict) -> User:
    email = data.get("email", f"user-{data['user_id']}@example.test").strip()
    return PremiumUser(email) if data.get("user_type") == "premium" else User(email)
