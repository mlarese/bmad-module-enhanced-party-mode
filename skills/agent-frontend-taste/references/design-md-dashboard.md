---
name: design-md-dashboard
description: Modello di DESIGN.md per dashboard / admin product
type: template
---

# DESIGN.md — Dashboard (modello)

Usa con `dashboard_recipe.py` + batch `--surface dashboard`. Light **e** dark della stessa famiglia.

```yaml
---
name: '{Product}'
description: '{Admin / ops shell — una riga}'
colors:
  surface-base: '#______'
  surface-base-dark: '#______'
  ink-primary: '#______'
  ink-primary-dark: '#______'
  accent: '#______'
  accent-dark: '#______'
typography:
  ui:
    fontFamily: '{UI sans}'
  data:
    fontFamily: '{tabular / mono if needed}'
rounded:
  sm: '{radius_family}'
  md: '{…}'
components:
  sidebar: {}
  kpi: {}
  data-table: {}
---
```

## Brand & Style

Chiarezza e densità controllata. Firma da ricetta (`signature`). No hero marketing.

## Layout & Spacing

Decisioni da ricetta: `shell` · `header_bar` · `kpi_style` · `table_pattern` · …

## Tabelle (obbligatorio quando la dashboard ne ha una)

Paginazione e filtro non sono dettagli di implementazione: sono la differenza fra
una tabella che regge trecentomila righe e una che regge quelle finte. Si
dichiarano qui — `dashboard-rules.md` → *Tabelle: paginazione e filtro multicampo*.

```yaml
paginazione:
  modo: 'server-side'          # server-side | in pagina (solo se un documento lo impone)
  strategia: 'offset'          # offset | cursore — e perché, in mezza riga
  per_pagina: 25
  totale_esposto: true         # «1–25 di 340»
filtro:
  modo: 'server-side'
  campi: ['stato', 'intervallo date', 'cliente (autocomplete)']
  autocomplete: ['cliente']
  debounce_ms: 250
  requisiti_backend: 'spec-{slug}.md — endpoint, autorizzazione, tetto risultati, rate limit'
deroga: 'no'                   # se un documento impone altro: quale documento, e perché
```

**Se un documento vincolante impone altro** (lista corta, insieme chiuso e piccolo)
comanda lui: si scrive in `deroga:` quale documento e perché. Un `deroga:` vuoto
quando la tabella non è paginata è una decisione presa per riflesso.

## Account (obbligatorio quando la dashboard ha accessi)

`dashboard-rules.md` → *Account: profilo, logout, admin — sempre*.

```yaml
account:
  profilo: true                 # cambio password con password attuale richiesta
  logout: 'server-side'         # chiude la sessione sul server, non solo il token
  ruoli: ['admin', '{…}']       # l'admin esiste dal primo account
  reset_admin: 'link monouso'   # mai una password scelta e conosciuta dall'admin
  token_reset: 'monouso · scadenza {…} · cifrato a riposo · invalida le sessioni'
  audit: 'chi resetta chi, e quando'
  credenziali_default: 'nessuna — primo avvio obbliga a impostarle'
  requisiti_backend: 'spec-{slug}.md'
deroga_account: 'no'            # se un documento impone altro: quale, e perché
```

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

- **Do:** mix ≥30 Envato admin; dual theme; row-click; empty+skeleton
- **Don't:** cinque card KPI clone; solo light; Inter come display; clone un template
