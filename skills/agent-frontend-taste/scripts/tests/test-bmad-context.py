# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for bmad_context.py — run: uv run scripts/tests/test-bmad-context.py"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "bmad_context.py"


def load():
    spec = importlib.util.spec_from_file_location("bmad_context", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bmad_context"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def make_project(root: Path, *, with_docs: bool, custom_paths: bool = False) -> None:
    planning = "plans" if custom_paths else "_bmad-output/planning-artifacts"
    implementation = "impl" if custom_paths else "_bmad-output/implementation-artifacts"
    if custom_paths:
        (root / "_bmad").mkdir(parents=True)
        (root / "_bmad" / "config.toml").write_text(
            f'planning_artifacts = "{{project-root}}/{planning}"\n'
            f'implementation_artifacts = "{{project-root}}/{implementation}"\n',
            encoding="utf-8",
        )
    (root / planning).mkdir(parents=True, exist_ok=True)
    (root / implementation).mkdir(parents=True, exist_ok=True)
    if with_docs:
        (root / planning / "prd-app.md").write_text(
            "---\ntitle: 'PRD App'\n---\n# PRD\nrequisiti.\n", encoding="utf-8")
        (root / planning / "architecture-app.md").write_text(
            "# Architettura\n\n## Tech stack\n- Next.js 15\n- Tailwind 4\n\n"
            "## Regole di architettura\n- componenti in `app/components`\n\n## Altro\nx\n",
            encoding="utf-8")
        (root / planning / "ux-spec-home.md").write_text(
            "---\ntitle: 'UX Home'\n---\ncorpo\n", encoding="utf-8")
        (root / implementation / "spec-vecchia.md").write_text(
            "---\ntitle: 'Spec vecchia'\n---\nfatta.\n", encoding="utf-8")
        (root / "CLAUDE.md").write_text("regole progetto\n", encoding="utf-8")
        (root / "package.json").write_text(
            json.dumps({"dependencies": {"next": "15.0.0", "react": "19.0.0"}}),
            encoding="utf-8")


def main() -> int:
    fails = 0
    mod = load()

    def check(label: str, got, want) -> None:
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- full project: everything found and binding ------------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=True)
        d = mod.discover(root)
        check("PRD trovato", [e["title"] for e in d["prd"]], ["PRD App"])
        check("architettura trovata", len(d["architecture"]), 1)
        check("UX spec trovata e separata dal PRD", [e["title"] for e in d["ux_specs"]], ["UX Home"])
        check("spec di implementazione elencati", len(d["implementation_specs"]), 1)
        check("project context (CLAUDE.md) rilevato", len(d["project_context"]), 1)
        check("verdetto: vincoli attivi", d["binding"], True)
        check("stack estratto dall'architettura", "Next.js 15" in (d["stack_section"] or ""), True)
        check("regole estratte dall'architettura",
              "app/components" in (d["rules_section"] or ""), True)
        check("segnali repo: next e react dal package.json",
              {"next", "react"} <= set(d["repo_stack_signals"]), True)

        md = mod.render_md(d)
        check("il report dichiara lo stack obbligatorio", "obbligatorio" in md, True)
        check("il report dà il verdetto vincolante", "VINCOLI ATTIVI" in md, True)
        check("copertura piena: nessun avviso", "AVVISA" in md, False)
        check("con architettura e context: nessun canone imposto",
              "CANONE DI SVILUPPO" in md, False)
        r = run(str(root), "--format", "json")
        check("CLI json valido e coerente", json.loads(r.stdout)["binding"], True)

    # --- empty project: autonomous path, declared --------------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=False)
        d = mod.discover(root)
        check("verdetto: nessun vincolo", d["binding"], False)
        md = mod.render_md(d)
        check("il report impone l'analisi autonoma", "NESSUN DOCUMENTO VINCOLANTE" in md, True)
        for needle in ("ricerca di dominio", "casi limite", "avversaria"):
            check(f"il verdetto autonomo cita «{needle}»", needle in md, True)
        check("la ricerca deve derivare anche i testi",
              "si derivano anche i testi" in md, True)
        for needle in ("lorem ipsum", "deliverable è **finito**", "all'owner in chat"):
            check(f"il verdetto sul copy cita «{needle}»", needle in md, True)
        check("il verdetto autonomo impone l'avviso preventivo",
              "AVVISA PRIMA DI PARTIRE" in md, True)
        check("progetto nudo: canone di sviluppo imposto",
              "CANONE DI SVILUPPO OBBLIGATORIO" in md, True)
        for needle in ("SOLID", "SoC", "KISS", "DRY", "OWASP", "vertical slices"):
            check(f"il canone cita «{needle}»", needle in md, True)

    # --- partial coverage: binding, but the gaps must be announced ----------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=True)
        (root / "_bmad-output/planning-artifacts/architecture-app.md").unlink()
        (root / "_bmad-output/planning-artifacts/ux-spec-home.md").unlink()
        d = mod.discover(root)
        check("copertura parziale: resta vincolante", d["binding"], True)
        md = mod.render_md(d)
        check("copertura parziale: avvisa sui buchi", "AVVISA SU CIÒ CHE MANCA" in md, True)
        check("l'avviso nomina l'architettura mancante", "architettura" in md.split("AVVISA")[1], True)
        check("l'avviso non nomina il PRD, che c'è", "PRD (perimetro)" in md, False)
        check("architettura assente ma CLAUDE.md presente: nessun canone imposto",
              "CANONE DI SVILUPPO" in md, False)

    # --- no architecture and no project context: the canon is law ----------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=True)
        (root / "_bmad-output/planning-artifacts/architecture-app.md").unlink()
        (root / "CLAUDE.md").unlink()
        d = mod.discover(root)
        check("PRD ancora vincolante", d["binding"], True)
        md = mod.render_md(d)
        check("niente architettura né context: canone imposto anche col PRD",
              "CANONE DI SVILUPPO OBBLIGATORIO" in md, True)
        for needle in ("SOLID", "OWASP", "vertical slices"):
            check(f"il canone (con PRD) cita «{needle}»", needle in md, True)

    # --- clarifying docs: read before guessing the stack --------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=False)
        (root / "docs").mkdir()
        (root / "docs" / "tech-stack.md").write_text("# Stack\nLaravel 11 + Blade\n", encoding="utf-8")
        (root / "docs" / "note-sparse.md").write_text("appunti\n", encoding="utf-8")
        (root / "README.md").write_text("# Progetto\n", encoding="utf-8")
        d = mod.discover(root)
        names = [e["path"] for e in d["clarifying_docs"]]
        check("docs/ scoperto", "docs/tech-stack.md" in names, True)
        check("README incluso", "README.md" in names, True)
        check("i nomi che promettono stack vengono per primi",
              names[0] in ("README.md", "docs/tech-stack.md"), True)
        (root / "docs" / "varianze").mkdir()
        (root / "docs" / "varianze" / "2026-07-26-stack-statico.md").write_text(
            "# Varianza\n- Atteso: Next\n- Deciso: HTML statico\n", encoding="utf-8")
        d2 = mod.discover(root)
        n2 = [e["path"] for e in d2["clarifying_docs"]]
        check("le varianze sono elencate per prime",
              n2.index("docs/varianze/2026-07-26-stack-statico.md") < n2.index("docs/note-sparse.md"), True)
        check("tech-stack prima delle note sparse",
              names.index("docs/tech-stack.md") < names.index("docs/note-sparse.md"), True)
        md = mod.render_md(d)
        check("il report elenca i chiarificatori", "Documenti chiarificatori" in md, True)
        check("il verdetto dice dove vanno scritte le indicazioni",
              "CLAUDE.md" in md and "PRIMA DI DEDURRE" in md, True)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=False)
        (root / "CLAUDE.md").write_text("stack: Astro\n", encoding="utf-8")
        d = mod.discover(root)
        check("CLAUDE.md resta project context, non chiarificatore",
              [e["path"] for e in d["project_context"]], ["CLAUDE.md"])
        check("nessun chiarificatore inventato se docs/ non esiste",
              d["clarifying_docs"], [])

    # --- custom paths from _bmad/config.toml are honoured -------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=True, custom_paths=True)
        d = mod.discover(root)
        check("config.toml: path custom rispettati", d["planning_dir"], "plans")
        check("con path custom trova comunque il PRD", len(d["prd"]), 1)

    # --- robustness ---------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "package.json").write_text("{corrotto", encoding="utf-8")
        d = mod.discover(root)  # must not raise
        check("package.json corrotto non crasha", "node" in d["repo_stack_signals"], True)
        # architecture without a recognisable stack heading → declared, not faked
        planning = root / "_bmad-output" / "planning-artifacts"
        planning.mkdir(parents=True)
        (planning / "architecture-x.md").write_text("# Doc\n\n## Sezione\ntesto\n",
                                                    encoding="utf-8")
        d = mod.discover(root)
        check("stack non riconosciuto → None, non inventato", d["stack_section"], None)
        check("il report dichiara l'estrazione fallita",
              "nessuna sezione stack riconosciuta" in mod.render_md(d), True)

    # --- sharded BMAD v6 layout: folders carry the keyword, files do not ----
    # On basename matching, prd/epic-1.md + architecture/tech-stack.md gave
    # the "no binding documents" verdict — the exact opposite of the truth.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        planning = root / "_bmad-output" / "planning-artifacts"
        (planning / "prd").mkdir(parents=True)
        (planning / "prd" / "epic-1.md").write_text("# Epic 1\n", encoding="utf-8")
        (planning / "architecture").mkdir()
        (planning / "architecture" / "tech-stack.md").write_text(
            "## Stack\n- Astro\n", encoding="utf-8")
        d = mod.discover(root)
        check("PRD shardato in cartella riconosciuto", len(d["prd"]), 1)
        check("architettura shardata riconosciuta", len(d["architecture"]), 1)
        check("layout shardato → vincoli attivi", d["binding"], True)
        check("stack estratto dal file shardato", "Astro" in (d["stack_section"] or ""), True)

    # A stack section organised in subsections must include them, and stop at
    # the next same-level heading.
    text = ("# A\n\n## Tech stack\n\n### Frontend\n- Next.js 15\n\n"
            "### Backend\n- Supabase\n\n## Regole\n- x\n")
    got = mod.extract_section(text, mod.STACK_HEADING) or ""
    check("le sottosezioni dello stack sono incluse", "Supabase" in got, True)
    check("la sezione successiva di pari livello è esclusa", "Regole" in got, False)
    check("il solo heading nudo non conta come estrazione",
          mod.extract_section("## Tech stack\n## Altro\n", mod.STACK_HEADING), None)

    # Absolute config paths without {project-root} are meant as-is.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "_bmad").mkdir()
        (root / "_bmad" / "config.toml").write_text(
            'planning_artifacts = "/var/shared/plans"\n', encoding="utf-8")
        p, _i = mod.read_config_paths(root)
        check("path assoluto in config non ri-radicato nel progetto",
              str(p), "/var/shared/plans")

    # --- il nome non basta: `ux` dentro `luxury` (review 2026-07-26) --------
    # `register: luxury` è un asse dello skill: file con "luxury" nel nome sono
    # l'esito normale della ricerca di dominio. Classificarli come page spec
    # vincolante saltava l'avviso di apertura e la stesura dei sei documenti.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=False)
        planning = root / "_bmad-output" / "planning-artifacts"
        (planning / "ricerca-hotel-luxury.md").write_text(
            "# Ricerca di dominio — hotel luxury\nappunti\n", encoding="utf-8")
        (planning / "note-deluxe.md").write_text("# Note\n", encoding="utf-8")
        d = mod.discover(root)
        check("«luxury» non è una page spec", d["ux_specs"], [])
        check("«deluxe» non è una page spec", len(d["ux_specs"]), 0)
        check("ricerca di dominio non rende il progetto vincolato", d["binding"], False)
        check("i file non classificati restano elencati", len(d["planning_other"]), 2)
        check("verdetto: i sei documenti si scrivono",
              "NESSUN DOCUMENTO VINCOLANTE" in mod.render_md(d), True)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_project(root, with_docs=False)
        planning = root / "_bmad-output" / "planning-artifacts"
        for name in ("ux-home.md", "UX_flows.md", "wireframe-menu.md", "page-spec-home.md"):
            (planning / name).write_text("# Spec\n", encoding="utf-8")
        (planning / "prd-v2.md").write_text("# PRD\n", encoding="utf-8")
        d = mod.discover(root)
        check("le vere page spec restano riconosciute", len(d["ux_specs"]), 4)
        check("il PRD resta riconosciuto", len(d["prd"]), 1)

    r = run("/nonexistent-path-xyz")
    check("root inesistente rifiutata", r.returncode != 0, True)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
