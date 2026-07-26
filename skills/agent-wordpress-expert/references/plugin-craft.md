---
name: plugin-craft
description: Plugin custom hooks-safe e upgrade-safe
code: PL
added: 2026-07-25
type: prompt
---

# Plugin Craft

## What Success Looks Like
L'owner ha un piano o codice plugin **upgrade-safe**: hook giusti, capability checks, sanitizzazione/escaping, no edit di core, attivazione/disattivazione pulita. Preferisci mu-plugin o piccolo plugin dedicato a un monolite "utility kitchen sink". Un plugin che fa tutto e non si può aggiornare è fallimento.

## Non-inferables
- Non inventare hook/API: se non sei sicuro, dillo e proponi dove verificare nel core/docs.
- Default: least privilege, nonce su form admin, prepared statements / API WP per DB.
- Distingui "serve davvero un plugin" vs filtro in tema child / snippet controllato.
- Controlla MEMORY/BOND per coding standards e Composer/Bedrock.
