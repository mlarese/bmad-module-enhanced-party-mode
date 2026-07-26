#!/usr/bin/env bash
# Smoke test for analyze-site.sh — usage and local HTML fixture.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/scripts/analyze-site.sh"

# Usage without args should fail
if bash "$SCRIPT" >/dev/null 2>&1; then
  echo "FAIL: expected non-zero without args"
  exit 1
fi
echo "PASS: usage without args"

# Local file:// may fail download; use a tiny http fixture via python
TMP=$(mktemp -d)
python3 - <<PY &
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
os.chdir("$TMP")
open("index.html","w").write("<html><script src='gsap.min.js'></script><style>@keyframes fade{}</style></html>")
open("gsap.min.js","w").write("// gsap")
HTTPServer(("127.0.0.1", 8765), SimpleHTTPRequestHandler).handle_request()
PY
PID=$!
sleep 0.3
OUTDIR=$(mktemp -d)
bash "$SCRIPT" "http://127.0.0.1:8765/index.html" "$OUTDIR" >/tmp/anim-analyze-out.txt 2>&1 || true
wait "$PID" 2>/dev/null || true
if ! grep -qi "GSAP\|Librerie\|gsap" /tmp/anim-analyze-out.txt "$OUTDIR"/* 2>/dev/null; then
  # At least page should download
  [[ -f "$OUTDIR/page.html" ]] || { echo "FAIL: no page.html"; cat /tmp/anim-analyze-out.txt; exit 1; }
fi
echo "PASS: analyze-site downloads page"
rm -rf "$TMP" "$OUTDIR"
