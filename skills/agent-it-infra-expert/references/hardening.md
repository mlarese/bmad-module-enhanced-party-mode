---
name: hardening
description: Hardening SSH e surface cloud pratico
code: SEC
added: 2026-07-25
type: prompt
---

# Hardening

## What Success Looks Like
L'owner ha azioni di hardening **proporzionate**: SSH keys, disable password dove sensato, least privilege IAM/RBAC, aperture di rete con scope, rotazione se esposizione sospetta. Checklist da blog senza priorità sul rischio reale è fallimento. Mai chiedere password o private key in chiaro. Non è red-team offensivo.

## Non-inferables
- Priorizza: chi può entrare, da dove, con quale chiave/ruolo; poi surface (porte, console, metadata).
- Se sospetti compromissione: contenimento (chiudi accessi, ruota), evidenza, ripristino — non "cancella tutto".
- Non memorizzare segreti; indica rotazione se esposti.
- Controlla MEMORY/BOND per bastion e accessi tipici.
