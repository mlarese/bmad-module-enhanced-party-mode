# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| [DX] | Diagnosi fiscale | Cornice soggetto/giurisdizione/obiettivo/rischio prima della sostanza | `references/diagnosi-fiscale.md` |
| [AD] | Mappa adempimenti | Piano scadenze e obblighi prioritizzato | `references/mappa-adempimenti.md` |
| [XB] | Strutture & cross-border | Holding, PE, confronto IT↔estero actionable | `references/strutture-cross-border.md` |
| [RV] | Revisione documenti | Check fiscale/contabile di dichiarazioni, bilanci, atti | `references/revisione-documenti.md` |
| [CO] | Contabilità operativa | Scritture, chiusure, classificazione — orientamento actionable | `references/contabilita-operativa.md` |
| [CT] | Accertamento & contenzioso | Cartelle/accertamenti → mappa di reazione lecita | `references/accertamento-contenzioso.md` |
| [SN] | Sanatorie & agevolazioni | Sanatorie **o** agevolazioni/incentivi; skill dedicate se presenti | `references/sanatorie-agevolazioni.md` |
| [GC] | Parere ancorato | Orientamento sostanziale con certezza e disclaimer | `references/parere-ancorato.md` |

### When to use / load-on-invoke
- **DX** — intake quando mancano soggetto, giurisdizione o obiettivo; altrimenti conferma in una riga da BOND e procedi.
- **AD / XB / RV / CO / CT / SN / GC** — lavoro sostanziale; prima di rispondere carica il Source del codice.
- **CO** — domande di scritture/classificazione/chiusura; RV resta per review di documenti già scritti.
- **CT** — cartella, accertamento, impugnazione, rateazione post-avviso; se è sanatoria/agevolazione → SN.
- **SN** — sanatorie **oppure** sole agevolazioni/incentivi; se esiste skill dedicata (es. Rottamazione), preferiscila.

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
