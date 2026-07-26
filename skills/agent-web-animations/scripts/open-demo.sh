#!/usr/bin/env bash
# Apre la pagina demo completa degli effetti (repeat).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO="$ROOT/demo/index.html"

if [[ ! -f "$DEMO" ]]; then
  echo "Demo non trovata: $DEMO" >&2
  exit 1
fi

echo "Web Animations demo: $DEMO"
if command -v open >/dev/null 2>&1; then
  open "$DEMO"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$DEMO"
else
  echo "Apri manualmente nel browser: file://$DEMO"
fi
