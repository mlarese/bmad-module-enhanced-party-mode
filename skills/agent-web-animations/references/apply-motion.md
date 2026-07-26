---
name: apply-motion
description: Scegli e inserisci animazioni opportune modificando il codice del progetto
code: AP
added: 2026-07-25
type: prompt
---

# Apply Motion

## What Success Looks Like
I **file del progetto** sono modificati: le animazioni opportune sono nel codice, al livello di stack minimo sufficiente. Il consumer è Mauro che apre la pagina e sente gerarchia e ritmo — non una chat con snippet. Inventare GSAP su un fade, ignorare lo stack già presente, o lasciare solo consigli senza edit è fallimento. Se stack + target (pagina/componente) sono già chiari, applica senza open-floor.

## Non-inferables
- Prima di aggiungere librerie: cerca cosa c’è già (`gsap`, `framer-motion`, `aos`, `@keyframes`, Lenis…).
- Ordine di stack: CSS > Web Animations API > Motion One > GSAP > WebGL.
- Default qualità: anima `transform`/`opacity`; reveal **repeat** (toggle `.is-visible`); one-shot solo con richiesta/`data-anim-once`; `prefers-reduced-motion` obbligatorio.
- Carica on-need: `references/catalog.md`, `references/recipes-css.md`, `references/recipes-js.md`, `references/frameworks.md`; riusa `assets/anim.css` + `assets/anim.js` quando copiare basta.
- Controlla MEMORY/BOND per brand-motion e stack del progetto.
- Dopo gli edit: indica file toccati e come verificare (scroll, hover, reduced-motion).
