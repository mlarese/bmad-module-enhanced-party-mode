---
name: audit-motion
description: Audit performance e accessibilità del motion esistente
code: AU
added: 2026-07-25
type: prompt
---

# Audit Motion

## What Success Looks Like
Mauro ha una checklist prioritizzata su fps/CLS/layout thrash e `prefers-reduced-motion`, con fix concreti (file o patch). Un saggio generico “usa transform” senza tocchi al progetto o findings specifici è fallimento quando il codice è disponibile.

## Non-inferables
- Carica `references/performance-a11y.md`.
- Controlla: proprietà animate, IO vs animazioni fuori viewport, loop su contenuto informativo, clip-path vs observer, media query reduced-motion già globale (non duplicare).
- Se i fix sono motion edits, applica o passa ad AP con i finding numerati.
