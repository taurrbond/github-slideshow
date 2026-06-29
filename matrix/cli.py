"""Matrix CLI — полный интерфейс командной строки для работы с матрицей данных."""
import json
import sys
from pathlib import Path

import click
from tabulate import tabulate

from matrix import MatrixDB
from models import (
    ClientCreate, ProjectCreate, TaskCreate, TransactionCreate, ContactCreate,
)
from exporter import MatrixExporter


DB_PATH = Path(__file__).parent / "matrix.db"


def _db():
    return MatrixDB(DB_PATH)


def _print_table(rows: list[dict], title: str = "") -> None:
    if not rows:
        click.echo("(нет данных)")
        return
    if title:
        click.echo(f"\n── {title} {'─' * max(0, 50 - len(title))}")
    click.echo(tabulate(rows, headers="keys", tablefmt="rounded_outline"))


# ── Root ──────────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Matrix Data — управление данными через CLI."""


# ── Summary ───────────────────────────────────────────────────────────────────

@cli.command()
def summary():
    """Общая сводка по матрице."""
    with _db() as db:
        s = db.summary()
    rows = [
        {"Метрика": "Клиенты",      "Значение": s["clients"]},
        {"Метрика": "Проекты",      "Значение": s["projects"]},
        {"Метрика": "Задачи",       "Значение": s["tasks"]},
        {"Метрика": "Транзакции",   "Значение": s["transactions"]},
        {"Метрика": "Контакты",     "Значение": s["contacts"]},
        {"Метрика": "Выручка",      "Значение": f"${s['revenue']:,.2f}"},
        {"Метрика": "Расходы",      "Значение": f"${s['expenses']:,.2f}"},
        {"Метрика": "Прибыль",      "Значение": f"${s['revenue'] - s['expenses']:,.2f}"},
        {"Метрика": "Просроч. задачи", "Значение": s["overdue_tasks"]},
    ]
    _print_table(rows, "MATRIX SUMMARY")


# ── Clients ───────────────────────────────────────────────────────────────────

@cli.group()
def client():
    """Управление клиентами."""


@client.command("add")
@click.option("--name",   required=True)
@click.option("--email")
@click.option("--phone")
@click.option("--status", default="active", type=click.Choice(["active","inactive","prospect"]))
@click.option("--notes")
def client_add(name, email, phone, status, notes):
    """Добавить клиента."""
    data = ClientCreate(name=name, email=email, phone=phone, status=status, notes=notes)
    with _db() as db:
        row_id = db.add_client(**data.model_dump())
    click.echo(f"✓ Клиент создан: id={row_id}")


@client.command("list")
@click.option("--status")
@click.option("--search")
def client_list(status, search):
    """Список клиентов."""
    with _db() as db:
        rows = db.get_clients(status=status, search=search)
    _print_table(rows, "Клиенты")


@client.command("delete")
@click.argument("client_id", type=int)
@click.confirmation_option(prompt="Удалить клиента и все связанные данные?")
def client_delete(client_id):
    """Удалить клиента."""
    with _db() as db:
        db.delete_client(client_id)
    click.echo(f"✓ Клиент {client_id} удалён")


# ── Projects ──────────────────────────────────────────────────────────────────

@cli.group()
def project():
    """Управление проектами."""


@project.command("add")
@click.option("--client-id", required=True, type=int)
@click.option("--name",      required=True)
@click.option("--description")
@click.option("--status",    default="active")
@click.option("--budget",    type=float)
@click.option("--start-date")
@click.option("--end-date")
def project_add(client_id, name, description, status, budget, start_date, end_date):
    """Добавить проект."""
    data = ProjectCreate(
        client_id=client_id, name=name, description=description,
        status=status, budget=budget, start_date=start_date, end_date=end_date,
    )
    with _db() as db:
        row_id = db.add_project(**data.model_dump())
    click.echo(f"✓ Проект создан: id={row_id}")


@project.command("list")
@click.option("--client-id", type=int)
@click.option("--status")
@click.option("--search")
def project_list(client_id, status, search):
    """Список проектов."""
    with _db() as db:
        rows = db.get_projects(client_id=client_id, status=status, search=search)
    _print_table(rows, "Проекты")


# ── Tasks ─────────────────────────────────────────────────────────────────────

@cli.group()
def task():
    """Управление задачами."""


@task.command("add")
@click.option("--project-id", required=True, type=int)
@click.option("--title",      required=True)
@click.option("--assignee")
@click.option("--status",   default="todo")
@click.option("--priority", default="medium")
@click.option("--due-date")
@click.option("--description")
def task_add(project_id, title, assignee, status, priority, due_date, description):
    """Добавить задачу."""
    data = TaskCreate(
        project_id=project_id, title=title, assignee=assignee,
        status=status, priority=priority, due_date=due_date, description=description,
    )
    with _db() as db:
        row_id = db.add_task(**data.model_dump())
    click.echo(f"✓ Задача создана: id={row_id}")


@task.command("list")
@click.option("--project-id", type=int)
@click.option("--status")
@click.option("--assignee")
@click.option("--priority")
@click.option("--overdue", is_flag=True)
def task_list(project_id, status, assignee, priority, overdue):
    """Список задач."""
    with _db() as db:
        rows = db.get_tasks(
            project_id=project_id, status=status, assignee=assignee,
            priority=priority, overdue=overdue,
        )
    _print_table(rows, "Задачи")


@task.command("done")
@click.argument("task_id", type=int)
def task_done(task_id):
    """Пометить задачу выполненной."""
    with _db() as db:
        db.update_task(task_id, status="done")
    click.echo(f"✓ Задача {task_id} закрыта")


# ── Transactions ──────────────────────────────────────────────────────────────

@cli.group()
def tx():
    """Управление транзакциями."""


@tx.command("add")
@click.option("--project-id", required=True, type=int)
@click.option("--amount",     required=True, type=float)
@click.option("--type",      "tx_type", default="income", type=click.Choice(["income","expense"]))
@click.option("--category")
@click.option("--description")
@click.option("--currency",  default="USD")
@click.option("--date")
def tx_add(project_id, amount, tx_type, category, description, currency, date):
    """Добавить транзакцию."""
    data = TransactionCreate(
        project_id=project_id, amount=amount, type=tx_type,
        category=category, description=description, currency=currency, date=date,
    )
    with _db() as db:
        row_id = db.add_transaction(
            project_id=data.project_id, amount=data.amount,
            tx_type=data.type, **{k: v for k, v in data.model_dump().items()
                                  if k not in ("project_id", "amount", "type")},
        )
    click.echo(f"✓ Транзакция создана: id={row_id}")


@tx.command("list")
@click.option("--project-id", type=int)
@click.option("--type",      "tx_type")
@click.option("--category")
@click.option("--from",      "date_from")
@click.option("--to",        "date_to")
def tx_list(project_id, tx_type, category, date_from, date_to):
    """Список транзакций."""
    with _db() as db:
        rows = db.get_transactions(
            project_id=project_id, tx_type=tx_type, category=category,
            date_from=date_from, date_to=date_to,
        )
    _print_table(rows, "Транзакции")


# ── Contacts ──────────────────────────────────────────────────────────────────

@cli.group()
def contact():
    """Управление контактами."""


@contact.command("add")
@click.option("--client-id", required=True, type=int)
@click.option("--name",      required=True)
@click.option("--role")
@click.option("--email")
@click.option("--phone")
@click.option("--notes")
def contact_add(client_id, name, role, email, phone, notes):
    """Добавить контакт."""
    data = ContactCreate(
        client_id=client_id, name=name, role=role,
        email=email, phone=phone, notes=notes,
    )
    with _db() as db:
        row_id = db.add_contact(**data.model_dump())
    click.echo(f"✓ Контакт создан: id={row_id}")


@contact.command("list")
@click.option("--client-id", type=int)
@click.option("--search")
def contact_list(client_id, search):
    """Список контактов."""
    with _db() as db:
        rows = db.get_contacts(client_id=client_id, search=search)
    _print_table(rows, "Контакты")


# ── Report ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--year", type=int, help="Фильтр по году")
def report(year):
    """Финансовый отчёт и аналитика."""
    with _db() as db:
        click.echo("\n═══ ФИНАНСОВЫЙ ОТЧЁТ ═══\n")
        _print_table(db.revenue_by_client(), "Выручка по клиентам")
        _print_table(db.monthly_cashflow(year=year), "Денежный поток по месяцам")
        _print_table(db.task_stats(), "Статистика задач")


# ── Export / Import ───────────────────────────────────────────────────────────

@cli.group()
def export():
    """Экспорт данных."""


@export.command("csv")
@click.argument("table", type=click.Choice(["clients","projects","tasks","transactions","contacts"]))
@click.option("--out", default=None, help="Путь к файлу (по умолчанию: <table>.csv)")
def export_csv(table, out):
    """Экспортировать таблицу в CSV."""
    path = Path(out) if out else Path(f"{table}.csv")
    with _db() as db:
        exp = MatrixExporter(db)
        exp.to_csv(table, path)
    click.echo(f"✓ Экспортировано в {path}")


@export.command("excel")
@click.option("--out", default="matrix_export.xlsx")
def export_excel(out):
    """Экспортировать всю матрицу в Excel (все листы)."""
    with _db() as db:
        exp = MatrixExporter(db)
        exp.to_excel(Path(out))
    click.echo(f"✓ Экспортировано в {out}")


@cli.group()
def imp():
    """Импорт данных."""
    # named 'imp' to avoid shadowing Python built-in 'import'


@imp.command("csv")
@click.argument("table", type=click.Choice(["clients","projects","tasks","transactions","contacts"]))
@click.argument("path")
def import_csv(table, path):
    """Импортировать данные из CSV."""
    with _db() as db:
        exp = MatrixExporter(db)
        count = exp.from_csv(table, Path(path))
    click.echo(f"✓ Импортировано {count} строк в '{table}'")


if __name__ == "__main__":
    cli()
