#!/usr/bin/env bash
# Auth + transcript bridge for BMAD evals on Codex CLI.
# Restores host CODEX_HOME for auth while keeping the case cwd as workspace.
# Translates Codex JSONL events into Claude-compatible assistant/tool_use
# lines so run_triggers detect_load and the grader can read them.
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

HOST_HOME="${BMAD_EVAL_HOST_HOME:-/Users/maurolarese}"
export CODEX_HOME="${CODEX_HOME:-$HOST_HOME/.codex}"
cd "$CWD"

RAW=$(mktemp)
trap 'rm -f "$RAW"; _clean_run_caches' EXIT

# Prompt as argv; never consume host stdin (avoids "Reading additional input…").
codex exec \
  --json \
  --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -C "$CWD" \
  "$PROMPT" </dev/null >"$RAW" 2>/dev/null || true

python3 - "$RAW" <<'PY'
import json, sys, re
from pathlib import Path

raw_path = Path(sys.argv[1])
text = raw_path.read_text(encoding="utf-8", errors="replace") if raw_path.is_file() else ""

def emit_assistant_text(t: str) -> None:
    print(json.dumps({
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [{"type": "text", "text": t}],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    }, ensure_ascii=False))

def emit_tool(name: str, inp: dict) -> None:
    print(json.dumps({
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "tool", "name": name, "input": inp}],
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    }, ensure_ascii=False))

skill_path_re = re.compile(r"[^\s'\"]+\.agents/skills/([A-Za-z0-9._-]+)(?:/[^\s'\"]*)?")
input_tokens = 0
output_tokens = 0
saw_any = False

for line in text.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        evt = json.loads(line)
    except json.JSONDecodeError:
        continue
    if not isinstance(evt, dict):
        continue
    et = evt.get("type")
    item = evt.get("item") if isinstance(evt.get("item"), dict) else {}

    if et == "item.completed" and item.get("type") == "agent_message":
        saw_any = True
        emit_assistant_text(item.get("text") or "")
    elif et in ("item.started", "item.completed") and item.get("type") == "command_execution":
        cmd = item.get("command") or ""
        saw_any = True
        emit_tool("Bash", {"command": cmd})
        # Codex often "loads" a skill by reading SKILL.md via shell — count as Read.
        for m in skill_path_re.finditer(cmd):
            name = m.group(1)
            emit_tool("Read", {"file_path": f".agents/skills/{name}/SKILL.md"})
        # Also catch explicit path fragments without regex group issues
        if "/SKILL.md" in cmd and ".agents/skills/" in cmd:
            pass  # already handled above when possible
    elif et == "item.completed" and item.get("type") == "file_change":
        saw_any = True
        paths = item.get("paths") or item.get("files") or []
        if isinstance(paths, list):
            for p in paths:
                emit_tool("Write", {"file_path": str(p), "content": ""})
    elif et == "turn.completed":
        usage = evt.get("usage") or {}
        input_tokens = int(usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)

# Always emit a result line for token accounting.
print(json.dumps({
    "type": "result",
    "subtype": "success",
    "is_error": not saw_any,
    "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
    "result": "",
}, ensure_ascii=False))
PY
