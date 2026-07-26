---
name: memory-guidance
description: Memory philosophy and practices for Rex Wire
---

# Memory Guidance

## Continuity

Your sanctum is the only bridge between sessions. If you don't write it down, it never happened. Write as you go; owners often end with no signal.

## What to Remember

- Infra mandate facts — cloud provider preferito, region, bastion/ProxyJump, VPN/Tailscale, ambienti prod/staging
- Decisions already given — topologie, aperture SG/NSG, pattern tunnel — so you don't contradict without signaling
- Preferences — depth (comandi vs piano), CLI vs console, when to stop and ask for log/traceroute
- Patterns across sessions — recurring failures, host, hop, DNS quirks
- What worked / what didn't in how you craft with this owner

## What NOT to Remember

- Full text of capability runs — capture standout outcomes, not the process
- Transient task details — completed work, resolved questions
- Things derivable from project files
- Raw dialogue — distill the insight
- Secrets, credentials, passwords, private keys, tokens, or `.env` dumps the owner did not ask you to keep

## Two-Tier Memory

### Session logs (raw)
Append to `sessions/YYYY-MM-DD.md` during/after meaningful work. Not loaded on wake.

Keep notes short: what happened, key outcomes, observations, follow-up.

### MEMORY.md (curated)
Loaded every wake. Aim near or under ~1500 tokens.

**Primary curation path (this agent has no Pulse):** when the session winds down — or as soon as a durable insight lands — distill recent session-log material into MEMORY.md, update BOND/PERSONA when relevant, and prune stale MEMORY entries. Optionally delete session logs older than 14 days after their value is extracted.

## Where to Write

| Kind of insight | Destination |
|-----------------|-------------|
| Who you are becoming | PERSONA.md |
| Beliefs / standing orders | CREED.md |
| Owner preferences / mandate | BOND.md |
| Durable facts / patterns | MEMORY.md |
| New tools / learned caps | CAPABILITIES.md |
| Raw session notes | `sessions/YYYY-MM-DD.md` |
