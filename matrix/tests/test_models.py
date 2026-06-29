"""Tests for Pydantic validation models."""
import sys
from pathlib import Path
import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    ClientCreate, ProjectCreate, TaskCreate,
    TransactionCreate, ContactCreate,
)


class TestClientValidation:
    def test_valid_client(self):
        c = ClientCreate(name="Acme", email="ceo@acme.com", status="active")
        assert c.name == "Acme"

    def test_name_required(self):
        with pytest.raises(ValidationError):
            ClientCreate()

    def test_name_empty_string_rejected(self):
        with pytest.raises(ValidationError):
            ClientCreate(name="")

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            ClientCreate(name="X", status="deleted")

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            ClientCreate(name="X", email="not-an-email")

    def test_optional_fields_default_none(self):
        c = ClientCreate(name="Min")
        assert c.email is None and c.phone is None


class TestProjectValidation:
    def test_valid_project(self):
        p = ProjectCreate(client_id=1, name="Alpha", budget=1000, start_date="2024-01-01")
        assert p.budget == 1000

    def test_negative_budget_rejected(self):
        with pytest.raises(ValidationError):
            ProjectCreate(client_id=1, name="X", budget=-100)

    def test_end_before_start_rejected(self):
        with pytest.raises(ValidationError):
            ProjectCreate(
                client_id=1, name="X",
                start_date="2024-06-01", end_date="2024-01-01",
            )

    def test_invalid_date_format(self):
        with pytest.raises(ValidationError):
            ProjectCreate(client_id=1, name="X", start_date="01-01-2024")

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            ProjectCreate(client_id=1, name="X", status="unknown")


class TestTaskValidation:
    def test_valid_task(self):
        t = TaskCreate(project_id=1, title="Do something", priority="high")
        assert t.status == "todo"

    def test_title_required(self):
        with pytest.raises(ValidationError):
            TaskCreate(project_id=1, title="")

    def test_invalid_priority(self):
        with pytest.raises(ValidationError):
            TaskCreate(project_id=1, title="X", priority="urgent")

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            TaskCreate(project_id=1, title="X", status="backlog")


class TestTransactionValidation:
    def test_valid_income(self):
        t = TransactionCreate(project_id=1, amount=500.0, type="income")
        assert t.amount == 500.0

    def test_zero_amount_rejected(self):
        with pytest.raises(ValidationError):
            TransactionCreate(project_id=1, amount=0)

    def test_negative_amount_rejected(self):
        with pytest.raises(ValidationError):
            TransactionCreate(project_id=1, amount=-100)

    def test_invalid_type(self):
        with pytest.raises(ValidationError):
            TransactionCreate(project_id=1, amount=100, type="transfer")

    def test_currency_max_length(self):
        with pytest.raises(ValidationError):
            TransactionCreate(project_id=1, amount=100, currency="USDA")


class TestContactValidation:
    def test_valid_contact(self):
        c = ContactCreate(client_id=1, name="Jane Doe", role="CFO")
        assert c.role == "CFO"

    def test_name_required(self):
        with pytest.raises(ValidationError):
            ContactCreate(client_id=1, name="")
