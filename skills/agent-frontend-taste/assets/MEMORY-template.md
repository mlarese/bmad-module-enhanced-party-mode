# Memory

_Curated long-term knowledge. Empty at birth — grows through sessions._

_This file is for distilled insights, not raw notes. Capture the essence: decisions made, ideas worth keeping, patterns noticed, lessons learned._

_Aim to stay under roughly 1500 tokens, a guardrail rather than a hard gate. If your curated knowledge genuinely earns more space, keep it, but treat growth past the guardrail as a signal to prune. Raw session notes go in `sessions/YYYY-MM-DD.md` (not here). Distill insights from session logs into this file on **session close** and prune what's stale. Every token here loads every session, so make each one count. See `references/memory-guidance.md` for full discipline._

## Taste log (keep short)

- `last_registers:` _(es. luxury · famigliare · artigianale — il **carattere** del business; mai da seed. Stesso register due volte di fila → cambia comunque famiglia di palette)_
- `last_palette_families:` _(es. coral-sea · pine-firn — non ripetere le ultime 2–3)_
- `last_hue_sectors:` _(settore di tinta dominante per area — rosso · terra · giallo · verde · teal · blu · viola · magenta · neutro. **Mai lo stesso per 3 job di fila**: il nome della famiglia può cambiare mentre l'hue resta. Misura con `palette_guard.py`. **Ordine: il più recente per primo** — `--last` conta la serie dall'inizio della lista, e una lista cronologica inverte il controllo in silenzio. Fra progetti diversi la serie vera sta nel ledger: `palette_guard.py --ledger …/hue-ledger.json`)_
- `last_ink_families:` _(neutro · caldo · freddo · virato-accento — lo scuro riempie hero, fasce e footer: se è sempre lo stesso, le pagine si somigliano anche con accenti diversi)_
- `last_font_pairs:` _(es. Fraunces+Figtree · Bodoni+Outfit — non ripetere)_
- `last_hero_treatments:` _(es. split · inset · duotone — **mai** velo scuro full-bleed di default; non ripetere le ultime 2)_
- `last_hero_copy:` _(es. right-solid · center-transparent · left-transparent — da `hero_copy.py`; non ripetere)_
- `last_radius_families:` _(es. soft · sharp · pill — forma btn/box; **mai** default implicito a 0 su ogni job; non ripetere le ultime 2)_
- `last_grid_systems:` _(es. fine · asym-rail · 12-col — da `craft_axes.py`; **mai** container centrato + tutto left per riflesso; non ripetere)_
- `last_surface_textures:` _(es. rule-lines · svg-pattern · baseline-rule · grain — una texture di casa per job, mai zero; non ripetere)_
- `last_type_voices:` _(terza voce: mono · italic · serif-accent — la coppia display+body non basta; non ripetere)_
- `last_splashes:` _(es. first-frame · mark-draw · gradient-wash — da `mobile_recipe.py`; non ripetere)_
- `last_app_backgrounds:` _(es. mesh-gradient · solid-texture · radial-glow — un fondo di marca per app; non ripetere)_
- `dashboard_themes:` light+dark obbligatori _(nota se Mauro preferisce default light o dark)_
- `page_default:` se non istruita → **determina da sola** le sezioni; palette/font da **locale + register + activity** (carattere: luxury · famigliare · artigianale…); motion misto destra/sinistra/alto con seed `YYYYMMDDHH`; **repeat**
- `approved_structures:` _(es. hero carousel full-bleed; dashboard sidebar + KPI strip)_
- `rejected:` _(pattern che Mauro ha bocciato)_
