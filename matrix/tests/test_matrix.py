"""Tests for MatrixDB core CRUD and analytics operations."""
import tempfile
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from matrix import MatrixDB


@pytest.fixture
def db(tmp_path):
    """Fresh in-memory-style DB per test (temp file, auto-deleted)."""
    db_file = tmp_path / "test.db"
    with MatrixDB(db_file) as d:
        yield d


@pytest.fixture
def seeded(db):
    """DB with one client, project, task, transaction, and contact."""
    client_id = db.add_client("Acme Corp", email="acme@example.com", status="active")
    project_id = db.add_project(client_id, "Website Relaunch", budget=50000, status="active")
    task_id = db.add_task(project_id, "Design mockups", assignee="Alice", priority="high")
    tx_id = db.add_transaction(project_id, 10000, tx_type="income", category="development")
    contact_id = db.add_contact(client_id, "Bob Smith", role="CTO", email="bob@acme.com")
    return {
        "db": db,
        "client_id": client_id,
        "project_id": project_id,
        "task_id": task_id,
        "tx_id": tx_id,
        "contact_id": contact_id,
    }


# ── Clients ───────────────────────────────────────────────────────────────────

class TestClients:
    def test_add_and_get(self, db):
        row_id = db.add_client("Test Corp", email="test@corp.com")
        assert isinstance(row_id, int) and row_id > 0
        row = db.get_client(row_id)
        assert row["name"] == "Test Corp"
        assert row["email"] == "test@corp.com"
        assert row["status"] == "active"

    def test_list_all(self, db):
        db.add_client("A"), db.add_client("B")
        assert len(db.get_clients()) == 2

    def test_filter_by_status(self, db):
        db.add_client("Active One", status="active")
        db.add_client("Prospect One", status="prospect")
        active = db.get_clients(status="active")
        assert all(r["status"] == "active" for r in active)

    def test_search(self, db):
        db.add_client("Searchable Inc", email="find@me.com")
        db.add_client("Other Corp")
        results = db.get_clients(search="Searchable")
        assert len(results) == 1
        assert results[0]["name"] == "Searchable Inc"

    def test_update(self, db):
        row_id = db.add_client("Old Name")
        db.update_client(row_id, name="New Name", status="inactive")
        row = db.get_client(row_id)
        assert row["name"] == "New Name"
        assert row["status"] == "inactive"

    def test_delete(self, db):
        row_id = db.add_client("To Delete")
        db.delete_client(row_id)
        assert db.get_client(row_id) is None

    def test_get_nonexistent_returns_none(self, db):
        assert db.get_client(9999) is None


# ── Projects ──────────────────────────────────────────────────────────────────

class TestProjects:
    def test_add_and_get(self, seeded):
        db = seeded["db"]
        project = db.get_project(seeded["project_id"])
        assert project["name"] == "Website Relaunch"
        assert project["client_name"] == "Acme Corp"
        assert project["budget"] == 50000

    def test_cascade_delete(self, seeded):
        db = seeded["db"]
        db.delete_client(seeded["client_id"])
        projects = db.get_projects()
        assert len(projects) == 0

    def test_filter_by_status(self, seeded):
        db, cid = seeded["db"], seeded["client_id"]
        db.add_project(cid, "Completed Project", status="completed")
        active = db.get_projects(status="active")
        assert all(p["status"] == "active" for p in active)


# ── Tasks ─────────────────────────────────────────────────────────────────────

class TestTasks:
    def test_add_and_get(self, seeded):
        task = seeded["db"].get_task(seeded["task_id"])
        assert task["title"] == "Design mockups"
        assert task["priority"] == "high"
        assert task["project_name"] == "Website Relaunch"

    def test_priority_ordering(self, seeded):
        db, pid = seeded["db"], seeded["project_id"]
        db.add_task(pid, "Low prio", priority="low")
        db.add_task(pid, "Critical task", priority="critical")
        tasks = db.get_tasks(project_id=pid)
        # critical comes first
        assert tasks[0]["priority"] == "critical"

    def test_overdue_filter(self, seeded):
        db, pid = seeded["db"], seeded["project_id"]
        db.add_task(pid, "Overdue task", due_date="2000-01-01", status="todo")
        overdue = db.get_tasks(overdue=True)
        assert any(t["title"] == "Overdue task" for t in overdue)

    def test_done_task_not_in_overdue(self, seeded):
        db, pid = seeded["db"], seeded["project_id"]
        tid = db.add_task(pid, "Old done task", due_date="2000-01-01", status="done")
        overdue = db.get_tasks(overdue=True)
        assert not any(t["id"] == tid for t in overdue)

    def test_update_status(self, seeded):
        db, tid = seeded["db"], seeded["task_id"]
        db.update_task(tid, status="done")
        task = db.get_task(tid)
        assert task["status"] == "done"


# ── Transactions ──────────────────────────────────────────────────────────────

class TestTransactions:
    def test_add_income(self, seeded):
        rows = seeded["db"].get_transactions(tx_type="income")
        assert any(t["amount"] == 10000 for t in rows)

    def test_date_filter(self, seeded):
        db, pid = seeded["db"], seeded["project_id"]
        db.add_transaction(pid, 500, tx_type="expense", date="2023-01-15")
        results = db.get_transactions(date_from="2023-01-01", date_to="2023-12-31")
        assert all("2023" in t["date"] for t in results)


# ── Analytics ─────────────────────────────────────────────────────────────────

class TestAnalytics:
    def test_summary_counts(self, seeded):
        s = seeded["db"].summary()
        assert s["clients"] == 1
        assert s["projects"] == 1
        assert s["tasks"] == 1
        assert s["transactions"] == 1
        assert s["contacts"] == 1

    def test_revenue_calculation(self, seeded):
        db, pid = seeded["db"], seeded["project_id"]
        db.add_transaction(pid, 2000, tx_type="expense")
        s = db.summary()
        assert s["revenue"] == 10000
        assert s["expenses"] == 2000

    def test_revenue_by_client(self, seeded):
        rows = seeded["db"].revenue_by_client()
        assert any(r["client"] == "Acme Corp" and r["revenue"] == 10000 for r in rows)

    def test_monthly_cashflow_structure(self, seeded):
        rows = seeded["db"].monthly_cashflow()
        assert len(rows) >= 1
        assert "month" in rows[0] and "net" in rows[0]
