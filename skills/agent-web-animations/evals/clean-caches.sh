#!/usr/bin/env bash
# Pulisce le cache che i runtime scaricano dentro l'HOME isolato di una run.
#
# Perché esiste, misurato: il runner degli eval crea un HOME vuoto per ogni
# query (`<stage>/.home`) così che la configurazione della macchina non falsi il
# risultato. Dentro, un runtime che apre un browser si scarica Chromium: una
# sola run di trigger ha lasciato **due copie da 542 MB**, il push a GitHub è
# stato rifiutato (`pre-receive declined`, file oltre 100 MB) e Dropbox stava
# sincronizzando un giga di cache. Degli artefatti di una run servono gli
# esiti — timing, transcript, grading — non il browser.
#
# Uso:  bash clean-caches.sh <stage-dir>
# Sicuro per costruzione: non tocca niente fuori da `<stage-dir>/.home`, e si
# rifiuta di lavorare su una directory vuota, sulla radice o sulla HOME vera.

set -uo pipefail

STAGE=${1:-}

# Le cartelle che i runtime riempiono e che nessuno rileggerà mai.
CACHE_NAMES=(ms-playwright puppeteer ".cache/puppeteer" "Cypress")

case "$STAGE" in
  "" | "/" | "$HOME" | "$HOME/")
    echo "clean-caches: rifiuto '$STAGE' — serve la stage dir di una run" >&2
    exit 1
    ;;
esac

[ -d "$STAGE/.home" ] || exit 0

freed=0
for name in "${CACHE_NAMES[@]}"; do
  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    size=$(du -sk "$dir" 2>/dev/null | cut -f1)
    rm -rf "$dir" 2>/dev/null && freed=$((freed + ${size:-0}))
  done < <(find "$STAGE/.home" -maxdepth 8 -type d -name "$(basename "$name")" -prune 2>/dev/null)
done

if [ "$freed" -gt 0 ]; then
  echo "clean-caches: liberati $((freed / 1024)) MB in $STAGE/.home" >&2
fi
exit 0
