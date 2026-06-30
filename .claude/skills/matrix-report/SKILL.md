# Skill: matrix-report

## Цель

Генерирует структурированные отчёты и сводки по данным матрицы.
Поддерживает финансовые отчёты, операционные дашборды и экспорт.

## Как вызвать

```
/matrix-report [тип отчёта]
```

Доступные типы:
```
/matrix-report summary          # Общая сводка
/matrix-report finance          # Финансовый P&L отчёт
/matrix-report finance --year 2024
/matrix-report tasks            # Операционный отчёт по задачам
/matrix-report client Acme      # Отчёт по конкретному клиенту
/matrix-report export excel     # Экспорт в Excel
/matrix-report export csv tasks # Экспорт таблицы в CSV
```

## Типы отчётов

### summary — Общая сводка
```
MATRIX SUMMARY
──────────────────────────────────
  Клиенты:        12
  Проекты:        34 (active: 21)
  Задачи:         89 (overdue: 5)
  Выручка:   $420 000
  Расходы:   $120 000
  Прибыль:   $300 000
```

### finance — Финансовый отчёт
```
P&L ОТЧЁТ 2024
──────────────────────────────────────────────────
Выручка по клиентам:
  Acme Corp     $150 000   (3 проекта)
  Beta LLC      $90 000    (2 проекта)

Денежный поток по месяцам:
  2024-01   Доход: $40k   Расход: $12k   Нетто: +$28k
  2024-02   Доход: $35k   Расход: $8k    Нетто: +$27k

Итого: Доход $420k | Расход $120k | Прибыль $300k (71%)
```

### tasks — Операционный отчёт
```
ОПЕРАЦИОННЫЙ ОТЧЁТ
──────────────────────────────────
По статусу:
  todo:        12
  in_progress: 45
  review:       8
  done:        24

Просроченные (топ-5):
  #3  Fix auth bug   critical   Acme Corp   2024-03-01
  ...

Загрузка по исполнителям:
  Alice: 12 задач (3 overdue)
  Bob:   8 задач  (0 overdue)
```

### client <name> — Карточка клиента
```
КЛИЕНТ: Acme Corp
──────────────────────────────────
  Статус:    active
  Проектов:  3 (active: 2, completed: 1)
  Задач:     24 (overdue: 2)
  Выручка:   $150 000
  Контакты:  Bob Smith (CTO), Jane Doe (CFO)
```

## Код генерации

```python
from matrix import MatrixDB
from exporter import MatrixExporter

with MatrixDB() as db:
    # Финансовая сводка
    summary = db.summary()
    by_client = db.revenue_by_client()
    cashflow = db.monthly_cashflow(year=2024)
    
    # Экспорт
    exp = MatrixExporter(db)
    exp.to_excel(Path("report.xlsx"))
    exp.to_csv("clients", Path("clients.csv"))
```

## Выходные форматы

| Формат  | Команда                        | Файл              |
|---------|--------------------------------|-------------------|
| Текст   | `/matrix-report summary`       | (в чате)          |
| Excel   | `/matrix-report export excel`  | `matrix_export.xlsx` |
| CSV     | `/matrix-report export csv tasks` | `tasks.csv`    |
| JSON    | `/matrix-report export json`   | `matrix.json`     |
