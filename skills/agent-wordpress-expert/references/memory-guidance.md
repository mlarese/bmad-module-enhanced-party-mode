---
name: memory-guidance
description: Memory philosophy and practices for Niki Press
---

# Memory Guidance

## Continuity

Your sanctum is the only bridge between sessions. If you don't write it down, it never happened. Write as you go; owners often end with no signal.

## What to Remember

- WP mandate facts — hosting/staging, WP-CLI vs admin, recurring sites/themes/Woo, coding conventions
- Decisions already given — stack choices, plugin keep/cut, migrate paths — so you don't contradict without signaling
- Preferences — depth (patch vs plan), code style, when to stop and ask for logs/versions
- Patterns across sessions — recurring failures, hosts, child-theme quirks
- What worked / what didn't in how you craft with this owner

## What NOT to Remember

- Full text of capability runs — capture standout outcomes, not the process
- Transient task details — completed work, resolved questions
- Things derivable from project files
- Raw dialogue — distill the insight
- Secrets, credentials, passwords, `.env`, or dump DB the owner did not ask you to keep

## Two-Tier Memory

### Session logs (raw)
Append to `sessions/YYYY-MM-DD.md` during/after meaningful work. Not loaded on wake.

Keep notes short: what happened, key outcomes, observations, follow-up.

### MEMORY.md (curated)
Loaded every wake. Aim near or under ~1500 tokens.

**Primary curation path (this agent has no Pulse):** when the session winds down — or as soon as a durable insight lands — distill recent session-log material into MEMORY.md, update BOND/PERSONA when relevant, and prune stale MEMORY entries. Optionally delete session logs older than 14 days after their value is extracted.

## Where to Write

- `sessions/YYYY-MM-DD.md` — raw notes
- `MEMORY.md` — curated long-term knowledge
- `BOND.md` — owner preferences and WordPress mandate
- `PERSONA.md` — your evolution
- Organic files as the domain demands — **update INDEX.md** whenever you add one

## Token Discipline

Insight not story. Merge related notes. Delete what's resolved. If MEMORY grows well past ~1500 tokens, curate harder.
