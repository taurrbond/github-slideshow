# .claude/ — Claude Code configuration for github-slideshow

Everything in this folder is loaded automatically when Claude Code starts in this
repository. Below is what each piece does and how they wire together.

## Layout

```
.claude/
├── README.md            — this file
├── settings.json        — permissions + Claude Code hooks (auto-loaded)
├── CLAUDE.md            — project context shown to the agent every session
├── CLAUDE.local.md      — personal overrides (gitignored)
├── commands/
│   ├── init.md          — /init        regenerate CLAUDE.md
│   └── code-review.md   — /code-review run the code-review skill on the diff
├── skills/
│   └── code-review/
│       └── SKILL.md     — checklist + output format for reviews
└── hooks/
    └── pre-commit       — git hook: prettier + rubocop + jekyll build
```

## How it integrates

1. **`settings.json` → permissions** — controls which Bash/Edit calls the agent
   can make without prompting. Anything destructive (`curl`, `rm -rf`, `.env`
   writes) is denied.

2. **`settings.json` → hooks**
    - `SessionStart` runs `git config core.hooksPath .claude/hooks`, so the
      versioned `pre-commit` hook activates automatically the first time you
      open the repo with Claude Code. No manual `cp` step.
    - `PostToolUse` on `Edit|Write` formats the file the agent just touched
      (prettier for web files, rubocop for Ruby). Silent if the formatter
      isn't installed.

3. **`CLAUDE.md`** is read into the agent's context every session, so the
   stack, build commands, and house rules are always known.

4. **`commands/*.md`** become slash commands (`/init`, `/code-review`).
   `/code-review` delegates to the skill so the logic lives in one place.

5. **`skills/code-review/SKILL.md`** is the actual review playbook —
   invoked by the slash command or by asking the agent to "do a code review".

6. **`hooks/pre-commit`** runs on every `git commit` (once `core.hooksPath`
   is wired). Checks staged files with prettier/rubocop and runs a Jekyll
   smoke-build if config/layouts/posts changed.

## Manual setup (if SessionStart hook didn't fire)

```bash
git config core.hooksPath .claude/hooks
chmod +x .claude/hooks/pre-commit
```

## Personal settings

Put anything you don't want committed in `CLAUDE.local.md` — it's listed in
`.gitignore` and merged on top of `CLAUDE.md` for your local sessions.
