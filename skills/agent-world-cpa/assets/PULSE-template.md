# Pulse

**Default frequency:** settimanale

## On Quiet Waking

When invoked via `--pulse` without a specific task, work through these in priority order.

### Memory Curation

Load `references/memory-guidance.md` and curate MEMORY.md (plus INDEX/BOND as needed) so the next waking is effective and under the guidance's token guardrail. Prefer `uv run scripts/sanctum-health.py {project-root}` for token counts, session inventory, and INDEX↔disk drift — then judge what to keep.

### Deadline sweep

Leggi prima `SCADENZE.md` (poi BOND/MEMORY solo come fallback). Elenca adempimenti aperti nelle prossime 4–6 settimane in `## Pending Sparks` di MEMORY.md (data, soggetto, obbligo, urgenza). Se il registro è vuoto, non inventare scadenze — annota «registro vuoto».

### Normative watch

Se hai tool di ricerca/web, controlla aggiornamenti rilevanti per le giurisdizioni e i temi del mandato. Una nota corta in Pending Sparks solo se cambia davvero il rischio o una scadenza; altrimenti skip.

### Self-Improvement

Se in State `self_improvement: yes`, rifletti su sessioni recenti: gap di capability, cosa ha funzionato. Nota in session log per il prossimo wake. Se `self_improvement: no` (default), salta.

### Exit trail

Prima di uscire (ogni task route): appendi un blocco pulse a `sessions/YYYY-MM-DD.md` (curated / sparks aggiunti o «none» / watch skipped|fired) e aggiorna State (`last_check`, pending). Poi exit.

## Task Routing

| Task | Action |
|------|--------|
| `curate` | Solo Memory Curation |
| `deadlines` | Solo Deadline sweep → Pending Sparks |
| `watch` | Solo Normative watch → Pending Sparks |
| `full` (default) | Curation → deadlines → watch → exit trail |

## Quiet Hours
23:00–07:00 Europe/Rome (salvo override in First Breath)

## State
- **self_improvement:** no
- **last_check:** _
- **pending:** _
