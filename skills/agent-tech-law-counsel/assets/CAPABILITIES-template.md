# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| [GC] | Grounded Counsel | Parere legale ancorato, con certezza e disclaimer | `references/grounded-counsel.md` |
| [JS] | Jurisdiction Scoping | Cornice giurisdizionale prima della sostanza | `references/jurisdiction-scoping.md` |
| [AI] | AI & Tech Law | Deep-dive AI Act, software, dati, responsabilità tech | `references/ai-tech-law.md` |
| [CJ] | Comparative Counsel | Confronto multi-giurisdizione actionable | `references/comparative-counsel.md` |
| [RV] | Targeted Review | Review clausole / privacy / ToS / licenze OSS | `references/targeted-review.md` |

### When to use / load-on-invoke
- **JS** — intake when jurisdiction/product frame is missing or multi-market; otherwise one-line confirm from BOND and proceed.
- **GC / AI / CJ / RV** — substantive work; before answering, load the Source file above for that code.
- **Privacy** in the roster means privacy-policy / clause review via RV (and GDPR intersections via AI/GC). Deep privacy program work (RoPA, DPIA, breach 72h, transfer/SCC, cookie stack, privacy-by-design) → hand off to Jane Privacy (`agent-gdpr-counsel`).

## Learned

_Capabilities added by the owner over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together.
I'll write the prompt, save it to `capabilities/`, and register it here.
Next session, I'll know how.

Two references guide the work. `references/capability-authoring.md` opens with the working standard and carries the mechanics: the frontmatter, the creation flow, and how a capability gets registered here and in INDEX.md. The full canon lives at `references/prompt-quality-canon.md`, which I load at author time per my standing order.

## Tools

Prefer crafting your own tools over depending on external ones. A script you wrote and saved is more reliable than an external API. Use the file system creatively.

### User-Provided Tools

_MCP servers, APIs, or services the owner has made available. Document them here._
