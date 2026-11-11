from src.domain.customer import EmailRecipient


class OutboxNotifier:
    def __init__(self, outbox: list[dict]):
        self.outbox = outbox

    def notify(self, order: dict, customer: EmailRecipient) -> None:
        order_id = order["id"]
        self.outbox.append({"to": customer.get_email(), "subject": customer.subject(order_id), "order_id": order_id})
