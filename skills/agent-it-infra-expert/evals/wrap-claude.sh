#!/usr/bin/env bash
set -euo pipefail
PROMPT=${1:-}
CWD=${2:-.}

# In coda a ogni query: via le cache che il runtime si è scaricato nell'HOME
# isolato della run (Chromium & co.). Gli esiti restano, il giga di browser no.
_clean_run_caches() {
  local script
  script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/clean-caches.sh"
  [ -f "$script" ] && bash "$script" "$CWD" || true
}

export HOME="${BMAD_EVAL_HOST_HOME:-/Users/maurolarese}"
unset CLAUDE_CONFIG_DIR || true
cd "$CWD"
trap _clean_run_caches EXIT
claude -p "$PROMPT" --output-format stream-json --verbose --dangerously-skip-permissions
