"""Pydantic models for Matrix entity validation. Used before every DB write."""
from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


DATE_RE = r"^\d{4}-\d{2}-\d{2}$"


class ClientCreate(BaseModel):
    name:   str            = Field(..., min_length=1, max_length=255)
    email:  Optional[str]  = None
    phone:  Optional[str]  = None
    status: Literal["active", "inactive", "prospect"] = "active"
    notes:  Optional[str]  = None

    @field_validator("email")
    @classmethod
    def email_format(cls, v: str | None) -> str | None:
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v


class ClientUpdate(BaseModel):
    name:   Optional[str]  = Field(None, min_length=1, max_length=255)
    email:  Optional[str]  = None
    phone:  Optional[str]  = None
    status: Optional[Literal["active", "inactive", "prospect"]] = None
    notes:  Optional[str]  = None


class ProjectCreate(BaseModel):
    client_id:   int           = Field(..., ge=1)
    name:        str           = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status:      Literal["active", "completed", "paused", "cancelled"] = "active"
    budget:      Optional[float] = Field(None, ge=0)
    start_date:  Optional[str]   = Field(None, pattern=DATE_RE)
    end_date:    Optional[str]   = Field(None, pattern=DATE_RE)

    @model_validator(mode="after")
    def end_after_start(self) -> "ProjectCreate":
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        return self


class ProjectUpdate(BaseModel):
    name:        Optional[str]   = Field(None, min_length=1, max_length=255)
    description: Optional[str]   = None
    status:      Optional[Literal["active", "completed", "paused", "cancelled"]] = None
    budget:      Optional[float]  = Field(None, ge=0)
    start_date:  Optional[str]    = Field(None, pattern=DATE_RE)
    end_date:    Optional[str]    = Field(None, pattern=DATE_RE)


class TaskCreate(BaseModel):
    project_id:  int           = Field(..., ge=1)
    title:       str           = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    assignee:    Optional[str] = None
    status:      Literal["todo", "in_progress", "review", "done", "cancelled"] = "todo"
    priority:    Literal["low", "medium", "high", "critical"] = "medium"
    due_date:    Optional[str] = Field(None, pattern=DATE_RE)


class TaskUpdate(BaseModel):
    title:       Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    assignee:    Optional[str] = None
    status:      Optional[Literal["todo", "in_progress", "review", "done", "cancelled"]] = None
    priority:    Optional[Literal["low", "medium", "high", "critical"]] = None
    due_date:    Optional[str] = Field(None, pattern=DATE_RE)


class TransactionCreate(BaseModel):
    project_id:  int           = Field(..., ge=1)
    amount:      float         = Field(..., gt=0)
    type:        Literal["income", "expense"] = "income"
    category:    Optional[str] = None
    description: Optional[str] = None
    currency:    str           = Field("USD", min_length=3, max_length=3)
    date:        Optional[str] = Field(None, pattern=DATE_RE)


class TransactionUpdate(BaseModel):
    amount:      Optional[float] = Field(None, gt=0)
    type:        Optional[Literal["income", "expense"]] = None
    category:    Optional[str]   = None
    description: Optional[str]   = None
    currency:    Optional[str]   = Field(None, min_length=3, max_length=3)
    date:        Optional[str]   = Field(None, pattern=DATE_RE)


class ContactCreate(BaseModel):
    client_id: int           = Field(..., ge=1)
    name:      str           = Field(..., min_length=1)
    role:      Optional[str] = None
    email:     Optional[str] = None
    phone:     Optional[str] = None
    notes:     Optional[str] = None


class ContactUpdate(BaseModel):
    name:  Optional[str] = Field(None, min_length=1)
    role:  Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
