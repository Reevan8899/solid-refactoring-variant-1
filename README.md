# Практическая работа № 9. Вариант № 1

[![SOLID checks](https://github.com/Reevan8899/solid-refactoring-variant-1/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Reevan8899/solid-refactoring-variant-1/actions/workflows/ci.yml)

Учебный проект «Обработка заказов» по описанию задания. Исходная реализация находится в `legacy/bad_code.py`. Для работы используется локальное SQLite-хранилище. Уведомления остаются в `outbox`, а PDF-счета доступны как байты в `invoices`.

```sh
python -m pip install -r requirements.txt
python -m pytest -v --cov=src --cov-report=term-missing --cov-fail-under=85
python -m scripts.quality_gate
python -m scripts.benchmark
```

Публичная точка входа `from order_processor import OrderProcessor`. Метод `process_order(data)` возвращает сумму заказа. `get_order(id)` возвращает заказ или `None`. `list_orders()` возвращает заказы по ID. `cancel_order(id)` возвращает `True` при успешном изменении статуса. Метод `close()` освобождает соединение.

Для базовой версии используйте метку `before-refactoring` и выполните `python -m pytest tests_before -v --cov=legacy --cov-fail-under=80`. CI проверяет базовую версию и финальный код. [План](docs/refactoring-plan.md) · [Метрики](docs/metrics.md)
