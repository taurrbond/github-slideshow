-- Matrix Data Schema — 5 связанных сущностей
-- Включает FK constraints, CHECK-валидацию и индексы

CREATE TABLE IF NOT EXISTS clients (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    UNIQUE,
    phone      TEXT,
    status     TEXT    NOT NULL DEFAULT 'active'
                       CHECK(status IN ('active','inactive','prospect')),
    notes      TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id   INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    description TEXT,
    status      TEXT    NOT NULL DEFAULT 'active'
                        CHECK(status IN ('active','completed','paused','cancelled')),
    budget      REAL    CHECK(budget IS NULL OR budget >= 0),
    start_date  TEXT,
    end_date    TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    description TEXT,
    assignee    TEXT,
    status      TEXT    NOT NULL DEFAULT 'todo'
                        CHECK(status IN ('todo','in_progress','review','done','cancelled')),
    priority    TEXT    NOT NULL DEFAULT 'medium'
                        CHECK(priority IN ('low','medium','high','critical')),
    due_date    TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    amount      REAL    NOT NULL CHECK(amount > 0),
    type        TEXT    NOT NULL DEFAULT 'income'
                        CHECK(type IN ('income','expense')),
    category    TEXT,
    description TEXT,
    currency    TEXT    NOT NULL DEFAULT 'USD',
    date        TEXT    NOT NULL DEFAULT (date('now')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS contacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id   INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    role        TEXT,
    email       TEXT,
    phone       TEXT,
    notes       TEXT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_client     ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status     ON projects(status);
CREATE INDEX IF NOT EXISTS idx_tasks_project       ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status        ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee      ON tasks(assignee);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date      ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_transactions_proj   ON transactions(project_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date   ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type   ON transactions(type);
CREATE INDEX IF NOT EXISTS idx_contacts_client     ON contacts(client_id);
