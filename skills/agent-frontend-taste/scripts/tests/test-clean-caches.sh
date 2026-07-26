#!/usr/bin/env bash
# Test per evals/clean-caches.sh — run: bash scripts/tests/test-clean-caches.sh
#
# La pulizia gira in coda a OGNI query di ogni eval, con i permessi di chi
# lancia: quindi i test che contano non sono «cancella», ma «non cancella
# quello che non deve» e «si rifiuta di lavorare dove non deve».
set -uo pipefail

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../evals" && pwd)/clean-caches.sh"
FAILS=0

check() {  # check <label> <atteso> <ottenuto>
  if [ "$2" = "$3" ]; then echo "PASS: $1"; else
    echo "FAIL: $1"; echo "  atteso: $2"; echo "  ottenuto: $3"; FAILS=$((FAILS + 1)); fi
}

TD=$(mktemp -d)
trap 'rm -rf "$TD"' EXIT

# --- la cache sparisce, il resto della run no ------------------------------
mkdir -p "$TD/stage/.home/Library/Caches/ms-playwright/chromium-1223" \
         "$TD/stage/.home/.cache/puppeteer" \
         "$TD/stage/.home/Library/Application Support/codex" \
         "$TD/stage/apps/demo"
dd if=/dev/zero of="$TD/stage/.home/Library/Caches/ms-playwright/chromium-1223/blob" \
   bs=1024 count=2048 2>/dev/null
echo '{"ok":true}' > "$TD/stage/timing.json"
echo "sessione" > "$TD/stage/.home/Library/Application Support/codex/state.json"
echo "<html>" > "$TD/stage/apps/demo/index.html"

bash "$SCRIPT" "$TD/stage" 2>/dev/null
check "la cache di Chromium è rimossa" "0" "$(find "$TD/stage" -name ms-playwright | wc -l | tr -d ' ')"
check "la cache di puppeteer è rimossa" "0" "$(find "$TD/stage" -name puppeteer | wc -l | tr -d ' ')"
check "l'esito della run resta" "1" "$(ls "$TD/stage/timing.json" 2>/dev/null | wc -l | tr -d ' ')"
check "i file prodotti dalla query restano" "1" \
      "$(ls "$TD/stage/apps/demo/index.html" 2>/dev/null | wc -l | tr -d ' ')"
check "il resto dell'HOME isolato resta" "1" \
      "$(ls "$TD/stage/.home/Library/Application Support/codex/state.json" 2>/dev/null | wc -l | tr -d ' ')"

# --- idempotente: rilanciarla non è un errore ------------------------------
bash "$SCRIPT" "$TD/stage" 2>/dev/null
check "seconda passata: esce 0" "0" "$?"

# --- i path che deve rifiutare ---------------------------------------------
bash "$SCRIPT" "" >/dev/null 2>&1;    check "path vuoto rifiutato" "1" "$?"
bash "$SCRIPT" "/" >/dev/null 2>&1;   check "radice rifiutata" "1" "$?"
bash "$SCRIPT" "$HOME" >/dev/null 2>&1; check "HOME vera rifiutata" "1" "$?"

# La HOME dell'utente non deve essere toccata neanche per sbaglio.
check "la HOME vera è intatta" "1" "$([ -d "$HOME" ] && echo 1 || echo 0)"

# --- una stage senza .home non è un errore ---------------------------------
mkdir -p "$TD/vuota"
bash "$SCRIPT" "$TD/vuota" >/dev/null 2>&1; check "stage senza .home: esce 0" "0" "$?"

# --- non esce niente su stdout: il runner ci parsa il JSONL -----------------
mkdir -p "$TD/s2/.home/Library/Caches/ms-playwright"
check "stdout muto (stderr sì, stdout no)" "" "$(bash "$SCRIPT" "$TD/s2" 2>/dev/null)"

echo
if [ "$FAILS" -eq 0 ]; then echo "tutti i test passati"; else echo "$FAILS test falliti"; fi
exit $((FAILS > 0))
