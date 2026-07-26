#!/usr/bin/env bash
# Auth bridge for BMAD eval isolation. Claude Code login resolves via host
# $HOME/.claude.json (and keychain). Restore host HOME for auth while keeping
# the case cwd as the working directory so staged skills under cwd/.claude/skills
# remain discoverable.
set -euo pipefail
PROMPT=${1:-}
CWD=${2:-.}
export HOME="${BMAD_EVAL_HOST_HOME:-/Users/maurolarese}"
unset CLAUDE_CONFIG_DIR || true
cd "$CWD"
exec claude -p "$PROMPT" --output-format stream-json --verbose --dangerously-skip-permissions
