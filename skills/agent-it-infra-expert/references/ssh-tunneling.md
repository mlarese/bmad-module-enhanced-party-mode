---
name: ssh-tunneling
description: SSH, ProxyJump, forward e reverse tunnel
code: SSH
added: 2026-07-25
type: prompt
---

# SSH & Tunneling

## What Success Looks Like
L'owner ha un **path di accesso chiaro** (host → jump → target) e comandi o stanza `ssh/config` che risolvono il bisogno (shell, Local/Remote/Dynamic forward, reverse) con **scope e durata** espliciti. Un tunnel "magico" senza dire cosa espone e come chiuderlo è fallimento.

## Non-inferables
- Chiedi errore esatto (`ssh -vvv` se serve), hop (bastion/jump), user/key, e se serve forward o solo shell.
- Preferisci ProxyJump/`ProxyCommand` a catene ad-hoc; documenta `LocalForward`/`RemoteForward`/`DynamicForward` col perché.
- Non chiedere private key in chat; guida a `ssh-agent`, file locali, e rotazione se esposta.
- Controlla MEMORY/BOND per bastion e pattern SSH già noti.
