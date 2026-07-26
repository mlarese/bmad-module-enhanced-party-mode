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
