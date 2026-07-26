---
name: ui-elaborate
description: Brief UI eseguibile — palette fresca, batch ≥30, motion Vera
code: UE
added: 2026-07-25
type: prompt
---

# UI Elaborate

## What Success Looks Like
`UI-BRIEF.md` che un FE implementa senza questa chat: tutti gli assi rilevanti da `craft-rules.md` (Craft Axes Index), Motion intent Vera `repeat: always`. Fallimento: stub, mono-direzione, radius 0 implicito, palette senza luogo **o senza `register`**, impaginazione identica all’ultimo job (griglia + allineamenti + superfici non dichiarati), brief con `TODO`/«da sostituire».

## Non-inferables
- Load `references/craft-rules.md` (nucleo) **+ il file della superficie** (`craft-marketing.md` · `dashboard-rules.md` · `mobile-rules.md`). Soft-gate micro-edit → no UE.
- Prima: DX + AW (`--surface` corretto); marketing → `hero_gallery.py --suggest` (archetipo scelto da te sulla shortlist da seed, mai chiesto all’owner) o `hero_copy.py`; new craft → `craft_axes.py` (composizione · superfici · tipografia).
- Marketing: il brief nomina `hero_archetype: <id>` con media, placement, panel e il vincolo dell’archetipo — un FE lo implementa senza vedere la pagina.
- Scrivi il brief; chiudi con path · primo task FE · verifica.
