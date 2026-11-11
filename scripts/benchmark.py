"""Сравнивает обработку 1000 одинаковых заказов на двух реализациях."""

from contextlib import closing
from functools import partial
from statistics import median
from timeit import Timer

from legacy.bad_code import OrderProcessor as LegacyProcessor
from order_processor import OrderProcessor

ORDERS = 1000
REPEATS = 5
DATA = {"user_id": 7, "user_type": "premium", "items": [{"price": 100, "quantity": 2}]}


def run(processor_factory):
    with closing(processor_factory()) as processor:
        totals = [processor.process_order(DATA) for _ in range(ORDERS)]
        assert set(totals) == {170.0}
        assert len(processor.outbox) == len(processor.audit_log) == len(processor.invoices) == ORDERS
        assert processor.get_order(ORDERS)["total"] == 170.0


def main() -> None:
    timers = [Timer(partial(run, factory)) for factory in (LegacyProcessor, OrderProcessor)]
    times = [[], []]
    for repeat in range(REPEATS):
        for index in (range(2) if repeat % 2 == 0 else reversed(range(2))):
            times[index].append(timers[index].timeit(number=1))
    for name, results in zip(("До", "После"), times):
        print(f"{name}: {', '.join(f'{value:.6f}' for value in results)} с")
        print(f"{name}: минимум {min(results):.6f} с, медиана {median(results):.6f} с")
    change = (median(times[1]) / median(times[0]) - 1) * 100
    print(f"Изменение медианы: {change:+.2f}%")


if __name__ == "__main__":
    main()
