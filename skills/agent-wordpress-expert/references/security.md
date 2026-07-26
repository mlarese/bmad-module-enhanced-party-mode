---
name: security
description: Hardening pratico + triage incidente WP
code: SC
added: 2026-07-25
type: prompt
---

# Security

## What Success Looks Like
L'owner ha azioni di hardening o triage **concrete**: auth, update strategy, file perms, headers, least privilege, e (se incidente) contenimento → evidenza → ripristino. Checklist da blog senza priorità sul rischio reale è fallimento. Mai chiedere password in chiaro.

## Non-inferables
- In sospetto malware: isola (maintenance/staging), non "cancella a caso"; guida a backup e scansione.
- Preferisci misure proporzionate al rischio (login, XML-RPC, file editing admin) rispetto a plugin security monolitici non giustificati.
- Non memorizzare segreti; indica rotazione se esposti.
- Controlla MEMORY/BOND per hosting e accessi tipici.
