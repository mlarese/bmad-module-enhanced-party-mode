---
name: design-md-mobile-web-app
description: Modello di DESIGN.md per web app mobile / PWA (browser, non native)
type: template
---

# DESIGN.md — Mobile web app (modello)

**Non è una landing.** Task-first, e la prima cosa che si vede non è il contenuto:
è lo **splash** e il **fondo di marca**. Batch: `--surface mobile` (+ `--activity`
se vertical). Decisioni da seed: `mobile_recipe.py`. Regole: `references/mobile-rules.md`.

```yaml
---
name: '{App}'
description: '{Azione principale che l’utente ripete}'
colors:
  surface-base: '#______'
  ink-primary: '#______'
  accent: '#______'
  # il fondo di marca: un solo gradiente per tutta l'app, colori dalla palette
  app-bg-from: '#______'
  app-bg-to: '#______'
  app-bg-angle: '{l’angolo di casa, es. 135deg}'
typography:
  title:
    fontFamily: '{UI}'
  body:
    fontFamily: '{UI}'
  meta:
    fontFamily: '{UI}'
rounded:
  sm: '{…}'
  md: '{…}'
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
graphic:
  splash: '{first-frame | mark-draw | gradient-wash | type-lockup | photo-fade | mask-reveal}'
  app_background: '{mesh-gradient | linear-brand | radial-glow | duotone-fade | solid-texture | photo-blur}'
  brand_mark: '{maskable-glyph | monogram-tile | mark-on-gradient | line-mark}'
  onboarding: '{none-declared | three-cards | progressive | value-first | permission-primer}'
  illustration: '{geometric-shapes | line-art | photo-crop | type-as-image | none-icon-only}'
  depth: '{flat-rules | soft-elevation | glass-layer | stacked-cards}'
manifest:
  background_color: '{IDENTICO al fondo dello splash, o lampo bianco all’avvio}'
  theme_color: '#______'
  display: standalone
  icons: '192 · 512 · maskable (glifo dentro la safe zone)'
components:
  tab-bar: {}
  list-row: {}
  primary-fab-or-cta: {}
  bottom-sheet: {}
  empty-state: {}
---
```

## Brand & Style

Stesso gusto di marca della landing gemella, abito da lavoro: meno teatro, più
chiarezza a 3 secondi. Una job per schermata. Il fondo di marca è **uno** e
attraversa tutta l'app: se ogni schermata ha il suo, è decorazione.

## Layout & Spacing

- **Shell ad altezza viewport, barra sempre visibile** (solo app, mai landing):
  `height: 100svh` + `overflow: hidden` + `grid-template-rows: auto 1fr auto`;
  scorre il `main`, non la pagina. La barra è la **terza riga della griglia**, non
  `position: fixed` — niente padding di compensazione, niente barra sopra la tastiera
- `interactive-widget=resizes-content` nel meta viewport; `overscroll-behavior: contain` sul main
- Shell app: nav bassa o rail collassabile; thumb zone per l'azione primaria
- Target ≥44px; `viewport-fit=cover` + `env(safe-area-inset-*)`; no overflow-x
- Altezze in `dvh`/`svh` — mai `100vh`: la barra del browser si ritrae
- Input a `font-size: 16px` con `inputmode`/`autocomplete`, o iOS zooma al focus
- Stati: vuoto, loading (skeleton della forma giusta), errore — obbligatori sulle liste

## Contenuto senza backend

- **Mai segnaposti muti.** Senza dati reali, ogni foto prodotto / copertina / thumbnail
  è un'**immagine vera** (Unsplash, mirata al dominio), non un rettangolo grigio con icona IMG
- La query segue il dominio: `food` → piatti veri, `fitness` → allenamento vero, non stock generico
- Eccezione: avatar senza foto → iniziale su tondo di palette, quello è uno stato corretto
- Diverso dallo skeleton di caricamento: qui è il contenuto **statico** della demo

## Grafica — se il fondo è un gradiente

- Contrasto AA sui **due estremi**, non nel punto medio: cambia il testo, non il gradiente
- Grana anti-banding sopra (noise data-URI o `feTurbulence`), o su mobile si vedono le fasce
- Animato solo su `transform`/`opacity`; `prefers-reduced-motion` lo ferma
- Fondo a gradiente **e** texture di superficie insieme = rumore: scegline uno

## Dati verosimili (obbligatorio quando i contenuti non erano forniti)

Elenca **cosa è inventato e dove** — telefono, email, indirizzo, P.IVA, prezzi,
orari, recensioni. Non è la nota di sostituzione vietata nella pagina: lì
sporcherebbe il lavoro consegnato, qui documenta. La riga di onestà all'owner in chat
si dà comunque: questa risponde fra sei mesi a «ma questo numero è vero?».

```yaml
dati_verosimili:
  - campo: telefono
    valore: '{quello scritto in pagina}'
    nota: 'inventato — prefisso non assegnato'
  - campo: prezzi
    valore: '{range esposto}'
    nota: 'plausibili per {activity} a {locale}, non confermati dal cliente'
```

Se i contenuti li ha forniti l'owner o il sito del cliente, scrivi
`dati_verosimili: nessuno — contenuti dal cliente`.

## Do's and Don'ts

- **Do:** Envato `mobile` / `mobile-app` / `pwa` / `progressive-web-app` / `ui-kits`
  (+ vertical cats con activity); per lo **splash e il fondo** guarda a mano Figma
  Community — il corpus di codice non li copre e la ricetta lo dichiara
- **Don't:** hero full-bleed da landing; nav solo desktop; lampo bianco fra splash e
  app; gradiente viola-indaco «perché fa app»; icona rettangolare rimpicciolita al
  posto di una `maskable`; chiamarla "app" se è solo una homepage responsive; card
  prodotto con sfondo grigio e icona immagine; contenuto che scorre come una pagina
  intera invece che dentro la shell
