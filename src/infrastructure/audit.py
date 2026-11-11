class ListAuditLog:
    def __init__(self, events: list[str]):
        self.events = events

    def write(self, action: str, order_id: int) -> None:
        self.events.append(f"{action}:{order_id}")
