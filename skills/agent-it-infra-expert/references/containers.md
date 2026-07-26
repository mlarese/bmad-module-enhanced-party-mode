---
name: containers
description: Docker Compose networking e deploy lean
code: CTR
added: 2026-07-25
type: prompt
---

# Containers

## What Success Looks Like
L'owner ha una causa o un piano **sul container runtime**: rete (bridge/host/overlay), DNS interno, porte pubblicate, volume, compose service — verificabile con `docker`/`compose` inspect e log. "Riavvia il container" senza ipotesi è fallimento.

## Non-inferables
- Chiedi compose vs singolo container, host OS, se il problema è reachability o app, e porte coinvolte.
- Distingui fallimento del processo nel container da fallimento di rete/DNS/volume.
- Deep Kubernetes cluster-admin è fuori scope salvo richiesta esplicita — dichiara il confine.
- Controlla MEMORY/BOND per host e pattern di deploy già noti.
