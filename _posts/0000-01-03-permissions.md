---
layout: slide
title: "Шаг 1: Управление разрешениями"
---

## ⚙️ Шаг 1: Управление разрешениями

Настройте `.claude/settings.json` вместо бесконечных нажатий `y`:

```json
{
  "permissions": {
    "allow": ["Bash(pytest *)", "Bash(uv run *)"],
    "deny":  ["Bash(curl *)", "Read(./.env)"]
  }
}
```

**Порядок применения:** `deny` → `ask` → `allow`
