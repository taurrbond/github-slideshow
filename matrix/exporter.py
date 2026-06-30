"""CSV and Excel export/import for the Matrix database."""
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from matrix import MatrixDB

TABLES = ("clients", "projects", "tasks", "transactions", "contacts")


class MatrixExporter:
    def __init__(self, db: "MatrixDB"):
        self.db = db

    def _load(self, table: str) -> pd.DataFrame:
        rows = self.db._query(f"SELECT * FROM {table}")
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    # ── CSV ───────────────────────────────────────────────────────────────────

    def to_csv(self, table: str, path: Path) -> None:
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")
        df = self._load(table)
        df.to_csv(path, index=False, encoding="utf-8-sig")

    def from_csv(self, table: str, path: Path) -> int:
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")
        df = pd.read_csv(path, encoding="utf-8-sig")
        # Drop system columns so INSERT auto-generates them
        df = df.drop(columns=[c for c in ("id", "created_at", "updated_at") if c in df.columns])
        count = 0
        for _, row in df.iterrows():
            data = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            self.db._insert(table, data)
            count += 1
        return count

    # ── Excel ─────────────────────────────────────────────────────────────────

    def to_excel(self, path: Path) -> None:
        """Write all tables to separate sheets in one .xlsx file."""
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            # Summary sheet
            summary = self.db.summary()
            pd.DataFrame(list(summary.items()), columns=["Metric", "Value"]).to_excel(
                writer, sheet_name="Summary", index=False
            )
            # Revenue by client
            pd.DataFrame(self.db.revenue_by_client()).to_excel(
                writer, sheet_name="Revenue_by_Client", index=False
            )
            # Monthly cashflow
            pd.DataFrame(self.db.monthly_cashflow()).to_excel(
                writer, sheet_name="Monthly_Cashflow", index=False
            )
            # Raw tables
            for table in TABLES:
                df = self._load(table)
                if not df.empty:
                    df.to_excel(writer, sheet_name=table.capitalize(), index=False)

    def from_excel(self, path: Path, sheet: str, table: str) -> int:
        """Import a single sheet from an Excel file into a table."""
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")
        df = pd.read_excel(path, sheet_name=sheet)
        df = df.drop(columns=[c for c in ("id", "created_at", "updated_at") if c in df.columns])
        count = 0
        for _, row in df.iterrows():
            data = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            self.db._insert(table, data)
            count += 1
        return count

    # ── JSON ──────────────────────────────────────────────────────────────────

    def to_json(self, path: Path) -> None:
        """Export full matrix to a single JSON file."""
        import json
        data = {table: self.db._query(f"SELECT * FROM {table}") for table in TABLES}
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def from_json(self, path: Path) -> dict[str, int]:
        """Import from a JSON file produced by to_json. Returns counts per table."""
        import json
        data = json.loads(path.read_text(encoding="utf-8"))
        counts = {}
        for table, rows in data.items():
            if table not in TABLES:
                continue
            count = 0
            for row in rows:
                row.pop("id", None)
                row.pop("created_at", None)
                row.pop("updated_at", None)
                self.db._insert(table, row)
                count += 1
            counts[table] = count
        return counts
