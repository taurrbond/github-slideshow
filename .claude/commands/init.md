---
description: Regenerate .claude/CLAUDE.md from the current project state
---

Re-read the project structure and rewrite `.claude/CLAUDE.md` with fresh content.

Steps:

1. Inspect the repo root: list top-level files and directories, read `Gemfile`, `_config.yml`, `package.json` (if present), and any `script/` entries.
2. Determine the stack (language, frameworks, build tools, test runners) from those files.
3. Read the existing `.claude/CLAUDE.md` to preserve sections the user has customized (look for headings outside the auto-generated ones).
4. Rewrite `.claude/CLAUDE.md` keeping this structure:
   - `# CLAUDE.md — <repo name>`
   - `## Project Overview`
   - `## Stack` (table)
   - `## Project Structure` (tree)
   - `## Building & Running` (commands)
   - `## Code Style`
   - `## Testing`
   - `## Agent Instructions`
   - `## /init Command`
5. Do not invent commands that aren't in the repo. If a command is unknown, omit it rather than guess.
6. Print a short summary of what changed.

Do not touch `CLAUDE.local.md` — that is the user's personal file.
