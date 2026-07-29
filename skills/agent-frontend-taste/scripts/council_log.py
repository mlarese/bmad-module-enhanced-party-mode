#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Il registro del consiglio: una riga per seduta, un file per progetto.

Perché esiste. Il consiglio decide tutto e non chiede niente all'owner: è la
legge dello skill (`references/autonomia.md`). Il prezzo è che l'owner non vede
**niente** di come si è arrivati alla pagina — quali agenti hanno parlato, chi
ha deciso cosa, quante volte è tornata indietro. Le decisioni finiscono nei sei
documenti e gli scostamenti in `docs/varianze/`, ma *chi era nella stanza* non
sta scritto da nessuna parte, e la chat sparisce.

Questo non è un verbale: è un **indice**. Una riga per seduta, e chi vuole il
contenuto va nel documento che quella riga nomina.

  docs/consiglio/<slug>.md

Usage:
    uv run scripts/council_log.py {project-root} --project <slug> \\
        --goal G1 --agents "Mary,John,Rex,Vesper" \\
        --outcome "landing, register famigliare, stack statico" [--slice S1]

    uv run scripts/council_log.py {project-root} --project <slug> --check

In **ciclo rapido** (`references/ciclo-rapido.md`) il consiglio non si riunisce, e
la riga serve a dire proprio quello — `--goal rapido --agents "Vesper"`. Un lavoro
senza consiglio è una scelta legittima dell'owner; un lavoro senza consiglio che
*sembra* averlo avuto no, e fra sei mesi le due cose si distinguono solo qui.

Exit: 0 scritto / registro presente · 1 registro assente o vuoto (in --check)
      · 2 riga rifiutata perché non è breve (non è un verbale)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import sys
from pathlib import Path

# Una riga. Oltre questa misura non è più un indice: è il documento che
# l'indice dovrebbe puntare, copiato nel posto sbagliato.
OUTCOME_MAX = 160

GOALS = {
    "g1": "G1 lettura",
    "g2": "G2 documenti",
    "controllo": "controllo documenti",
    "g3": "G3 approvazione",
    # In ciclo rapido non si siede nessuno: la riga esiste per dire **quello**.
    # Scritta com'era — «rapido» — sembrava il nome di una seduta veloce; scritta
    # così dice che seduta non ce n'è stata (`references/ciclo-rapido.md` §6).
    "rapido": "ciclo rapido (nessuna seduta)",
}

HEADER = """# Consiglio — {slug}

Una riga per seduta: data · obiettivo · chi ha parlato · cosa si è deciso.
È un **indice**, non un verbale — le decisioni stanno nei sei documenti
(`planning-artifacts/`), gli scostamenti in `docs/varianze/`.

"""

ENTRY_RE = re.compile(r"^- \*\*\d{4}-\d{2}-\d{2}", re.M)


SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def log_path(root: Path, slug: str) -> Path:
    """Lo slug e un nome, non un percorso.

    Senza questo controllo `--project ../../../fuori` scriveva **fuori dal
    progetto**: la legge dello skill ha un solo confine — le azioni fuori dal
    workspace — e un registro che lo attraversa per distrazione lo viola lo
    stesso.
    """
    if not SLUG_RE.match(slug or ""):
        raise SystemExit(
            f"slug non valido: '{slug}'. Serve un nome di progetto — lettere, "
            "cifre, punto, trattino — non un percorso: il registro si scrive "
            "dentro `docs/consiglio/`, mai fuori dal progetto."
        )
    return root / "docs" / "consiglio" / f"{slug}.md"


def normalise_goal(goal: str) -> str:
    return GOALS.get(goal.strip().lower(), goal.strip())


def format_agents(raw: str) -> str:
    """Chi ha **parlato**, non chi era convocato: al tavolo ci sono tutti."""
    names = [a.strip() for a in re.split(r"[,·;]", raw) if a.strip()]
    if not names:
        raise SystemExit("--agents vuoto: una seduta senza nessuno che parla non è una seduta")
    return " · ".join(names)


def append(root: Path, slug: str, goal: str, agents: str, outcome: str,
           slice_: str | None, date: str | None) -> tuple[int, str]:
    outcome = " ".join(outcome.split())
    if len(outcome) > OUTCOME_MAX:
        return 2, (
            f"--outcome è lungo {len(outcome)} caratteri, il massimo è {OUTCOME_MAX}.\n"
            "Il registro è un indice, non un verbale: se non sta in una riga, "
            "quello che stai scrivendo è una varianza (`docs/varianze/`) o un "
            "pezzo di documento — scrivilo lì e qui lascia il rimando."
        )

    when = date or _dt.date.today().isoformat()
    label = f"{when} · {normalise_goal(goal)}"
    if slice_:
        label = f"{when} · {slice_.strip().upper()} · {normalise_goal(goal)}"

    path = log_path(root, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(HEADER.format(slug=slug), encoding="utf-8")

    line = f"- **{label}** — {format_agents(agents)} → {outcome}\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)
    return 0, f"{path}\n{line.rstrip()}"


def check(root: Path, slug: str) -> tuple[int, str]:
    path = log_path(root, slug)
    if not path.is_file():
        return 1, (
            f"nessun registro del consiglio in `{path}`: il consiglio ha deciso "
            "tutto senza lasciare traccia di chi c'era. Una riga per seduta, "
            "scritta quando la seduta si chiude."
        )
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = ENTRY_RE.findall(text)
    if not entries:
        return 1, f"`{path}` esiste ma non ha nemmeno una seduta: è un file vuoto con un titolo."
    last = [l for l in text.splitlines() if l.startswith("- **")][-1]
    return 0, f"{path} — {len(entries)} sedute registrate.\nUltima: {last}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Registro del consiglio, una riga per seduta")
    ap.add_argument("root", help="{project-root}")
    ap.add_argument("--project", required=True, help="slug del progetto (la cartella in apps/)")
    ap.add_argument("--check", action="store_true", help="verifica che il registro esista e non sia vuoto")
    ap.add_argument("--goal", help="G1 | G2 | controllo | G3 | rapido (o testo libero)")
    ap.add_argument("--agents", help="chi ha parlato, separati da virgola")
    ap.add_argument("--outcome", help="cosa si è deciso, in una riga")
    ap.add_argument("--slice", dest="slice_", help="la slice in corso, es. S1")
    ap.add_argument("--date", help="YYYY-MM-DD (default: oggi)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"project-root inesistente: {root}")

    if args.check:
        state, msg = check(root, args.project)
    else:
        missing = [n for n, v in (("--goal", args.goal), ("--agents", args.agents),
                                  ("--outcome", args.outcome)) if not v]
        if missing:
            raise SystemExit(f"servono {', '.join(missing)} per registrare una seduta "
                             "(o --check per verificare il registro)")
        state, msg = append(root, args.project, args.goal, args.agents,
                            args.outcome, args.slice_, args.date)
    print(msg)
    return state


if __name__ == "__main__":
    sys.exit(main())
