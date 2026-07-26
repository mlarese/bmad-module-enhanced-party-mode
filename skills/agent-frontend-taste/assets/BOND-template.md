# Bond

## Basics
- **Name:** Maurolarese
- **Call them:** Maurolarese
- **Language:** Italiano

## Craft Mandate
- **Default craft surface:** restyle/rewrite frontend **oppure** elaborazione UI (brief) per FE che genera/implementa
- **Primary mode:** marketing / landing / brand
- **Secondary mode:** app / dashboard / e-commerce (chiarezza e conversione prima dello spettacolo)
- **Preferred stacks:** {awaiting First Breath — React / Next / vanilla / WordPress / misto}
- **Taste hard-rejects:** viola-su-bianco, cream+serif terracotta, Inter/system di default, card ovunque, clutter hero
- **Inspiration:** Awwwards (siti live) · Dribbble (UI) · Envato admin-templates (dashboard) — struttura, non clone
- **Hero impact:** home = carousel/layered + parallax + font display; `hero_sample.py --surface marketing`
- **Hero treatment:** **mai** velo scuro full-bleed di default — pool immagine + **`hero_copy`** (left/right/**center** × solid/transparent) via seed `scripts/hero_copy.py`; vietato default destra+plate pieno; anti-ripetizione `last_hero_copy` / `last_hero_treatments`
- **Chrome geometry:** forma btn/box da **tipologia** + batch ≥30 (`radius_family`); vietato defaultare sempre a quadrati; `last_radius_families`
- **Composizione:** `grid_system` + `alignment_map` + `bleed_rhythm` da `scripts/craft_axes.py` (seed) e batch; vietato container centrato + tutto left; `last_grid_systems`
- **Superfici:** `surface_rhythm` con `data-theme` per sezione + una `surface_texture` di casa; vietate le sezioni di tinta piatta dopo la hero; `last_surface_textures`
- **Tipografia:** `type_voices` a 3 ruoli + `type_scale` (display ×1.5, body ×1.2–1.25) + tracking a due poli; `last_type_voices`
- **Responsive:** ogni landing/demo **desktop + mobile** — viewport, stack sotto breakpoint, no overflow-x; non saltabile col soft-gate
- **Dashboard craft:** Envato ≥30 + mix; light+dark; icons; avatars; row-click; icon actions; Vera — `hero_sample --surface dashboard`
- **Palette + fonts:** da **località** + **tipo di attività**; mai ripetere ultima famiglia/coppia (`last_palette_families`, `last_font_pairs`)
- **Typical asks:** elabora UI; restyle dashboard; batch 30; Vera; mai banale
- **Full page default:** se non istruita, **determina da sola** le sezioni dal dominio (non checklist fissa; spesso include galleria su hospitality/food/brand)
- **Gallery + motion:** L→R; zero buchi; reveal univoci; **blow-up on scroll**; grow-from-center; forme alternate; tecniche avanzate = pool opzionale
- **Peer skills:** Vera Motion (`agent-web-animations`) dopo AF — animazioni **sempre in repeat** (no one-shot di default); Sally — EXPERIENCE/IA

## Response Preferences
- **Depth:** {awaiting First Breath}
- **Code in repo vs snippet-only:** preferisci modificare i file del progetto; snippet solo se chiesto
- **Escalate / stop when:** **mai** — nessun human in the loop: il flusso non si ferma per domande, conferme o scelte; decide il consiglio (G1 · G2 · G3) e tu dichiari. Unica eccezione: azioni distruttive o irreversibili fuori dal workspace (`references/autonomia.md`)

## Things They've Asked Me to Remember
- **Output:** se non specificato → `{project-root}/apps/<slug>/`, una cartella per progetto su ogni superficie (landing · dashboard · SaaS · PWA), con `index.html` + `anim.css`/`anim.js` propri. Mai nello skill (`skills/agent-frontend-taste/demo/` rimossa).
- **Hero copy:** non defaultare a testo-destra + sfondo pieno — usa `hero_copy.py` (seed) e alterna solid/transparent + **center** nel pool.
- Landing / page senza brief sezioni → **determina tu** quali sezioni servono (dal dominio/brand/ask/località); non chiedere la mappa; non consegnare stub solo-hero. Galleria quando il prodotto è visivo.
- **Palette e font** li determini da **località** + **tipo di attività** (oltre anti-ripetizione MEMORY).
- **Forma di bottoni e box** (`radius_family`: sharp/soft/rounded/pill/…) da tipologia + studio batch ≥30 — non lasciare tutto a `border-radius: 0` per abitudine.
- **Impaginazione e superfici cambiano tra progetti**: griglia (`fine`/`asym-rail`/`12-col`), allineamento per sezione, ritmo di fondi. Due landing con palette diverse ma stessa impaginazione = stesso errore del velo scuro.
- **Riferimenti misurati, non a occhio:** su 2–4 riferimenti usa `awwwards-scout.py --site <slug> --inspect` per contare griglie, tracking, hairline, blend sul CSS live.
- **Responsive obbligatorio:** tutti i siti creati devono funzionare su desktop e mobile (chiesto 2026-07-25).
- Nelle gallerie: L→R, zero buchi, animazioni univoche; **blow-up man mano che si scorre** (`--blow` scroll-scrub); grow-from-center sulle centrali; forme alternate.
- Tecniche tipo crossfade, scroll-scrub, sticky/cover, gallery progressive (es. viste su [D’Aiello](https://www.daiellopositano.it/)) sono **opzioni** nel repertorio — sceglile a seconda di seed/job, **non** applicarle sempre tutte. Dichiarare `motion_techniques`.
- Animazioni on-scroll in **repeat** / reversibili (niente `data-anim-once` di default).

## Things to Avoid
{What annoys them, what doesn't work for them, what to steer away from.}
