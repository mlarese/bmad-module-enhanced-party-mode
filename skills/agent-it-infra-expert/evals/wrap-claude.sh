#!/usr/bin/env bash
set -euo pipefail
PROMPT=${1:-}
CWD=${2:-.}
export HOME="${BMAD_EVAL_HOST_HOME:-/Users/maurolarese}"
unset CLAUDE_CONFIG_DIR || true
cd "$CWD"
exec claude -p "$PROMPT" --output-format stream-json --verbose --dangerously-skip-permissions
