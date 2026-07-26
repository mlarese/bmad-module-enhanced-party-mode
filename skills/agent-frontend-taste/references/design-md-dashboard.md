---
name: design-md-dashboard
description: Stampo DESIGN.md per dashboard / admin product
type: template
---

# DESIGN.md — Dashboard (stampo)

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

Assi da ricetta: `shell` · `header_bar` · `kpi_style` · `table_pattern` · …

## Do's and Don'ts

- **Do:** mix ≥30 Envato admin; dual theme; row-click; empty+skeleton
- **Don't:** cinque card KPI clone; solo light; Inter come display; clone un template
