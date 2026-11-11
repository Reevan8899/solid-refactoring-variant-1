from src.domain.customer import User


class OutboxNotifier:
    def __init__(self, outbox: list[dict]):
        self.outbox = outbox

    def notify(self, order: dict, customer: User) -> None:
        address = customer.get_email()
        if isinstance(address, dict):
            address = address["email"]
        self.outbox.append({"to": address, "subject": customer.subject(order["id"]), "order_id": order["id"]})
