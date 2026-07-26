---
name: diagnose
description: Triage infra/rete — causa + piano + rimedio
code: DX
added: 2026-07-25
type: prompt
---

# Diagnose

## What Success Looks Like
L'owner ha una **causa radice** (o 2–3 ipotesi ordinate), un piano di check **verificabile**, e un **rimedio concreto** (o il load esplicito della capability specialty — SSH/NET/CLD/CTR/SEC — se il next step è fuori dal triage). Inventare "è il firewall" senza segnale è fallimento. Se sintomo+hop+provider/env sono già nel messaggio, produci ipotesi+check+rimedio senza open-floor.

## Non-inferables
- Chiedi 1–2 fatti mancanti critici solo se mancano; se i fatti ci sono, non intervistare.
- Distingui sintomo (timeout, connection refused, NXDOMAIN, 502) da causa (route, SG, DNS, processo down, MTU).
- Preferisci check read-only prima di cambiare regole di rete.
- Controlla MEMORY/BOND per ambienti e bastion già noti.
- Dopo la causa: rimedio o handoff esplicito alla Source specialty — non chiudere sul solo check plan.
