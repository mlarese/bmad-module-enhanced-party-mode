# Craft Marketing — hero, sezioni, gallerie

Regole della superficie **marketing** (landing, home, brand page). Load da DX/UE/AF
quando la superficie è marketing, **insieme** a `craft-rules.md` (nucleo: palette,
tipografia, composizione, superfici, chrome, responsive, motion). Non è una capability.

Qui vive solo ciò che è specifico della landing: la hero (catalogo visivo,
trattamento immagine, copy layout), le sezioni determinate dal dominio e le
gallerie. Tutto il resto vale per ogni superficie e sta nel nucleo.

## Hero — impatto

Hero = impact zone: media plan (carousel | layered | still), depth, display fonts ≥2 candidates (poi scegli con regola locale+attività).

**Il testo è contenuto, non riempitivo.** Se l'owner non fornisce il copy, lo si **deriva dalla ricerca di dominio e marketing** (headline, CTA col verbo del business, sezioni, FAQ, microcopy, `alt`, meta) — mai lorem ipsum, mai gergo da landing generica; prezzi/orari/contatti verosimili si scrivono per intero e la loro natura si dice all'owner in chat (`craft-rules.md` → *Il lavoro consegnato è finito*). Disciplina: `references/implementation-handoff.md`. Attenzione a non confondere: `hero_copy` qui sotto è **dove** sta il testo, non cosa dice.

### Catalogo visivo (offrilo prima di sorteggiare)

Descrivere una hero a parole («split con plate a sinistra») costa due giri di fraintendimenti; guardarla costa uno sguardo. Il catalogo è una pagina di miniature — una per archetipo, con nome, descrizione, quando usarlo e cosa sorvegliare — così l'owner **indica** la hero invece di immaginarla. Ogni miniatura è una hero vera in piccolo: **foto reale** da `assets/hero-media/` e **testo reale** (occhiello, titolo, sottotitolo, CTA), perché uno schema a barre grigie non si legge e fa scegliere a caso.

```bash
uv run scripts/hero_gallery.py --build            # scrive assets/hero-gallery.html → poi `open <path>`
uv run scripts/hero_gallery.py --suggest 6 --seed YYYYMMDDHH --last <da MEMORY>
uv run scripts/hero_gallery.py --show <id>        # assi + quando + attenzione
uv run scripts/hero_gallery.py --filter media=video    # o placement=center, panel=solid
```

1. **Copertura:** media (foto singola · carosello · video · nessun media · collage · sequenza a scroll · UI di prodotto · mappa · prima/dopo) × placement (sinistra · destra · centro · basso · basso-sinistra · sopra il media · due poli · rail laterale) × pannello (plate pieno · nessuno · velo chiaro · vetro · fascia · gradiente di un bordo). Sorgente: `assets/hero-catalog.json`.
2. **L'archetipo lo scegli tu, non lo chiedi.** `--suggest N` dà una shortlist deterministica dal seed, diversa su media e placement, con le esclusioni da MEMORY (`--last` accetta id, `hero_treatment` o etichette `hero_copy`): prendi il primo che regge dominio e `register`, verificalo con `--show <id>`, e vai. Nessuna fermata, nessun catalogo aperto in attesa (legge dello skill: `references/autonomia.md`).
3. **L'`id` scelto fissa le decisioni.** Che venga dalla shortlist o dall'owner di sua iniziativa, quello **fissa** `hero_treatment`, placement e panel: non rilanciare `hero_copy.py` per contraddirlo. Dichiara `hero_archetype: <id>` accanto alle altre decisioni. Il catalogo a vista (`--build` + `open`) si costruisce solo su richiesta esplicita dell'owner.
4. **Il campo «attenzione» è un vincolo di consegna**, non una nota di colore: video → `poster` + `muted` + `playsinline` + `prefers-reduced-motion`; carosello → ≥6s per slide, pausa su hover/focus, controlli raggiungibili da tastiera; mappa → non interattiva nella hero; vetro → fallback tinta piena.
5. **Foto e marchi delle miniature sono campioni, non proposte:** servono a far leggere lo schema. Palette, font e immagini del progetto vero restano derivati da località + carattere + business (Envato per le foto). Un archetipo scelto porta con sé il **layout**, non i colori né il brand del riquadro.
6. **Il catalogo è estendibile:** aggiungi l'archetipo a `assets/hero-catalog.json` (con `photo:` dal `media_pool` e, se serve, un `copy:` dedicato), rigenera con `--build`, e `scripts/tests/test-hero-gallery.py` verifica copertura, vocabolario, testo reale, media presenti e sync della pagina — filtro incluso, cliccato nel browser quando playwright c'è. Un archetipo mai messo in catalogo è un archetipo che dimenticherai.
7. Dopo approve: MEMORY `last_hero_archetypes` (oltre a `last_hero_treatments` e `last_hero_copy`).

### Trattamento immagine (mai il velo scuro di default)

Il problema: il velo scuro full-bleed (`linear-gradient(180deg, rgba(dark,.35) → rgba(dark,.9))` + vignetta radiale) è la soluzione **universale** al problema "testo chiaro su foto qualsiasi". Essendo universale produce hero **identiche**: cambia l’hex, non la sensazione. Distrugge la luce propria della foto (la neve di Cortina, il turchese di Jesolo e la notte di Milano diventano la stessa fanghiglia) e annulla la regola palette-da-località proprio nel primo viewport.

1. **Vietato come default:** velo scuro a piena area + testo centrato in bianco. Non è una scelta, è un riflesso.
2. **Scegli e dichiara `hero_treatment:`** dal pool (uno, al massimo due combinati):

| Trattamento | Come regge la leggibilità |
|---|---|
| Split / asimmetrico | testo su pannello tinta piena, foto accanto **intatta** |
| Editorial (testo fuori dalla foto) | headline sopra/sotto l’immagine, zero overlay |
| Inset / cornice | foto rientrata sul fondo pagina, testo sul fondo |
| Plate / band locale | scrim solo dietro al blocco testo (≤35% area) |
| Velo **chiaro** | wash col chiaro del brand + testo scuro → hero luminosa |
| Duotone / grading brand | foto virata nella palette, non annerita |
| Knockout / blend | tipografia in `mix-blend-mode`, nessun scurimento |
| Negative space | crop scelto (cielo, neve, muro) e testo lì |
| Type-first | tipografia gigante protagonista, foto in inserti o mascherata |
| Video ambient + plate | `<video>` muted loop a colori pieni; testo su **plate opaco** (≤35% area) — non annerire il filmato; poster + rispetto `prefers-reduced-motion` |
| Gradiente **di un solo bordo** | copertura ≤40%, resto della foto pulito |

I media oltre la foto ferma — `carousel` · `collage` · `sequence` · `ui-shot` · `map` · `compare` · `marquee` — sono trattamenti legittimi allo stesso titolo, con i loro vincoli nel catalogo (`hero_gallery.py --show <id>`). Il velo scuro full-bleed resta vietato su tutti.

3. **Chiave tonale dalla località/ora:** alta (neve, mare, giorno) → hero **luminosa**; bassa (fine dining notturno, cantina) → hero scura. Non tutto low-key.
4. **Anti-ripetizione:** famiglia di trattamento **diversa** dalle ultime in MEMORY (`last_hero_treatments`), come per palette e font.
5. Se serve davvero uno scrim: **sagomato e locale** (dietro il testo, o un bordo), tarato sui toni di quella foto — non lo stesso 0.35→0.9 su ogni progetto.
6. **Test:** affianca la hero a quella dell’ultimo progetto. Se leggono come la stessa foto sporcata di scuro → fallimento, cambia trattamento.

### Copy layout (placement × panel) — obbligatorio su lavoro nuovo

Bias da uccidere: ripetere sempre **testo a destra + plate/sfondo pieno** (Aster-style). Placement e opacità del blocco testo sono una decisione **separato** da `hero_treatment` (immagine), e vanno **dichiarati** ogni volta.

1. Dichiara: `hero_copy:` · `hero_copy_placement:` (`left` | `right` | `center`) · `hero_copy_panel:` (`solid` | `transparent`).
2. Pool a 6 ipotesi **equiprobabili** (nessun default a destra-pieno):

| `hero_copy` | Placement | Panel | Note |
|---|---|---|---|
| `right-solid` | destra | pieno (plate/pannello) | ≤40% area; foto intatta |
| `right-transparent` | destra | trasparente | no plate; negative-space / knockout / velo chiaro locale |
| `left-solid` | sinistra | pieno | simmetrico dello split plate |
| `left-transparent` | sinistra | trasparente | |
| `center-solid` | **centrato** | pieno | plate opaco centrato — **non** velo full-bleed |
| `center-transparent` | **centrato** | trasparente | titolo in mezzo senza plate; leggibilità dal crop |

3. **Algoritmo (deterministico da seed — “casuale” ripetibile):**
   - `seed = YYYYMMDDHH` (stesso clock di motion; oppure output di `uv run scripts/hero_copy.py`).
   - Leggi MEMORY `last_hero_copy` (ultime 1–2 etichette) → **escludile** dal pool.
   - `u = (seed * 2654435761) & 0xFFFFFFFF` (hash moltiplicativo Knuth).
   - `choice = candidates[u % len(candidates)]`.
   - CLI: `uv run scripts/hero_copy.py --seed YYYYMMDDHH --last <ultime da MEMORY>`.
4. **Vincoli:** `center` + velo scuro full-bleed = **vietato** (resta l’anti-pattern del punto 1). `solid` = plate/pannello locale, non wash a tutta hero. Dopo approve aggiorna MEMORY `last_hero_copy`.

4b. **Placement oltre le 6 etichette:** il catalogo (`hero_gallery.py`) porta anche `bottom`, `bottom-left`, `top` (testo fuori dalla foto), `split` (due poli) e `rail` laterale, più i pannelli `wash` · `glass` · `band` · `gradiente di un bordo`. Sono scelte piene, non eccezioni: quando ne usi una, `hero_copy` non ha un'etichetta del pool → dichiara `hero_archetype: <id>` + `hero_copy_placement:` + `hero_copy_panel:` a mano.
5. Fallimento: tre landing di fila con testo a destra su plate pieno; oppure centrato solo con gradiente scuro full-bleed.

## Sezioni — determina da sola (default se non istruita)
Se l’owner chiede una landing / page / restyle sostanziale **senza** elenco sezioni, **non chiedere** la mappa sezioni e **non** consegnare solo hero + footer. **Tu determini** quali sezioni servono, dal dominio + brand + ask + località (ristorante ≠ hotel ≠ SaaS ≠ portfolio; Cortina ≠ Milano).

**Se il cliente ha già un sito, i servizi si verificano lì** (craft-rules → *Il sito esistente del cliente*): la pagina ripropone l'offerta reale — nomi veri, perimetro vero — riorganizzata meglio, non un elenco inventato. Il *design* di quel sito resta fuori: non si guarda e non si imita.

Come decidere (giudizio, non checklist fissa):
1. Cosa deve capire / sentire / fare il visitatore in questa pagina?
2. Quali blocchi sono necessari per quel viaggio (impatto → prova → offerta → prova visiva → fiducia → azione)?
3. Dove il prodotto è visivo → **galleria** (spesso sì su hospitality, food, brand, portfolio).
4. Dichiara in DX/UE/AF le sezioni che hai scelto e perché (una riga), poi implementale.

Esempi di blocchi tipici (aperti, non obbligatori tutti): hero · intro/storia · offerta/menu/camere/servizi · galleria · team/chef · trust/recensioni · location/orari · CTA/prenota · footer.

Fallimento: stub solo-hero; oppure chiedere “quali sezioni vuoi?” quando puoi inferirle. Scorciatoia correzione piccola → non espandere.

## Gallerie — ordine L→R + motion + forme (sempre)
1. Includi una galleria (grid / masonry / strip / bento) quando il prodotto è visivo. **Le foto sono quelle del cliente** se un sito esiste e le ha usabili (sono il suo posto, i suoi piatti); stock mirato solo in mancanza. Mai celle vuote o rettangoli grigi.
2. **Inserimento sinistra → destra (obbligatorio):**
   - DOM order = ordine di lettura L→R (poi riga successiva). `appendChild` / markup in sequenza; **non** `prepend`, **non** shuffle random delle posizioni.
   - Grid: `grid-auto-flow: row` **oppure** placement esplicito in ordine di lettura L→R. Masonry/strip: stesso principio — prima cella a sinistra.
   - Progressive load / batch: aggiungi in coda L→R; lo **stagger di comparsa** segue l’indice (`delay ≈ i × 60–100ms`) così appaiono da sinistra verso destra.
3. **Zero buchi (obbligatorio):** la griglia deve essere **pieno continuo** — nessuna cella vuota tra le foto. Non bastano span “a caso”: usa un **mosaico che tesse** (placement esplicito `grid-column`/`grid-row`, o sequenza di forme collaudata che riempie ogni track). Vietato lasciare gap per `tall`/`wide` mal piazzati. `dense` solo se non spezza la lettura L→R; preferisci layout progettato senza buchi.
4. **Animazioni diverse per item (obbligatorio):** **ogni** foto ha un reveal **univoco** rispetto alle altre nella stessa gallery (N tipi distinti finché il pool basta; seed senza adiacenti uguali). Pool obbligatorio da mescolare:
   - direzionali: sinistra / destra / alto / basso / diagonale / flip
   - **espansione centrale:** tile/`img` piccola al centro → riempie la cella
   - **blow-up on scroll (obbligatorio nel mix):** man mano che si scorre, le foto **si gonfiano** nello spazio (`--blow` 0→1 legato allo scroll, reversibile). Non un solo pop IO: progress continuo mentre entrano nel viewport, L→R. Celle centrali → blow più marcato (`scale` da ~0.25).
   Stagger per indice L→R; **repeat**. Vedi `craft-rules.md` → *Motion (Vera)* → **Motion diversificato**.
5. **Forme alternate (obbligatorio):** mescola **quadrato** (~1×1), **largo** (~2×1), **alto** (~1×2) — e se serve uno span 3 per chiudere l’ultima riga senza buchi. Track con altezza definita. Seed ruota **quale** mosaico gapless usare, non spezza il tiling.
6. Fallimento: celle vuote in mezzo alla gallery; inserimento caotico; due+ foto con la stessa animazione quando N ≤ pool; gallery tutta a quadrati uguali; batch con un solo fade simultaneo.

## Almeno una tenda, sempre

Su una landing va **sempre** almeno un effetto `curtain`. È una regola
dell'owner, non una preferenza di craft: il gesto della tenda è quello che
distingue un'apertura pensata da una pagina che appare e basta.

Il catalogo di Vera ne ha **sei** — `curtain` (due metà), `curtain-page`, e le
quattro direzioni `curtain-up` · `curtain-down` · `curtain-left` ·
`curtain-right`. Quale, lo decide **il seed** come ogni altro effetto: il verso
non è indifferente — dal basso segue la lettura, dall'alto è il sipario, i due
laterali seguono o contraddicono lo scorrimento.

**Una per pagina.** Quattro tende che si aprono da quattro lati non sono un
sistema, sono un difetto. `close_check --surface marketing` verifica che ce ne
sia una e non fa consegnare senza.

## Le parole del mestiere restano come sono

`reception` non diventa «ricevimento». Vale per tutto il lessico che il settore
usa così com'è — `check-in`, `spa`, `brunch`, `coworking`, `dehors`, `booking`,
`front office` — e la prova non è la lingua, è **cosa dice quel settore**: lo si
legge nella ricerca di dominio e sul sito del cliente.

Tradurle è il segnale più veloce che la pagina l'ha scritta qualcuno che non
conosce il mestiere. L'eccesso opposto — infilare anglicismi che il mestiere non
usa — è già vietato: «Elevate your business» non è lessico, è gergo.

Disciplina completa: `implementation-handoff.md` §9.
