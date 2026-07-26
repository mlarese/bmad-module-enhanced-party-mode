---
name: demo
description: Apri o integra la pagina demo di tutti gli effetti
code: DM
added: 2026-07-25
type: prompt
---

# Demo

## What Success Looks Like
La showcase in `demo/index.html` è aperta (o Mauro ha il path assoluto e sa come aprirla). Se chiede la demo **nel progetto**, copia `demo/` + `assets/anim.{css,js}` in una cartella pubblica e collega la route — senza ricreare da zero. Fallimento: riscrivere la demo esistente o lasciare card statiche.

## Non-inferables
- Apri con `bash scripts/open-demo.sh` (path skill root); fallback `open`/`xdg-open` sul path assoluto.
- Comunica le tre modalità: repeat allo scroll, replay hover/focus, loop ambientali (badge libreria).
- Estensioni catalogo: ogni voce deve avere animazione osservabile; se serve libreria, riproduci l’idea in CSS/JS e marca il badge.
