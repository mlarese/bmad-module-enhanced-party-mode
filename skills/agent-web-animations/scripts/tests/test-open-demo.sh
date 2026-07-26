#!/usr/bin/env bash
# Smoke test for open-demo.sh — does not require a GUI; checks path resolution.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DEMO="$ROOT/demo/index.html"
[[ -f "$DEMO" ]] || { echo "FAIL: missing $DEMO"; exit 1; }
# Dry-run: script echoes path; on CI without open, still should find demo
OUT=$(bash "$ROOT/scripts/open-demo.sh" 2>&1 || true)
echo "$OUT" | grep -q "Web Animations demo:" || { echo "FAIL: unexpected output: $OUT"; exit 1; }
echo "PASS: open-demo resolves demo path"
