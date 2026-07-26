---
name: design-md-saas
description: Stampo DESIGN.md per SaaS marketing + product chrome
type: template
---

# DESIGN.md — SaaS (stampo)

Ibrido: landing prodotto (`--activity saas`) e/o shell app. Dichiare quale dei due è in scope.

```yaml
---
name: '{Product}'
description: '{Job-to-be-done in una riga}'
colors:
  surface-base: '#______'
  ink-primary: '#______'
  accent: '#______'
typography:
  display:
    fontFamily: '{Display}'
  body:
    fontFamily: '{Body}'
  ui:
    fontFamily: '{UI}'
rounded:
  sm: '{…}'
  md: '{…}'
components:
  button-primary: {}
  pricing-tier: {}
  nav: {}
---
```

## Brand & Style

Credibilità B2B/B2C senza purple-glow AI. Pricing e CTA leggibili; feature come prova, non decorazione.

## Layout & Spacing

- Marketing: hero + sezioni dal dominio (social proof, pricing, FAQ) — non stub
- Product: seguire regole dashboard se è admin; mobile-web-app se è app task

## Do's and Don'ts

- **Do:** batch `--activity saas` (Envato `saas` + `landing-page`)
- **Don't:** fintech-purple default; mock dashboard finta come hero unica
