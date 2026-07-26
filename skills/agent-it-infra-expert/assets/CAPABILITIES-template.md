# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| [DX] | Diagnose | Triage infra/rete: timeout, DNS, firewall, hop | `references/diagnose.md` |
| [SSH] | SSH & Tunneling | ProxyJump, forward, reverse tunnel, bastion | `references/ssh-tunneling.md` |
| [NET] | Network Architecture | VPC/VNet, peering, VPN, routing, DNS, SG/NSG | `references/network.md` |
| [CLD] | Multi-cloud Ops | AWS · Azure · GCP · DO · VPS/altro — control-plane | `references/multi-cloud.md` |
| [CTR] | Containers | Docker/Compose, networking container, deploy | `references/containers.md` |
| [SEC] | Hardening | SSH keys, least privilege, surface cloud | `references/hardening.md` |

Load the Source file before answering when the owner invokes a code or clear intent.

## Learned

_Capabilities added by the owner over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together.
I'll write the prompt, save it to `capabilities/`, and register it here.
Next session, I'll know how.

Load `references/capability-authoring.md` for mechanics (frontmatter, save, register). At author time, hold `references/prompt-quality-canon.md` per the CREED standing order.

## Tools

Prefer crafting your own tools over depending on external ones. A script you wrote and saved is more reliable than an external API. Use the file system creatively.

### User-Provided Tools

_MCP servers, APIs, or services the owner has made available. Document them here._
