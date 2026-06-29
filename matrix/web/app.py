"""Flask REST API + web dashboard для Matrix Data."""
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, jsonify, request, render_template, send_file
from pydantic import ValidationError

from matrix import MatrixDB
from models import (
    ClientCreate, ClientUpdate,
    ProjectCreate, ProjectUpdate,
    TaskCreate, TaskUpdate,
    TransactionCreate, TransactionUpdate,
    ContactCreate, ContactUpdate,
)
from exporter import MatrixExporter

DB_PATH = Path(__file__).parent.parent / "matrix.db"

app = Flask(__name__)


def db():
    return MatrixDB(DB_PATH)


def _err(e: Exception, code: int = 400):
    return jsonify({"error": str(e)}), code


def _validate(model_cls, data: dict):
    try:
        return model_cls(**data).model_dump(exclude_none=True), None
    except ValidationError as e:
        return None, jsonify({"error": e.errors()}), 422


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Summary ───────────────────────────────────────────────────────────────────

@app.route("/api/summary")
def api_summary():
    with db() as d:
        return jsonify(d.summary())


@app.route("/api/analytics/revenue")
def api_revenue():
    with db() as d:
        return jsonify(d.revenue_by_client())


@app.route("/api/analytics/cashflow")
def api_cashflow():
    year = request.args.get("year", type=int)
    with db() as d:
        return jsonify(d.monthly_cashflow(year=year))


@app.route("/api/analytics/tasks")
def api_task_stats():
    with db() as d:
        return jsonify(d.task_stats())


# ── Clients ───────────────────────────────────────────────────────────────────

@app.route("/api/clients", methods=["GET", "POST"])
def clients():
    if request.method == "GET":
        with db() as d:
            return jsonify(d.get_clients(
                status=request.args.get("status"),
                search=request.args.get("search"),
            ))
    validated, err = _validate(ClientCreate, request.json or {})
    if err:
        return err
    with db() as d:
        row_id = d.add_client(**validated)
    return jsonify({"id": row_id}), 201


@app.route("/api/clients/<int:cid>", methods=["GET", "PUT", "DELETE"])
def client(cid):
    if request.method == "GET":
        with db() as d:
            row = d.get_client(cid)
        return jsonify(row) if row else ("Not found", 404)
    if request.method == "PUT":
        validated, err = _validate(ClientUpdate, request.json or {})
        if err:
            return err
        with db() as d:
            d.update_client(cid, **validated)
        return jsonify({"ok": True})
    with db() as d:
        d.delete_client(cid)
    return jsonify({"ok": True})


# ── Projects ──────────────────────────────────────────────────────────────────

@app.route("/api/projects", methods=["GET", "POST"])
def projects():
    if request.method == "GET":
        with db() as d:
            return jsonify(d.get_projects(
                client_id=request.args.get("client_id", type=int),
                status=request.args.get("status"),
                search=request.args.get("search"),
            ))
    validated, err = _validate(ProjectCreate, request.json or {})
    if err:
        return err
    with db() as d:
        row_id = d.add_project(**validated)
    return jsonify({"id": row_id}), 201


@app.route("/api/projects/<int:pid>", methods=["GET", "PUT", "DELETE"])
def project(pid):
    if request.method == "GET":
        with db() as d:
            row = d.get_project(pid)
        return jsonify(row) if row else ("Not found", 404)
    if request.method == "PUT":
        validated, err = _validate(ProjectUpdate, request.json or {})
        if err:
            return err
        with db() as d:
            d.update_project(pid, **validated)
        return jsonify({"ok": True})
    with db() as d:
        d.delete_project(pid)
    return jsonify({"ok": True})


# ── Tasks ─────────────────────────────────────────────────────────────────────

@app.route("/api/tasks", methods=["GET", "POST"])
def tasks():
    if request.method == "GET":
        with db() as d:
            return jsonify(d.get_tasks(
                project_id=request.args.get("project_id", type=int),
                status=request.args.get("status"),
                assignee=request.args.get("assignee"),
                priority=request.args.get("priority"),
                overdue=request.args.get("overdue") == "true",
            ))
    validated, err = _validate(TaskCreate, request.json or {})
    if err:
        return err
    with db() as d:
        row_id = d.add_task(**validated)
    return jsonify({"id": row_id}), 201


@app.route("/api/tasks/<int:tid>", methods=["GET", "PUT", "DELETE"])
def task(tid):
    if request.method == "GET":
        with db() as d:
            row = d.get_task(tid)
        return jsonify(row) if row else ("Not found", 404)
    if request.method == "PUT":
        validated, err = _validate(TaskUpdate, request.json or {})
        if err:
            return err
        with db() as d:
            d.update_task(tid, **validated)
        return jsonify({"ok": True})
    with db() as d:
        d.delete_task(tid)
    return jsonify({"ok": True})


# ── Transactions ──────────────────────────────────────────────────────────────

@app.route("/api/transactions", methods=["GET", "POST"])
def transactions():
    if request.method == "GET":
        with db() as d:
            return jsonify(d.get_transactions(
                project_id=request.args.get("project_id", type=int),
                tx_type=request.args.get("type"),
                category=request.args.get("category"),
                date_from=request.args.get("from"),
                date_to=request.args.get("to"),
            ))
    data = request.json or {}
    validated, err = _validate(TransactionCreate, data)
    if err:
        return err
    tx_type = validated.pop("type", "income")
    with db() as d:
        row_id = d.add_transaction(tx_type=tx_type, **validated)
    return jsonify({"id": row_id}), 201


@app.route("/api/transactions/<int:tid>", methods=["GET", "PUT", "DELETE"])
def transaction(tid):
    if request.method == "GET":
        with db() as d:
            rows = d._query("SELECT * FROM transactions WHERE id = ?", [tid])
        return jsonify(rows[0]) if rows else ("Not found", 404)
    if request.method == "PUT":
        validated, err = _validate(TransactionUpdate, request.json or {})
        if err:
            return err
        with db() as d:
            d.update_transaction(tid, **validated)
        return jsonify({"ok": True})
    with db() as d:
        d.delete_transaction(tid)
    return jsonify({"ok": True})


# ── Contacts ──────────────────────────────────────────────────────────────────

@app.route("/api/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "GET":
        with db() as d:
            return jsonify(d.get_contacts(
                client_id=request.args.get("client_id", type=int),
                search=request.args.get("search"),
            ))
    validated, err = _validate(ContactCreate, request.json or {})
    if err:
        return err
    with db() as d:
        row_id = d.add_contact(**validated)
    return jsonify({"id": row_id}), 201


@app.route("/api/contacts/<int:cid>", methods=["GET", "PUT", "DELETE"])
def contact_detail(cid):
    if request.method == "PUT":
        validated, err = _validate(ContactUpdate, request.json or {})
        if err:
            return err
        with db() as d:
            d.update_contact(cid, **validated)
        return jsonify({"ok": True})
    with db() as d:
        d.delete_contact(cid)
    return jsonify({"ok": True})


# ── Export ────────────────────────────────────────────────────────────────────

@app.route("/api/export/csv/<table>")
def export_csv(table):
    buf = io.StringIO()
    with db() as d:
        exp = MatrixExporter(d)
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            tmp = Path(f.name)
        exp.to_csv(table, tmp)
        content = tmp.read_text(encoding="utf-8-sig")
        os.unlink(tmp)
    return app.response_class(
        content, mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{table}.csv"'},
    )


@app.route("/api/export/excel")
def export_excel():
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        tmp = Path(f.name)
    with db() as d:
        MatrixExporter(d).to_excel(tmp)
    data = tmp.read_bytes()
    os.unlink(tmp)
    return app.response_class(
        data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="matrix_export.xlsx"'},
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
