---
name: performance
description: CWV/TTFB — cache, asset, DB, hosting
code: PF
added: 2026-07-25
type: prompt
---

# Performance

## What Success Looks Like
L'owner ha priorità **misurabili** (TTFB, LCP, INP/CLS dove rilevante) e un piano ordinato: hosting/cache → query/DB → asset/plugin → fine-tuning. Un altro "speed plugin" come prima mossa senza baseline è fallimento.

## Non-inferables
- Chiedi o stima baseline (PageSpeed/Query Monitor/hosting) prima della lista infinita di ottimizzazioni.
- Distingui server (TTFB, object cache, PHP) da front-end (JS/CSS, immagini, font).
- Su Woo, tratta cart/checkout come casi speciali (cache bypass).
- Controlla MEMORY/BOND per hosting e stack cache già presenti.
