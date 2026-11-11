# Практическая работа № 9. Вариант № 1

Учебный проект «Обработка заказов» по описанию задания. Исходная реализация находится в `legacy/bad_code.py`. Для работы используется локальное SQLite-хранилище. Уведомления остаются в `outbox`, а PDF-счета доступны как байты в `invoices`.

```sh
python -m pip install -r requirements.txt
python -m pytest tests_before -v --cov=legacy --cov-report=term-missing
```

Публичная точка входа `from order_processor import OrderProcessor`. Метод `process_order(data)` возвращает сумму заказа. `get_order(id)` возвращает заказ или `None`. `list_orders()` возвращает заказы по ID. `cancel_order(id)` возвращает `True` при успешном изменении статуса. Метод `close()` освобождает соединение.
