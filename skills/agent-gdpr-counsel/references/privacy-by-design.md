---
name: privacy-by-design
description: Feature → rischi + controlli pre-build
code: PD
added: 2026-07-25
type: prompt
---

# Privacy by Design

## What Success Looks Like
Data una feature (o redesign), l'owner riceve: dati toccati, finalità, base giuridica candidata, rischi per gli interessati, controlli minimi (minimizzazione, retention, access control, logging, UI di consenso se serve), e flag se scattano DPIA / DPO / transfer / cookie. Il consumatore è Mauro o il team prodotto prima del build. Compliance-after-ship consigliata come piano A è fallimento.

## Non-inferables
- Art. 25 (data protection by design and by default) è la cornice; collega ad art. 5 principi quando serve.
- Preferisci controlli implementabili questa sprint, non architetture fantasma.
- Se la feature tocca AI/profiling, segnala overlap AI Act e quando passare anche da Elena.
- Controlla BOND/MEMORY per prodotti e vincoli già noti.
- Chiudi con il disclaimer formale da CREED.
