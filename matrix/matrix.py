"""Core MatrixDB engine — SQLite-backed CRUD + analytics for all 5 entities."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "matrix.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class MatrixDB:
    """Context-manager wrapper around a SQLite connection."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> "MatrixDB":
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._init_schema()
        return self

    def __exit__(self, *_: Any) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def _init_schema(self) -> None:
        self._conn.executescript(SCHEMA_PATH.read_text())
        self._conn.commit()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Use MatrixDB inside a `with` block")
        return self._conn

    # ── Generic helpers ────────────────────────────────────────────────────────

    def _insert(self, table: str, data: dict) -> int:
        data = {k: v for k, v in data.items() if v is not None}
        cols = ", ".join(data)
        ph = ", ".join("?" * len(data))
        cur = self.conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({ph})", list(data.values())
        )
        self.conn.commit()
        return cur.lastrowid

    def _update(self, table: str, row_id: int, data: dict) -> None:
        data = {k: v for k, v in data.items() if v is not None}
        sets = ", ".join(f"{k} = ?" for k in data)
        self.conn.execute(
            f"UPDATE {table} SET {sets}, updated_at = ? WHERE id = ?",
            [*data.values(), datetime.now().isoformat(), row_id],
        )
        self.conn.commit()

    def _delete(self, table: str, row_id: int) -> None:
        self.conn.execute(f"DELETE FROM {table} WHERE id = ?", [row_id])
        self.conn.commit()

    def _query(self, sql: str, params: list | None = None) -> list[dict]:
        cur = self.conn.execute(sql, params or [])
        return [dict(row) for row in cur.fetchall()]

    def _one(self, sql: str, params: list | None = None) -> dict | None:
        rows = self._query(sql, params)
        return rows[0] if rows else None

    # ── Clients ───────────────────────────────────────────────────────────────

    def add_client(self, name: str, email: str | None = None,
                   phone: str | None = None, status: str = "active",
                   notes: str | None = None) -> int:
        return self._insert("clients", {
            "name": name, "email": email, "phone": phone,
            "status": status, "notes": notes,
        })

    def get_client(self, client_id: int) -> dict | None:
        return self._one("SELECT * FROM clients WHERE id = ?", [client_id])

    def get_clients(self, status: str | None = None,
                    search: str | None = None) -> list[dict]:
        sql, params = "SELECT * FROM clients WHERE 1=1", []
        if status:
            sql += " AND status = ?"; params.append(status)
        if search:
            sql += " AND (name LIKE ? OR email LIKE ?)"; params += [f"%{search}%"] * 2
        return self._query(sql + " ORDER BY created_at DESC", params)

    def update_client(self, client_id: int, **kwargs: Any) -> None:
        self._update("clients", client_id, kwargs)

    def delete_client(self, client_id: int) -> None:
        self._delete("clients", client_id)

    # ── Projects ──────────────────────────────────────────────────────────────

    def add_project(self, client_id: int, name: str,
                    description: str | None = None, status: str = "active",
                    budget: float | None = None, start_date: str | None = None,
                    end_date: str | None = None) -> int:
        return self._insert("projects", {
            "client_id": client_id, "name": name, "description": description,
            "status": status, "budget": budget,
            "start_date": start_date, "end_date": end_date,
        })

    def get_project(self, project_id: int) -> dict | None:
        return self._one(
            "SELECT p.*, c.name AS client_name FROM projects p "
            "LEFT JOIN clients c ON p.client_id = c.id WHERE p.id = ?",
            [project_id],
        )

    def get_projects(self, client_id: int | None = None,
                     status: str | None = None,
                     search: str | None = None) -> list[dict]:
        sql = ("SELECT p.*, c.name AS client_name FROM projects p "
               "LEFT JOIN clients c ON p.client_id = c.id WHERE 1=1")
        params: list = []
        if client_id:
            sql += " AND p.client_id = ?"; params.append(client_id)
        if status:
            sql += " AND p.status = ?"; params.append(status)
        if search:
            sql += " AND (p.name LIKE ? OR p.description LIKE ?)"; params += [f"%{search}%"] * 2
        return self._query(sql + " ORDER BY p.created_at DESC", params)

    def update_project(self, project_id: int, **kwargs: Any) -> None:
        self._update("projects", project_id, kwargs)

    def delete_project(self, project_id: int) -> None:
        self._delete("projects", project_id)

    # ── Tasks ─────────────────────────────────────────────────────────────────

    def add_task(self, project_id: int, title: str,
                 assignee: str | None = None, status: str = "todo",
                 priority: str = "medium", due_date: str | None = None,
                 description: str | None = None) -> int:
        return self._insert("tasks", {
            "project_id": project_id, "title": title, "assignee": assignee,
            "status": status, "priority": priority,
            "due_date": due_date, "description": description,
        })

    def get_task(self, task_id: int) -> dict | None:
        return self._one(
            "SELECT t.*, p.name AS project_name, c.name AS client_name "
            "FROM tasks t LEFT JOIN projects p ON t.project_id = p.id "
            "LEFT JOIN clients c ON p.client_id = c.id WHERE t.id = ?",
            [task_id],
        )

    def get_tasks(self, project_id: int | None = None,
                  status: str | None = None, assignee: str | None = None,
                  priority: str | None = None, overdue: bool = False) -> list[dict]:
        sql = ("SELECT t.*, p.name AS project_name, c.name AS client_name "
               "FROM tasks t LEFT JOIN projects p ON t.project_id = p.id "
               "LEFT JOIN clients c ON p.client_id = c.id WHERE 1=1")
        params: list = []
        if project_id:
            sql += " AND t.project_id = ?"; params.append(project_id)
        if status:
            sql += " AND t.status = ?"; params.append(status)
        if assignee:
            sql += " AND t.assignee = ?"; params.append(assignee)
        if priority:
            sql += " AND t.priority = ?"; params.append(priority)
        if overdue:
            sql += " AND t.due_date < DATE('now') AND t.status NOT IN ('done','cancelled')"
        return self._query(
            sql + " ORDER BY CASE t.priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 "
            "WHEN 'medium' THEN 2 ELSE 3 END, t.due_date ASC",
            params,
        )

    def update_task(self, task_id: int, **kwargs: Any) -> None:
        self._update("tasks", task_id, kwargs)

    def delete_task(self, task_id: int) -> None:
        self._delete("tasks", task_id)

    # ── Transactions ──────────────────────────────────────────────────────────

    def add_transaction(self, project_id: int, amount: float,
                        tx_type: str = "income", description: str | None = None,
                        category: str | None = None, currency: str = "USD",
                        date: str | None = None) -> int:
        return self._insert("transactions", {
            "project_id": project_id, "amount": amount, "type": tx_type,
            "description": description, "category": category,
            "currency": currency,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
        })

    def get_transactions(self, project_id: int | None = None,
                         tx_type: str | None = None, category: str | None = None,
                         date_from: str | None = None,
                         date_to: str | None = None) -> list[dict]:
        sql = ("SELECT t.*, p.name AS project_name, c.name AS client_name "
               "FROM transactions t LEFT JOIN projects p ON t.project_id = p.id "
               "LEFT JOIN clients c ON p.client_id = c.id WHERE 1=1")
        params: list = []
        if project_id:
            sql += " AND t.project_id = ?"; params.append(project_id)
        if tx_type:
            sql += " AND t.type = ?"; params.append(tx_type)
        if category:
            sql += " AND t.category = ?"; params.append(category)
        if date_from:
            sql += " AND t.date >= ?"; params.append(date_from)
        if date_to:
            sql += " AND t.date <= ?"; params.append(date_to)
        return self._query(sql + " ORDER BY t.date DESC", params)

    def update_transaction(self, tx_id: int, **kwargs: Any) -> None:
        self._update("transactions", tx_id, kwargs)

    def delete_transaction(self, tx_id: int) -> None:
        self._delete("transactions", tx_id)

    # ── Contacts ──────────────────────────────────────────────────────────────

    def add_contact(self, client_id: int, name: str, role: str | None = None,
                    email: str | None = None, phone: str | None = None,
                    notes: str | None = None) -> int:
        return self._insert("contacts", {
            "client_id": client_id, "name": name, "role": role,
            "email": email, "phone": phone, "notes": notes,
        })

    def get_contacts(self, client_id: int | None = None,
                     search: str | None = None) -> list[dict]:
        sql = ("SELECT ct.*, cl.name AS client_name FROM contacts ct "
               "LEFT JOIN clients cl ON ct.client_id = cl.id WHERE 1=1")
        params: list = []
        if client_id:
            sql += " AND ct.client_id = ?"; params.append(client_id)
        if search:
            sql += " AND (ct.name LIKE ? OR ct.email LIKE ? OR ct.role LIKE ?)"
            params += [f"%{search}%"] * 3
        return self._query(sql + " ORDER BY ct.name", params)

    def update_contact(self, contact_id: int, **kwargs: Any) -> None:
        self._update("contacts", contact_id, kwargs)

    def delete_contact(self, contact_id: int) -> None:
        self._delete("contacts", contact_id)

    # ── Analytics ─────────────────────────────────────────────────────────────

    def summary(self) -> dict:
        scalar = lambda sql: self._one(sql)["n"]  # noqa: E731
        return {
            "clients":      scalar("SELECT COUNT(*) AS n FROM clients"),
            "projects":     scalar("SELECT COUNT(*) AS n FROM projects"),
            "tasks":        scalar("SELECT COUNT(*) AS n FROM tasks"),
            "transactions": scalar("SELECT COUNT(*) AS n FROM transactions"),
            "contacts":     scalar("SELECT COUNT(*) AS n FROM contacts"),
            "revenue":      scalar("SELECT COALESCE(SUM(amount),0) AS n FROM transactions WHERE type='income'"),
            "expenses":     scalar("SELECT COALESCE(SUM(amount),0) AS n FROM transactions WHERE type='expense'"),
            "overdue_tasks": scalar(
                "SELECT COUNT(*) AS n FROM tasks "
                "WHERE due_date < DATE('now') AND status NOT IN ('done','cancelled')"
            ),
        }

    def revenue_by_client(self) -> list[dict]:
        return self._query("""
            SELECT c.name AS client,
                   COALESCE(SUM(CASE WHEN t.type='income'  THEN t.amount ELSE 0 END), 0) AS revenue,
                   COALESCE(SUM(CASE WHEN t.type='expense' THEN t.amount ELSE 0 END), 0) AS expenses,
                   COUNT(DISTINCT p.id) AS projects,
                   COUNT(DISTINCT tk.id) AS tasks
            FROM clients c
            LEFT JOIN projects p  ON p.client_id  = c.id
            LEFT JOIN transactions t ON t.project_id = p.id
            LEFT JOIN tasks tk    ON tk.project_id = p.id
            GROUP BY c.id
            ORDER BY revenue DESC
        """)

    def task_stats(self) -> list[dict]:
        return self._query("""
            SELECT status, priority, COUNT(*) AS count
            FROM tasks
            GROUP BY status, priority
            ORDER BY status, CASE priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1
                                           WHEN 'medium' THEN 2 ELSE 3 END
        """)

    def monthly_cashflow(self, year: int | None = None) -> list[dict]:
        where = f"WHERE strftime('%Y', date) = '{year}'" if year else ""
        return self._query(f"""
            SELECT strftime('%Y-%m', date) AS month,
                   SUM(CASE WHEN type='income'  THEN amount ELSE 0 END) AS revenue,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS expenses,
                   SUM(CASE WHEN type='income'  THEN amount ELSE -amount END) AS net
            FROM transactions {where}
            GROUP BY month
            ORDER BY month
        """)
