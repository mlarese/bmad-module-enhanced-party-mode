---
name: capability-authoring
description: How to author, register, and evolve learned capabilities
---

# Capability Authoring

When the owner wants a new ability, author it together while holding `references/prompt-quality-canon.md` (CREED standing order). Outcome: a registered learned capability future-you can invoke by code. Consumer: future Rex reading CAPABILITIES on wake. Do not restate persona — it is already loaded.

## Capability Types

### Prompt (default)
`capabilities/{name}.md` — judgment work; outcome + consumer + bar + non-inferables.

### Script
`capabilities/{name}.md` + `{name}.py` — deterministic one-job scripts; accept sanctum path as arg; never hardcode paths.

### Multi-file
`capabilities/{name}/` with a main guidance file plus optional structure/examples.

### External Skill Reference
Suggest an installed skill; always ask before installing. Register as `External: skill-name` in Learned.

## Prompt File Frontmatter

```markdown
---
name: {kebab-case-name}
description: {one line, what this does}
code: {2-letter menu code, unique across all capabilities}
added: {YYYY-MM-DD}
type: prompt | script | multi-file | external
---
```

## Create / refine / retire

Explore what they need, then draft and show — when confirmed: save under `capabilities/`, add a Learned row in CAPABILITIES.md, note the file under INDEX.md My Files, confirm the trigger code. Refine in place and log in the session. Retire by removing the Learned row (keep the file); apply the canon retirement test — if it no longer beats bare, retire rather than patch.
