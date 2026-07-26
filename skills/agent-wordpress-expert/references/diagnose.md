---
name: diagnose
description: Causa radice errori WP + piano di fix
code: DG
added: 2026-07-25
type: prompt
---

# Diagnose

## What Success Looks Like
L'owner ha una **causa radice** (o le 2–3 ipotesi ordinate per probabilità) e un piano di fix **verificabile**: cosa controllare, in che ordine, come confermare che è risolto. Inventare un plugin colpevole "perché capita spesso" senza segnale è fallimento.

## Non-inferables
- Chiedi 1–2 fatti mancanti critici (versione WP/PHP, ultimi cambiamenti, log/`WP_DEBUG_LOG`, tema/plugin) invece di uno scenario completo inventato.
- Preferisci check sicuri in staging; niente `display_errors` in produzione.
- Controlla MEMORY/BOND per stack e siti già noti.
- Distingui sintomo (white screen, 500, redirect loop) da causa (fatal PHP, plugin conflict, permalink, object cache).
