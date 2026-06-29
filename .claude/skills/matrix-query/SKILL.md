# Skill: matrix-query

## Цель

Поиск и фильтрация данных в матрице (SQLite). Умеет строить запросы
по любым полям, объединять таблицы и возвращать результат в удобном формате.

## Как вызвать

```
/matrix-query <что найти>
```

Примеры:
```
/matrix-query клиенты со статусом prospect
/matrix-query просроченные задачи для клиента Acme
/matrix-query транзакции expense за 2024 год
/matrix-query все контакты с ролью CTO
```

## Алгоритм

1. Разобрать запрос на естественном языке → определить таблицу и фильтры.
2. Построить SQL-запрос через `MatrixDB._query()` или нужный метод.
3. Вывести результат таблицей через `tabulate`.
4. Показать количество найденных записей.

## Маппинг сущностей

| Термин          | Таблица       | Основные фильтры |
|-----------------|---------------|-----------------|
| клиент/client   | clients       | status, name, email |
| проект/project  | projects      | status, client_id, budget |
| задача/task     | tasks         | status, priority, assignee, due_date, overdue |
| транзакция/tx   | transactions  | type, category, date_from, date_to |
| контакт/contact | contacts      | client_id, role, email |

## Примеры SQL-запросов

```python
# Просроченные критические задачи
with MatrixDB() as db:
    rows = db.get_tasks(priority="critical", overdue=True)

# Все расходы за квартал
with MatrixDB() as db:
    rows = db.get_transactions(tx_type="expense",
                               date_from="2024-01-01",
                               date_to="2024-03-31")

# Произвольный JOIN
with MatrixDB() as db:
    rows = db._query("""
        SELECT c.name, p.name, COUNT(t.id) AS tasks
        FROM clients c
        JOIN projects p ON p.client_id = c.id
        LEFT JOIN tasks t ON t.project_id = p.id
        GROUP BY c.id, p.id
    """)
```

## Выходной формат

```
── Результат: 7 записей ──────────────────────────────────────
╭──────┬────────────┬──────────────┬──────────┬────────────╮
│ id   │ client     │ title        │ priority │ due_date   │
├──────┼────────────┼──────────────┼──────────┼────────────┤
│ 3    │ Acme Corp  │ Fix login    │ critical │ 2024-05-01 │
╰──────┴────────────┴──────────────┴──────────┴────────────╯
```
