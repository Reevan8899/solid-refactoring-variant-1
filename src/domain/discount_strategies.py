from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from typing import Protocol


class DiscountStrategy(Protocol):
    def discount(self) -> float:
        """Возвращает коэффициент скидки от 0 до 1 включительно."""


@dataclass(frozen=True)
class FixedDiscount:
    rate: float = 0.0

    def discount(self) -> float:
        return self.rate


class DiscountStrategyFactory:
    def __init__(self):
        self._creators: dict[str, Callable[[], DiscountStrategy]] = {
            "regular": partial(FixedDiscount, 0.05),
            "vip": partial(FixedDiscount, 0.10),
            "premium": partial(FixedDiscount, 0.15),
            "student": partial(FixedDiscount, 0.20),
        }

    def register(self, user_type: str, creator: Callable[[], DiscountStrategy]) -> None:
        if not user_type or user_type in self._creators:
            raise ValueError("Ключ стратегии должен быть непустым и уникальным")
        self._creators[user_type] = creator

    def create(self, user_type: str) -> DiscountStrategy:
        return self._creators.get(user_type, FixedDiscount)()
