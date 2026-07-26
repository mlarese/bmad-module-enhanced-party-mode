---
name: design-direction
description: Direzione craft — palette fresca; hero o dashboard da batch ≥30
code: DX
added: 2026-07-25
type: prompt
---

# Design Direction

## Com'è fatto un lavoro riuscito
Una **direzione di craft** chiara che UE o AF possono eseguire senza questa chat: modo, decisioni dichiarate (vedi Le decisioni da dichiarare in `craft-rules.md`), piano d’impatto. Dashboard: light **e** dark della stessa famiglia.

## Le cose che non si indovinano: si applicano
- Load `references/craft-rules.md` (nucleo: indice + scorciatoia per i lavori piccoli + regole) **+ il file della superficie**: marketing → `craft-marketing.md` · dashboard → `dashboard-rules.md` · mobile → `mobile-rules.md`. Uno solo. Scorciatoia correzione piccola → direzione minima, no batch.
- **Nessun beat di scoping, mai** (legge dello skill: `references/autonomia.md`). Se manca **landing vs dashboard vs mobile-web-app** — o l’activity — lo decide **G1** dalla richiesta e dal dominio, e tu lo dichiari in una riga.
- **Dichiara i tre segnali di palette/font: `locale` · `register` · `activity`** (craft-rules → *Palette + fonts*). Il `register` è il **carattere** del business (luxury · famigliare · artigianale · clinico…): non si sorteggia da seed e non si deduce dall’activity — stesso luogo e stesso business con carattere diverso danno palette e font diversi. Se le due letture sono opposte (famigliare vs luxury) decide **G1** sull’evidenza (dominio, luogo, prezzi, tono del sito) e la lettura entra nei documenti; negli altri casi dichiara la tua e procedi. In nessun caso si chiede.
- **Dichiara anche `hue_sector` e `ink_family`** (craft-rules → *Il settore cromatico* e *Lo scuro è una decisione*): il settore dominante non deve ripetere gli ultimi due di MEMORY (`last_hue_sectors`), e lo scuro che riempie hero/fasce/footer sta sotto croma 6 — sopra, è un colore pieno su mezza pagina e la tinta domina la pagina qualunque sia l'accento.
- Sezioni: determinala dal dominio se non elencate (1 riga: sezioni + perché).
- Dichiara tutte le decisioni dell’indice rilevanti al job; su marketing: `uv run scripts/hero_copy.py --seed YYYYMMDDHH --last …` e applica.
- Marketing lavoro nuovo: **archetipo hero deciso da te, senza fermate** — `uv run scripts/hero_gallery.py --suggest 6 --seed YYYYMMDDHH --last <da MEMORY>`, poi prendi il primo della shortlist che regge dominio e `register` (`--show <id>` per decisioni e vincolo di consegna). Fissa `hero_archetype` + `hero_treatment` + placement + panel e **batte** il sorteggio di `hero_copy.py`. Il catalogo visivo (`--build` + `open`) si costruisce solo se l’owner lo chiede di sua iniziativa: non si apre per farlo scegliere, e non si aspetta un `id`.
- Lavoro nuovo: `uv run scripts/craft_axes.py --seed YYYYMMDDHH --activity … --sections N --last-grid … --last-texture …` → conferma o altera con activity + batch, poi dichiara `grid_system` · `alignment_map` · `bleed_rhythm` · `surface_rhythm` · `surface_texture` · `type_voices` · `type_scale`.
- Responsive è assioma: ogni direzione assume desktop **e** mobile viewport (vedi craft-rules). Se l’ask è **web app mobile** (task ripetuto), non è “landing responsive”: usa `--surface mobile` e lo modello `design-md-mobile-web-app.md`.
- Prima di chiudere struttura (lavoro nuovo): AW batch con `--surface` e `--activity` corretti (default valuta 30–40; pool Envato tipizzato ~100).
- Parti dallo modello DESIGN.md giusto: `design-md-landing` · `design-md-dashboard` · `design-md-saas` · `design-md-mobile-web-app`.
- Dopo: UE o AF.
