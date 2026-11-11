# Метрики

## Исходная версия

Измерена до изменений в коде.

```text
legacy/bad_code.py
    M 91:4 OrderProcessor.validate - C (18)
    M 114:4 OrderProcessor.calculate_total - B (6)
    C 82:0 OrderProcessor - A (4)
    C 12:0 User - A (2)
    C 23:0 PremiumUser - A (2)
    C 32:0 IOrderOperations - A (2)
    C 56:0 ReadOnlyOrderView - A (2)
    C 72:0 LegacyDatabase - A (2)
    M 135:4 OrderProcessor.get_order - A (2)
    M 141:4 OrderProcessor.list_orders - A (2)
    M 147:4 OrderProcessor.cancel_order - A (2)
    M 155:4 OrderProcessor.notify - A (2)
    M 172:4 OrderProcessor.process_order - A (2)
    M 13:4 User.__init__ - A (1)
    M 16:4 User.get_email - A (1)
    M 19:4 User.subject - A (1)
    M 25:4 PremiumUser.get_email - A (1)
    M 28:4 PremiumUser.subject - A (1)
    M 35:4 IOrderOperations.get_order - A (1)
    M 38:4 IOrderOperations.list_orders - A (1)
    M 41:4 IOrderOperations.save_order - A (1)
    M 44:4 IOrderOperations.cancel_order - A (1)
    M 47:4 IOrderOperations.notify - A (1)
    M 50:4 IOrderOperations.generate_invoice - A (1)
    M 53:4 IOrderOperations.audit - A (1)
    M 57:4 ReadOnlyOrderView.__init__ - A (1)
    M 60:4 ReadOnlyOrderView.get_order - A (1)
    M 63:4 ReadOnlyOrderView.list_orders - A (1)
    M 66:4 ReadOnlyOrderView.unsupported - A (1)
    M 73:4 LegacyDatabase.__init__ - A (1)
    M 84:4 OrderProcessor.__init__ - A (1)
    M 129:4 OrderProcessor.save_order - A (1)
    M 161:4 OrderProcessor.audit - A (1)
    M 164:4 OrderProcessor.generate_invoice - A (1)
    M 184:4 OrderProcessor.close - A (1)

35 blocks (classes, functions, methods) analyzed.
Average complexity: A (2.0)

legacy/bad_code.py - A (36.51)
Required test coverage of 80% reached. Total coverage: 96.64%
============================= 20 passed in 0.42s ==============================
```
