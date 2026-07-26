# Mobile Rules — corpus + regole randomiche + craft grafico

Come si progetta una web app mobile / PWA che non sia la landing schiacciata né il
template consumer di default. Load da DX/UE/AF quando la superficie è `mobile`.
Non è una capability.

Il problema misurato: sulla web app mobile la skill era **più sottile che altrove**.
C'erano le regole responsive (che valgono per ogni pagina) e uno stampo DESIGN.md,
ma nessuna regola sul **primo istante** (splash), sul **fondo di marca**, sul
marchio, sull'onboarding — cioè su tutto ciò che si vede prima del contenuto. Quel
vuoto si riempie da solo, sempre allo stesso modo: fondo bianco, icona generata a
caso, lampo bianco all'avvio e un gradiente viola-indaco messo lì perché «fa app».

Due strumenti, in quest'ordine:

| Strumento | Cosa fa | Quando |
|---|---|---|
| `scripts/mobile_corpus.py` | costruisce/legge il corpus di **centinaia** di template mobile/PWA reali, con tratti (stack · domain · graphic) | una volta, poi refresh quando invecchia |
| `scripts/mobile_recipe.py` | estrae dal seed una **ricetta**: 16 assi (6 dei quali grafici) + motion + extra + firma, con invarianti e refs dal corpus | a ogni new app / restyle sostanziale |

```bash
uv run scripts/mobile_corpus.py --build            # ~22 request → assets/mobile-corpus.json
uv run scripts/mobile_corpus.py --stats
uv run scripts/mobile_recipe.py --domain food --activity "consegna a domicilio a Padova"
uv run scripts/mobile_recipe.py --batch "app-a,app-b" --out-dir _bmad-output/mobile-recipes
```

**`--build --offline` non tocca un corpus reale già presente**, e nemmeno un
`--target` troppo basso o una rete a metà: se il risultato è meno della metà
dell'esistente, lo script rifiuta e serve `--force` per confermarlo davvero —
misurato per esperienza diretta, non in teoria: un probe di casi limite senza
`--out` esplicito ha sovrascritto 866 item reali con 6 di fixture in un colpo.

## Minimo non negoziabile

**Non è una landing stretta.** Task-first, e soprattutto: la parte che si vede per
prima non è il contenuto ma il **primo istante** e il **fondo di marca**. Era il buco
più largo della skill — senza una regola, ogni app finiva con fondo bianco, icona di
riflesso, lampo bianco all'avvio e un gradiente viola-indaco «perché fa app».

**Ricetta prima della shell (new app / restyle sostanziale):** genera gli assi con
`mobile_recipe.py` (seed `YYYYMMDDHH`, `--domain`, esclusioni da MEMORY incluse
`--last-splash` e `--last-background`; `--batch` per varianti sorelle) e dichiarali.
Corpus con `mobile_corpus.py`. Leve misurate (e **leve morte**: i tag path che negli admin sono la leva, qui
non esistono) e craft grafico nel resto di questo file. Il minimo non negoziabile:

1. **Sei assi grafici dichiarati:** `splash` · `app_background` · `brand_mark` ·
   `onboarding` · `illustration` · `depth`. Non dichiararli significa ereditarli.
2. **Manifest coerente:** `background_color` **identico** al fondo dello splash
   (altrimenti lampo bianco all'avvio), icona `maskable` con glifo in safe zone,
   `theme_color`, `display: standalone`.
3. **Splash solo in standalone** e di durata pari al boot reale, mai inventata.
4. **Se il fondo è un gradiente:** contrasto AA sui **due estremi**, grana
   anti-banding, animazione solo su `transform`/`opacity`, un solo gradiente per
   tutta l'app, colori da `palette_family`, angolo di casa. Vedi l'eccezione
   dichiarata in `craft-rules.md` → Superfici §3.
5. **Shell ad altezza viewport — la barra in basso è sempre visibile, il contenuto
   non scorre come una pagina desktop** (solo web app, mai landing):
   `height: 100svh` + `overflow: hidden` + `grid-template-rows: auto 1fr auto`,
   **scorre il `main` non la pagina**, e la barra è la **terza riga della griglia,
   non `position: fixed`** — così non copre l'ultimo elemento e non salta con la
   tastiera. Se la viewport intera trasla quando scrolli, non è un'app.
6. **Mai segnaposti muti senza backend:** ogni contenuto visivo (foto prodotto,
   copertina, thumbnail, sfondo card) è un'**immagine reale mirata al dominio**,
   non un rettangolo grigio o un'icona IMG. Unica eccezione: l'avatar senza foto,
   dove l'iniziale su un tondo di palette è lo stato corretto. Diverso dallo
   skeleton di caricamento — questa regola riguarda il contenuto statico della demo.
7. **Fisica del telefono:** `dvh`/`svh` mai `100vh`; `viewport-fit=cover` +
   `env(safe-area-inset-*)`; `interactive-widget=resizes-content`; input a
   `font-size: 16px` o iOS zooma al focus; nessuna gesture di sistema rubata.
8. **Batch ≥30** con `hero_sample.py --surface mobile` (+ `--activity` se vertical).
   Per il craft **grafico** il corpus non basta e la ricetta lo dichiara: si guarda
   **a mano** Figma Community, oppure si decide dalla palette.

## Corpus — cosa funziona davvero come leva

Misurato 2026-07-26 (rifallo se cambia). **Le leve non sono le stesse delle dashboard.**

| Superficie | Resa | Nota |
|---|---|---|
| `/web-templates/{mobile, mobile-app, pwa, progressive-web-app, mobile-website}` | 48 item ciascuno, overlap 3–27% | i cataloghi core |
| Altri cataloghi di categoria (`ui-kits`, `app-landing-page`, `ionic`, `flutter`, `food-delivery`, `fitness`, `banking`, `travel`, `onboarding`, `splash-screen`, `gradient`) | 48 ciascuno, overlap **0–8%** | **la vera leva di ampiezza**: 16 cataloghi ≈ 610 unici |
| `/web-templates/mobile/{tag}` (dark, ios, tailwind…) | **stessi 48 item del catalogo base** | **leva morta** — il tag è ignorato server-side. È l'opposto degli admin, dove il tag path è la leva |
| `api.github.com/search/repositories` | ~256 repo su 6 query | descrizioni ricche → gli unici domini davvero affidabili |

**Il nome del catalogo non è un tratto.** Misurata la fedeltà (quanti item confermano
il tema del catalogo che li ospita):

```
food-delivery 100%  ·  fitness 93%  ·  mobile 90%  ·  pwa 68%  ·  ui-kits 62%
flutter 10%  ·  splash-screen 6%  ·  onboarding 5%  ·  gradient 0%  ·  ionic 0%
```

I cataloghi della riga bassa sono **etichette di vetrina**: 48 template generici
ciascuno. Restano nel corpus perché sono disgiunti e lo allargano, ma non timbrano
un tratto — `trusted=False` nel codice. Un riferimento etichettato `gradient` che
il gradiente non ce l'ha è peggio di nessun riferimento.

**Conseguenza operativa, da dire e non nascondere:** sul corpus di 866 item ci sono
**zero** tratti `splash` o `gradient` onesti. Il corpus serve per shell, dominio e
stack. **Per il craft grafico non serve.**

## Dove si guarda per la grafica

Splash, fondo di marca, marchio, onboarding non si trovano in un catalogo di codice.

- **Figma Community** — `figma.com/community/mobile-apps?resource_type=files` è il
  posto giusto per vedere splash e fondi veri. **Si apre a mano, nel browser.** Il
  `robots.txt` di Figma dichiara `User-Agent: anthropic-ai → Disallow: /`, più
  `Disallow: /api/*` e `/community/search?*`: nessuno scout automatico, nessun
  corpus. Un umano che sfoglia non è un crawler; un agente che raccoglie sì.
- **Dribbble** (`dribbble-scout.py --list shots`) per il linguaggio visivo, con il
  limite noto: `?q=` ignora il termine.
- **Il resto si decide.** Il fondo di marca è una conseguenza di `palette_family` e
  di `locale + register + activity`, non un riferimento da cercare. Cercarlo è il modo in cui
  si finisce con il gradiente viola-indaco di tutti.

Etica come in `inspire-ops.md`: poche request, UA onesto, niente `/api/*`, nessun
mirror di asset, nessuna fonte che ha detto di no.

## La legge randomica (deterministica, non capricciosa)

Identica a `dashboard-rules.md`: seed `YYYYMMDDHH`, **uno stream RNG per asse**
(`random.Random("<seed>|<asse>")`), esclusioni da MEMORY (`--last-palette`,
`--last-radius`, `--last-type`, `--last-shell`, **`--last-splash`**,
**`--last-background`**), conflitti risolti e dichiarati, `--batch` mutuamente
distinto su shell · splash · fondo · liste · palette · radius · type.

**Armonia estetica (2026-07-26):** la palette è l'**àncora di registro** — viene
estratta per prima e gli assi visivi si accordano a lei tramite una matrice di
affinità dichiarata (`AFFINITY`: obsidian-champagne → sharp/segno, clay-ember →
rounded/fotografia…). I pesi favoriscono o sfavoriscono, **mai eliminano**; le
poche coppie davvero stonate sono `DISSONANCES` dure, risolte come i conflitti e
dichiarate. La ricetta stampa la riga **Armonia** con gli assi accordati;
`--flat` spegne tutto (pesi di dominio e affinità). Misurato: gli abbinamenti
stonati scendono dal 12,2% al 2,2% (mobile) e dal 6,9% all'1,3% (dashboard),
con varietà e determinismo intatti. È gusto codificato in una tabella
ispezionabile, non un punteggio opaco — e non sostituisce la verifica visiva
sul renderizzato.

**Pesi di dominio (2026-07-26):** con `--domain` l'estrazione non è più uniforme —
una piccola tabella `DOMAIN_WEIGHTS` sposta i pesi verso ciò che la vertical chiede
davvero (fintech ↑ sharp/dense/compact-data, food ↑ rounded/card-stack/photo-crop…).
I pesi **sfavoriscono, mai eliminano** (nessun peso zero), la ricetta dichiara su
quali assi hanno agito, `--flat` ripristina l'estrazione uniforme, e il determinismo
resta pieno: stesso seed+dominio → stessa ricetta.

La ricetta **propone**. DX/UE/AF confermano o alterano ogni asse contro `activity`,
dominio e corpus — e poi lo **dichiarano**. Un asse non dichiarato è un asse
ereditato per riflesso.

## Assi grafici (il motivo per cui questo file esiste)

Pool nel codice, non duplicati qui: `splash` · `app_background` · `brand_mark` ·
`onboarding` · `illustration` · `depth`. Le regole che li governano:

### Splash

1. **Lo splash dura quanto il boot, non un tempo inventato.** Se l'app è pronta in
   200 ms, lo splash dura 200 ms. Una schermata che *aspetta* per farsi guardare è
   tempo rubato all'utente.
2. **Solo in `display-mode: standalone`.** In scheda browser lo splash è una
   schermata di attesa regalata: la pagina è già lì, mostrala.
2b. **Manifest, service worker e icone vivono nella cartella del progetto**
   (`apps/<slug>/`), e i loro path sono **relativi**: `"start_url": "."`,
   `"scope": "."`, icone come `icons/icon-512.png`. Un manifest con path assoluti
   (`/icon.png`, `start_url: "/"`) funziona solo se l'app sta nella root del dominio
   — servita da una sottocartella si rompe in silenzio: niente icona, niente
   standalone, e l'installazione fallisce senza dire perché.
3. **`background_color` del manifest identico al fondo dello splash.** Se
   differiscono, fra splash e primo schermo compare il lampo bianco — il fallimento
   più comune e più visibile delle PWA.
4. Lo splash è **il solo momento in cui l'app parla da sola**: o dice il marchio, o
   non esiste (`first-frame`). Non è il posto per uno slogan.

### Fondo d'app — e il gradiente

Questo è il punto dove la regola generale e la superficie mobile si toccano.
`craft-rules.md` → Superfici **vieta il gradiente lineare a tutta pagina** come
fondo di sezione, ed è una regola giusta: su una landing è il modo più rapido per
rendere sei sezioni uguali. **Su una web app mobile l'eccezione è dichiarata**, con
un perimetro preciso:

- l'eccezione vale per **la shell dell'app** (una superficie continua, vista mille
  volte, che deve dire il marchio senza contenuto) — **non** per le sezioni di una
  landing, dove il divieto resta pieno;
- il gradiente è **uno** e attraversa tutta l'app: se ogni schermata ha il suo, non
  è un fondo di marca, è decorazione;
- i colori vengono da `palette_family` — nessuna tinta nuova introdotta dal fondo;
- l'angolo è **l'angolo di casa** già dichiarato (`craft-rules.md` → Superfici §5),
  non un `135deg` di riflesso.

Regole tecniche non negoziabili, tutte verificabili:

1. **Contrasto sui due estremi, non nel punto medio.** Il testo che ci scorre sopra
   deve reggere AA sulla fermata più chiara **e** sulla più scura. Se non regge, si
   cambia il testo (pannello, peso, colore), non si annacqua il gradiente.
2. **Grana anti-banding obbligatoria.** Un gradiente ampio su schermo mobile mostra
   le fasce: `feTurbulence` o un noise data-URI a bassa opacità sopra.
3. **Animato solo su `transform` / `opacity`.** Animare `background-position` o i
   color-stop ridipinge ogni frame a schermo intero: batteria e jank garantiti.
   `prefers-reduced-motion` ferma anche il fondo.
4. **Il gradiente non è il fallback per non decidere.** Se il fondo è gradiente, la
   texture di superficie è zero o quasi: due linguaggi decorativi insieme sono
   rumore. `solid-texture` è la scelta opposta, altrettanto valida, e va dichiarata
   con la stessa serietà.

### Altezza viewport e barra sempre visibile (solo web app)

Una web app non è una pagina che scorre: è una **shell alta quanto la viewport**, con
dentro una sola area che scorre. La barra di navigazione in basso deve essere sempre
lì — è la cosa che distingue una app da una landing stretta, e va applicata **sempre
su mobile app, mai su landing**.

```html
<meta name="viewport"
      content="width=device-width, initial-scale=1, viewport-fit=cover,
               interactive-widget=resizes-content">
```

```css
.app {
  height: 100svh;              /* stabile: la barra del browser non la accorcia  */
  overflow: hidden;            /* la pagina non scorre mai                        */
  display: grid;
  grid-template-rows: auto 1fr auto;   /* header · contenuto · barra              */
}
.app__main {
  overflow-y: auto;
  overscroll-behavior: contain;        /* niente rimbalzo che scopre il fondo     */
}
.app__tabs {
  padding-bottom: env(safe-area-inset-bottom);   /* dentro la sua altezza         */
}
```

1. **La barra è la terza riga della griglia, non `position: fixed`.** Fissarla
   sembra equivalente e non lo è: con `fixed` devi compensare l'ultimo elemento
   della lista con un padding a mano (e prima o poi sbagli il valore), e con la
   tastiera aperta su iOS la barra fissa scavalca l'input. Come riga di griglia,
   il `1fr` del contenuto si adatta da solo.
2. **`100svh` o `100dvh`?** `svh` è l'altezza più piccola (barra del browser
   estesa): stabile, nessun reflow durante lo scroll, la barra è sempre dentro.
   `dvh` segue la viewport reale e recupera quei pixel, al prezzo di un
   ridimensionamento continuo mentre si scorre. Default **`svh`**; `dvh` solo se
   quei pixel servono davvero, e va dichiarato. Installata in standalone le due
   coincidono: il problema esiste solo in scheda browser.
3. **Tastiera:** `interactive-widget=resizes-content` fa restringere il contenuto
   invece di far scorrere tutto. Se la barra si ritira al focus di un campo è una
   scelta legittima — coprire l'input attivo non lo è mai.
4. **Il contenuto non finisce sotto la barra:** con la griglia questo è gratis. Se
   ti trovi a scrivere `padding-bottom: 72px` da qualche parte, la shell è sbagliata.
5. `overscroll-behavior: contain` sul `main`: senza, il rimbalzo iOS scopre il fondo
   della pagina sotto la app e rompe l'illusione di superficie continua.

**Questo è il punto che distingue un'app da una pagina web.** Una landing scorre
libera dall'alto in basso: è la sua natura, il contenuto è il flusso. Una web app
mobile **non deve mai comportarsi così** — se scrolli e la barra sparisce, o se
l'header rifluisce col contenuto invece di restare fermo, quella non è un'app,
è una pagina responsive travestita.

Fallimento: pagina che scorre tutta e barra che sparisce scrollando; barra `fixed`
con padding di compensazione; ultimo elemento della lista coperto; barra sopra la
tastiera; `100vh` che lascia la barra fuori schermo quando la barra del browser è
estesa; **contenuto che scorre "alla desktop"** — l'intera viewport che trasla
invece del solo `main`.

### Contenuto senza dati reali: immagini, non segnaposti

Una demo mobile viene quasi sempre costruita **senza backend collegato**: niente
foto prodotto vere, niente avatar utente, niente copertina articolo. Il riflesso
sbagliato è coprire quel buco con un segnaposto — un rettangolo grigio, un'icona
"IMG" al centro, la scritta `placeholder.jpg`. Il risultato dichiara «questo non
è pronto» in ogni schermata, il contrario di quello che una demo deve fare.

1. **Ogni contenuto visivo che dipende dai dati (foto prodotto, copertina,
   thumbnail lista, sfondo card) è un'immagine reale**, non un blocco muto —
   stessa fonte già in uso nelle demo Vesper: URL Unsplash diretti, mirati al
   soggetto (`photo-1559339352-...` per un piatto, non un grigio `#e5e5e5`).
   Il criterio è lo stesso di `assets/hero-media/`: campioni realistici, non
   proposte finali, ma **mai finti nell'aspetto**.
2. **La query dell'immagine segue il dominio**, non è generica: un'app
   `food` mostra piatti veri, un'app `fitness` mostra allenamento vero, un'app
   `travel` mostra luoghi veri. Un'immagine di scorta qualunque (uno sfondo
   astratto, uno stock "business") è ancora un placeholder travestito.
3. **Eccezione dichiarata, una sola:** l'avatar di un utente che non ha
   caricato una foto. Lì l'iniziale su un tondo a tinta piena (dalla palette)
   è lo stato corretto, non un placeholder — è informazione vera ("questo
   utente non ha foto"), non un buco coperto.
4. **Non è lo stesso problema dello stato di caricamento né dello stato vuoto.**
   Lo skeleton (`state_treatment`) resta per l'attesa vera, quando i dati stanno
   arrivando; `illustrated-empty` resta legittimo quando i risultati sono
   **davvero zero** ("nessun ordine ancora", "nessun risultato per il filtro") —
   lì l'illustrazione dice "non c'è niente", ed è vero. Questa regola riguarda
   il caso diverso: la card **esiste** nella lista (con un DB reale avrebbe una
   foto), e va mostrata con un prodotto vero, non con un rettangolo che finge
   un'assenza che non c'è.
5. Se il progetto ha davvero un catalogo immagini proprio (media library,
   asset del cliente), quelli hanno sempre la precedenza: questa regola vale
   quando quel collegamento **non c'è ancora**, non come sostituto permanente.

Fallimento: card prodotto con sfondo `#eee` e icona immagine; avatar tutti
uguali con la stessa iniziale "U"; una sola foto stock ripetuta su ogni card
della lista; sfondo generico non coerente col dominio (un tramonto stock su
un'app bancaria).

### Marchio, onboarding, illustrazione, profondità

- **Marchio:** icona `maskable` con il glifo dentro la safe zone (su Android la
  maschera taglia gli angoli), leggibile a 48px, più `apple-touch-icon`. Un logo
  rettangolare rimpicciolito non è un'icona d'app.
- **Onboarding:** `none-declared` è una scelta legittima e spesso la migliore. Il
  carosello di tre schermate va giustificato: se serve a spiegare l'ovvio, il
  problema è la app. Il `permission-primer` prima del permesso di sistema alza
  l'accettazione e si scrive una volta.
- **Illustrazione:** un linguaggio solo, coerente fra vuoti, errori e onboarding.
  `none-icon-only` è dichiarabile; mischiare tre stili no.
- **Profondità:** una regola sola. `flat-rules` con hairline, oppure 2–3 livelli di
  ombra **nominati come token**. Il `glass-layer` sta su **un** livello: due
  `backdrop-filter` sovrapposti costano il doppio su telefono, e su fondo sfocato
  non si vedono nemmeno.

## Invarianti (non sorteggiabili)

Sono stampati in ogni ricetta e valgono sempre: `viewport-fit=cover` +
`env(safe-area-inset-*)`; altezze in `dvh`/`svh` mai `100vh`; target ≥44px e azione
primaria in thumb zone; manifest completo con `background_color` allineato allo
splash e icona `maskable`; splash solo in standalone; contrasto del gradiente sui
due estremi; grana anti-banding; gradiente animato solo su GPU; input a
`font-size: 16px` con `inputmode`/`autocomplete`; empty + skeleton + errore per ogni
lista; nessun overflow-x e nessuna gesture di sistema rubata; `:focus-visible`,
contrasto AA, `prefers-reduced-motion`; motion repeat; hard-reject palette.

## Procedura

1. Corpus presente e non vecchio (`--stats`); se manca, `--build` o dichiara il gap.
2. Genera la ricetta col dominio giusto e le esclusioni da MEMORY. Su varianti
   sorelle usa `--batch`.
3. Per gli assi grafici guarda **a mano** Figma Community o Dribbble, oppure decidi
   dalla palette. Non fingere una ricerca che il corpus non può fare.
4. Traduci **ogni** asse in markup/CSS concreti. Se un asse non ha senso per il
   dominio, cambialo **e dichiara perché** — non ignorarlo in silenzio.
5. Verifica **installata**, non solo in scheda: lampo bianco all'avvio, safe area
   con la tastiera aperta, pollice su ogni azione primaria, contrasto sul fondo reale.
6. Aggiorna MEMORY: `last_palette_families`, `last_radius_families`,
   `last_type_voices`, `last_app_backgrounds`, `last_splashes`.

## Fallimenti

Landing schiacciata a 375px spacciata per app; lampo bianco fra splash e primo
schermo; gradiente viola-indaco «perché fa app»; gradiente con testo illeggibile su
una delle due fermate; fasce di banding su fondo ampio; icona senza safe zone
maskable tagliata su Android; `100vh` che salta quando la barra del browser si
ritrae; input che fanno zoomare iOS al focus; onboarding di tre schermate che
spiegano l'ovvio; due `backdrop-filter` sovrapposti; ricetta generata e poi ignorata.
