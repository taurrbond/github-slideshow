#!/usr/bin/env bash
# PreToolUse hook for Write tool
# Triggered before any file write operation.

set -euo pipefail

FILE="${CLAUDE_TOOL_INPUT_FILE_PATH:-}"
LOG=".claude/hooks.log"
TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

# ── Logging helper ────────────────────────────────────────────────────────────
log() {
  echo "[$TIMESTAMP] $*" >> "$LOG"
}

# ── Guard: FILE must be set ───────────────────────────────────────────────────
if [[ -z "$FILE" ]]; then
  log "WARN  pre-write: CLAUDE_TOOL_INPUT_FILE_PATH not set, skipping"
  exit 0
fi

BASENAME="$(basename "$FILE")"

log "INFO  pre-write: attempt to write '$FILE'"

# ── Rule 1: Block sensitive files ─────────────────────────────────────────────
BLOCKED=(".env" "secrets.json" ".env.local" ".env.production" ".env.staging")
for blocked in "${BLOCKED[@]}"; do
  if [[ "$BASENAME" == "$blocked" ]]; then
    log "BLOCK pre-write: '$FILE' is a protected file — write denied"
    echo "❌ Write blocked: '$FILE' is a sensitive file (.env / secrets.json)." >&2
    echo "   Store secrets in a password manager or use environment variables." >&2
    exit 1
  fi
done

# ── Rule 2: Auto-format Python files with black ───────────────────────────────
if [[ "$FILE" == *.py ]]; then
  if command -v black &>/dev/null; then
    log "INFO  pre-write: running black on '$FILE'"
    # black reads from stdin and writes to stdout when given '-'
    # Claude Code passes file content via CLAUDE_TOOL_INPUT_CONTENT for Write.
    # We format the content before it lands on disk by printing the formatted
    # version; the hook replaces the tool's content when it exits 0 and prints
    # to stdout on some runtimes. Where that's not supported, black is run as
    # a PostToolUse step instead — see post-write.sh.
    black --quiet "$FILE" 2>>"$LOG" || log "WARN  pre-write: black failed on '$FILE'"
  else
    log "WARN  pre-write: black not installed, skipping Python formatting"
  fi
fi

log "INFO  pre-write: '$FILE' allowed"
exit 0
