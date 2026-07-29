# Craft rapido — tutto quello che serve alla pagina, e nient'altro

Questo file **sostituisce** `craft-rules.md` + `craft-marketing.md` +
`autonomia.md` quando il ciclo è **rapido** (`ciclo-rapido.md`). Non è un
riassunto per pigrizia: è ciò che resta togliendo consiglio, sei documenti,
slice, workflow BMAD e tetti di giro — cose che in rapido non girano, e che
pesavano **~25.600 token** da leggere prima della prima riga di HTML.

Misurato il 2026-07-29: il percorso di lettura del rapido era **~45.700 token**
di reference (più ~9.400 di sanctum) per una pagina che si scrive con **due**
decisioni. Da qui questo file: **~2.400**, e il percorso intero — `SKILL.md` più
questo — **~8.900**.

> **La bellezza non sta in ciò che si è tagliato.** Sta nel lock e in
> `craft_axes` — che sono due comandi — e in quanto è scritto bene l'HTML. Tutto
> il resto era procedura.

---

## 1. Due comandi, e le decisioni ci sono già

```bash
uv run scripts/craft_lock.py --project <slug> --seed YYYYMMDDHH \
  --surface marketing --out apps/<slug>/craft-lock.json
uv run scripts/craft_axes.py --seed YYYYMMDDHH --activity <attività> --sections N
```

**Il lock decide cinque cose in un colpo** — e le decide chiamando *lui* i
cataloghi (`craft_lock.py:95,121,133` importa ed esegue `accent_pool`,
`font_pool`, `shape_pool`, `hero_gallery`, `effects_gallery`):

| Dal lock | Cosa contiene |
|---|---|
| `colore` | `id`, `famiglia`, `accent` esadecimale |
| `font` | `display` + `body` |
| `forma` | `radius` e `radius_family` |
| `hero` | `id` dell'archetipo, `media`, `placement` |
| `effetti` | tre tecniche di movimento |

**Quindi non si chiamano `accent_pool`, `font_pool`, `shape_pool`,
`hero_gallery` né `effects_gallery` a parte.** Restituirebbero gli stessi
identici valori — escono dalle stesse funzioni, con lo stesso seed — al prezzo
di cinque giri di andata e ritorno. La regola «i cataloghi si eseguono, non si
citano» resta vera e **il lock è il modo in cui si eseguono**.

**`craft_axes` dà il resto:** `grid_system` · `alignment_map` · `bleed_rhythm` ·
`surface_rhythm` · `surface_texture` · `type_voices` · `type_scale`.

Il seed è **`YYYYMMDDHH-<slug>`**: con la sola ora, due pagine fatte nello stesso
momento escono identiche su ogni asse.

---

## 2. Come si rendono, senza sbagliare

Le decisioni sono prese; qui c'è come si scrivono in pagina. Ogni riga di questa
sezione nasce da un difetto misurato, non da un gusto.

### Tipografia — è una legge, non una coppia di nomi

- **Tre voci** (`type_voices`): display · body · **terza voce** con un compito
  vero (didascalia, dato, citazione, label). Due sole famiglie solo se un
  vincolo di brand lo impone. Il mono può essere voce **primaria** — label,
  metriche, nav — non «il font del codice».
- **Scala fluida differenziata:** display `max ≈ min × 1.5`, body
  `max ≈ min × 1.2–1.25`. Il display respira, il testo di lettura no.
- **Tracking a due poli, obbligatorio:** display da `-0.03em` a `-0.06em` (più
  negativo al crescere del corpo); eyebrow/label `+0.10em`…`+0.18em` con
  uppercase. Un solo valore di tracking su tutta la pagina è un fallimento.
- **Leading per registro:** display `0.80–0.95`, body `1.35–1.50`.
- `font-variant-numeric: tabular-nums` su ogni cifra in colonna (prezzi, orari).
- `text-wrap: balance` sulle headline, `pretty` sui paragrafi.
- **Vietato `clamp(x, …, x)`** con estremi uguali: se non scala, scrivi il valore
  fisso.

### Composizione — è la silhouette a far somigliare le pagine, più del colore

- **`grid_system`** dal `craft_axes`: `fine` (24–36 colonne + placement
  esplicito) · `asym-rail` (traccia fissa `12–22vw` + `1fr`) · `12-col` (da
  motivare, non è il default).
- **Almeno due blocchi con `grid-column: <start>/<end>` esplicito** (start ≠ 1
  oppure end ≠ -1). Se tutto è `span N`, l'off-center non esiste: è un template.
- **`alignment_map` sezione per sezione.** Stesso allineamento ovunque =
  fallimento. **Centratura: massimo 2 sezioni**, e solo su statement o CTA
  finale. Il destra-allineato è un registro vero per metadati, anni, contatti —
  mai per il corpo.
- **Misura in `ch`:** headline `10–20ch`, body `55–68ch`. Nessun testo eredita la
  larghezza del contenitore.
- **`bleed_rhythm`**: `contained` o `alternating`, e si tiene per tutta la
  pagina. Margini dai token di griglia, **non** `max-width: 1200px; margin: auto`.
- `subgrid` sulle liste di card con testo di lunghezza variabile.
- `aspect-ratio` scelto (`4/5`, `1/1.2`, `9/16`), non solo `16/9`.

### Superfici — la hero è il primo schermo, poi ne restano cinque

- **`surface_rhythm`**: sequenza di fondi con **cambio di chiave ogni 2–3
  sezioni**, implementata con `data-theme` **sulla sezione**, non con override
  sparsi.
- **Una `surface_texture` di casa** (max due, mai zero): `rule-lines` (hairline
  `1px`, anche `dashed`, come sistema) · `svg-pattern` (data-URI agganciato al
  modulo di griglia) · `baseline-rule` (carta rigata col passo della riga) ·
  `grain` (noise vero, non un velo al 3%).
- **Luce con raggio dichiarato:** `radial-gradient(circle at X Y, <accento>,
  transparent 8–15rem)`, o una forma colorata con `blur(20–30px)` **dietro** il
  contenuto. Vietati il gradiente lineare a tutta pagina come fondo di sezione e
  il `backdrop-filter` come risposta a ogni pannello.
- **Token nominati per materiale:** `--bg-paper`, `--bg-dirty-white`, `--bg-inv`.
  L'off-white è un token dichiarato, mai `#f8f9fa` di riflesso.
- Un angolo di gradiente di casa, riusato. Scala di opacità a 4–6 gradini fissi.
- Fallimento: alternare `#ffffff` / `#f8f9fa` (alternanza invisibile che costa
  come una vera); tinta piatta + card bianche con shadow morbida; hero curata e
  sezioni successive senza nessuna decisione di superficie.

### Forma — arriva dal lock, si applica ovunque

`radius_family` è nel lock. Si mettono i token in `:root` e si applicano a
**bottoni, card, input, chip, modal** in modo coerente:

```css
:root { --r-btn: 999px; --r-box: 12px; --r-chip: 8px; }
```

`border-radius: 0` implicito su tutto è il difetto che rende uguali le pagine
anche quando palette e font cambiano. Se è `sharp`, è perché il lock l'ha detto.

### Hero

L'archetipo è nel lock. **La sezione si firma `data-hero="<id>"`**, o l'archetipo
deciso non è verificabile e `close_check --lock` non può dire niente.

### Movimento

Le tre tecniche sono nel lock. In rapido le scrivi tu — reveal allo scroll,
hover, transizioni — con `prefers-reduced-motion` rispettato. Vera si invoca solo
se l'owner la chiede. Una pagina senza nessun movimento non è «rapida», è finita
male.

---

## 3. Le cose che non si negoziano mai

- **Il lavoro consegnato è finito.** Nel file **non compare mai** `TODO`,
  `[INSERIRE …]`, `XXX`, `lorem ipsum`, «testo di esempio», commenti che
  avvisano, elenchi di dati fittizi. Contatti, prezzi e orari si scrivono
  **verosimili e per intero**; l'onestà si dice **all'owner in chat** e nella
  voce `dati_verosimili:` del `DESIGN.md`. Preferisci recapiti che non possano
  appartenere a nessuno (prefissi non assegnati, dominio del brand fittizio).
- **Non si inventano i fatti che fanno danno se creduti:** certificazioni, premi,
  partner o clienti reali, riferimenti di legge, dati sanitari, recensioni
  attribuite a persone esistenti. Lì si progetta la sezione in modo che non
  richieda quel dato, e lo si dice.
- **Responsive**, sempre: `<meta name="viewport" …>`; griglie che **collassano**
  sotto ~820–900px; `clamp`/unità relative con body ≥16px effettivo su mobile;
  media `max-width: 100%` e hero in `svh` non `100vh` bloccato; tap target
  ≥44px; **nessun overflow-x di pagina**. Verifica a ~375 e ~1280.
- **Cookie e informativa** se la pagina raccoglie un dato o carica da terzi —
  prima si chiede, poi si carica. La strada più pulita è **non avere il
  problema**: font in locale, zero risorse di terzi, nessun banner. Se c'è un
  form, il testo è di Jane (`agent-gdpr-counsel`) e si invoca: un'informativa
  inventata rientra nei fatti che fanno danno se creduti.
- **Le parole del mestiere non si traducono** (`reception` resta `reception`,
  come `check-in`, `spa`, `booking`), e l'italiano non è una traduzione: niente
  «scopri di più», «prenota la tua vacanza», «soluzioni su misura». Restano
  legittimi la frase senza verbo e il periodo breve — si tolgono i calchi, non
  il ritmo.
- **L'output non si sovrascrive:** slug libero → si scrive lì; cartella occupata
  da altro → `apps/<slug>-<data>/`, e lo si dice. Mai un `rm -rf` per «ripartire
  pulito».

---

## 4. Anti-banale, in una riga

Fuori: Inter + viola/indigo, badge pill flottanti, container centrato con tutto
a sinistra, sei sezioni di tinta piatta con card bianche, `clamp` degenere,
gallery caotica, clone di un template Envato, clone del sito vecchio. Il lock
protegge dal ripetersi; questa riga protegge dal partire già uguale a tutti.

---

## 5. Chiusura

```bash
uv run scripts/close_check.py apps/<slug>/*.html --design apps/<slug>/DESIGN.md \
  --council {project-root}/docs/consiglio/<slug>.md --lock apps/<slug>/craft-lock.json \
  --surface marketing --ledger ~/.claude/agent-frontend-taste/craft-ledger.json
```

Un comando: colore, responsive, nessun segnaposto, traccia nel DESIGN, registro,
e il confronto con il lock. **`0` si consegna · `1` correggi · `2` non
misurabile, e un `2` non è un pass.** Il ledger si scrive **sempre**, anche in
rapido: se le bozze non contassero, l'anti-ripetizione guarderebbe solo i lavori
lenti.
