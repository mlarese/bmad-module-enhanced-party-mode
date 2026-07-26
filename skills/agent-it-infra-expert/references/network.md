---
name: network
description: Architetture di rete cloud e troubleshooting
code: NET
added: 2026-07-25
type: prompt
---

# Network Architecture

## What Success Looks Like
L'owner ha una **topologia utile**: chi parla con chi, su quale path (VPC/VNet, peering, VPN, Private Link/endpoint), con **bordi** (SG/NSG, route, DNS) espliciti — o un piano di fix su un path rotto. Un diagramma generico senza bordi è fallimento. CLD resta sul control-plane (account/IAM/servizi); il path è qui.

## Non-inferables
- Chiedi provider, CIDR/segmenti rilevanti, direzione del traffico, e se DNS è privato/pubblico.
- Preferisci least privilege su aperture; se serve un hole temporaneo, dichiara scope e chiusura.
- Distingui L3 (route/peering) da L4 (SG/NSG/firewall) da DNS.
- Controlla MEMORY/BOND per ambienti e pattern di rete già noti.
