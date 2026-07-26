# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for council_roster.py — run: uv run scripts/tests/test-council-roster.py

The rule under test: every agent skill installed in the project sits on the
council by right. It used to be a hand-kept list in three files, and the three
had already drifted — the party carried 13 members while the references named
11, so the PM and the dev were in the room and in nobody's roster.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "council_roster.py"

PARTY = """[workflow]
default_party = "super-esperti"

[[workflow.party_members]]
code = "vesper"
name = "Vesper"

[[workflow.party_members]]
code = "vera"
name = "Vera Motion"

[[workflow.party_members]]
code = "jane-privacy"
name = "Jane Privacy"

[[workflow.party_groups]]
id = "super-esperti"
members = ["vesper", "vera", "jane-privacy", "bmad-agent-pm", "bmad-tea"]
"""


def load():
    spec = importlib.util.spec_from_file_location("council_roster", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["council_roster"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def agent(root: Path, folder: str, description: str, where: str = "skills") -> None:
    d = root / where / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {folder}\ndescription: {description}\n---\n",
                                encoding="utf-8")


def main() -> int:
    fails = 0
    mod = load()

    def check(label, got, want=True):
        nonlocal fails
        if got == want:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}\n  atteso: {want}\n  ottenuto: {got}")
            fails += 1

    # --- il nome della persona si legge dalla description --------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        agent(root, "agent-gdpr-counsel", "Jane Privacy (GDPR/privacy counsel IT/UE). Trigger on Jane.")
        agent(root, "agent-web-animations", "Vera Motion (web animations craft). Trigger on Vera.")
        agent(root, "agent-frontend-taste", "Vesper — craft FE. Zero domande all'owner.")
        names = {a["skill"]: a["name"] for a in mod.installed_agents(root)}
        check("nome dal formato «Nome (dominio)»", names["agent-gdpr-counsel"], "Jane Privacy")
        check("nome dal formato «Nome — descrizione»", names["agent-frontend-taste"], "Vesper")
        check("tutti gli agent-* installati sono trovati", len(names), 3)

    # --- roster completo -----------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "_bmad" / "custom").mkdir(parents=True)
        (root / "_bmad" / "custom" / "bmad-party-mode.toml").write_text(PARTY, encoding="utf-8")
        agent(root, "agent-frontend-taste", "Vesper — craft FE.")
        agent(root, "agent-web-animations", "Vera Motion (web animations craft).")
        agent(root, "agent-gdpr-counsel", "Jane Privacy (GDPR/privacy counsel IT/UE).")
        d = mod.build(root)
        check("roster completo quando tutti sono nel gruppo", d["complete"])
        check("ogni agente installato è seduto", all(a["seated"] for a in d["agents"]))
        check("il ruolo BMAD presente nel gruppo è marcato seduto",
              [r["seated"] for r in d["bmad_roles"] if r["skill"] == "bmad-agent-pm"], [True])
        check("il ruolo BMAD assente è marcato mancante",
              [r["seated"] for r in d["bmad_roles"] if r["skill"] == "bmad-agent-architect"], [False])
        r = run(str(root))
        check("CLI: exit 0 su roster completo", r.returncode, 0)
        check("CLI: lo dice", "Roster completo" in r.stdout)

    # --- un agente nuovo installato e non aggiunto al party ------------------
    # Il caso che la lista a mano non può intercettare: nessuno se ne accorge,
    # perché una voce che manca non dà errore — semplicemente non parla mai.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "_bmad" / "custom").mkdir(parents=True)
        (root / "_bmad" / "custom" / "bmad-party-mode.toml").write_text(PARTY, encoding="utf-8")
        agent(root, "agent-frontend-taste", "Vesper — craft FE.")
        agent(root, "agent-security-research", "Kim Ferro (security research). Trigger on Kim.")
        d = mod.build(root)
        check("roster incompleto rilevato", d["complete"], False)
        check("l'agente fuori dal gruppo è nominato",
              [a["name"] for a in d["missing_from_group"]], ["Kim Ferro"])
        r = run(str(root))
        check("CLI: exit 1 quando qualcuno è fuori", r.returncode, 1)
        check("CLI: non autorizza a decidere senza di lui",
              "si convocano **per nome**" in r.stdout)
        rj = run(str(root), "--format", "json")
        check("CLI json valido", json.loads(rj.stdout)["complete"], False)

    # --- copie installate: stesso agente in due alberi, contato una volta ----
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "_bmad" / "custom").mkdir(parents=True)
        (root / "_bmad" / "custom" / "bmad-party-mode.toml").write_text(PARTY, encoding="utf-8")
        agent(root, "agent-web-animations", "Vera Motion (web animations craft).")
        agent(root, "agent-web-animations", "Vera Motion (web animations craft).",
              where=".claude/skills")
        d = mod.build(root)
        check("lo stesso agente in due alberi conta una volta", len(d["agents"]), 1)
        check("la sorgente vince sulla copia installata",
              d["agents"][0]["where"].startswith("skills/"))

    # --- modulo appena installato: nessun party configurato ------------------
    # Il caso normale in un progetto che installa epm. Non è un difetto: senza
    # `default_party`, party-mode convoca già tutto il collettivo installato.
    # Segnalarlo come roster incompleto renderebbe il gate rosso per sempre, e
    # un gate sempre rosso non viene più letto.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        agent(root, "agent-gdpr-counsel", "Jane Privacy (GDPR/privacy counsel IT/UE).",
              where=".claude/skills")
        agent(root, "agent-frontend-taste", "Vesper — craft FE.", where=".claude/skills")
        d = mod.build(root)
        check("gli agenti installati sotto .claude/skills sono trovati", len(d["agents"]), 2)
        check("senza gruppo il roster è comunque completo", d["complete"], True)
        check("senza gruppo tutti sono al tavolo (collettivo)",
              all(a["seated"] for a in d["agents"]))
        check("senza gruppo si convoca SENZA --party",
              d["convocazione"], "bmad-party-mode --non-interactive")
        r = run(str(root))
        check("CLI: exit 0 su modulo installato senza party", r.returncode, 0)
        check("CLI: avverte che un id sconosciuto apre un menu",
              "chiedendo quale usare" in r.stdout)

    # Con il gruppo configurato la convocazione lo nomina.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "_bmad" / "custom").mkdir(parents=True)
        (root / "_bmad" / "custom" / "bmad-party-mode.toml").write_text(PARTY, encoding="utf-8")
        agent(root, "agent-frontend-taste", "Vesper — craft FE.")
        d = mod.build(root)
        check("con gruppo configurato si convoca con --party",
              d["convocazione"], "bmad-party-mode --non-interactive --party super-esperti")

    # Il gruppo che --emit-party scrive nomina gli agenti col loro codice
    # installato, senza personas custom: deve risultare completo. Trovato
    # installandolo davvero in un progetto — usciva 1 dicendo che non sedeva
    # nessuno, cioè lo script bocciava il file che aveva generato lui.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        agent(root, "agent-frontend-taste", "Vesper — craft FE.", where=".claude/skills")
        agent(root, "agent-world-cpa", "Dan Arrow — Commercialista Mondiale (fiscale).",
              where=".claude/skills")
        (root / "_bmad" / "custom").mkdir(parents=True)
        (root / "_bmad" / "custom" / "bmad-party-mode.toml").write_text(
            mod.emit_party(root), encoding="utf-8")
        d = mod.build(root)
        check("il gruppo generato da --emit-party è completo", d["complete"], True)
        check("ogni agente è seduto col proprio codice",
              sorted(a["party_code"] for a in d["agents"]),
              ["agent-frontend-taste", "agent-world-cpa"])
        check("con il gruppo si convoca con --party",
              d["convocazione"], "bmad-party-mode --non-interactive --party super-esperti")
        check("CLI: exit 0 sul gruppo appena generato", run(str(root)).returncode, 0)

    # Il gruppo non può sedere meno gente del non averlo: senza gruppo
    # party-mode convoca TUTTI gli agenti registrati dal progetto. Misurato su
    # un progetto vero: default 14, gruppo generato 13 — il tech writer usciva
    # dal tavolo senza che nessuno lo dicesse.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        agent(root, "agent-frontend-taste", "Vesper — craft FE.", where=".claude/skills")
        (root / "_bmad").mkdir(parents=True)
        (root / "_bmad" / "config.toml").write_text(
            "[agents.agent-frontend-taste]\nmodule = \"epm\"\n\n"
            "[agents.bmad-agent-tech-writer]\nmodule = \"bmm\"\n\n"
            "[agents.bmad-agent-pm]\nmodule = \"bmm\"\n", encoding="utf-8")
        check("gli agenti registrati dal progetto sono letti",
              mod.registered_agents(root),
              ["agent-frontend-taste", "bmad-agent-tech-writer", "bmad-agent-pm"])
        toml = mod.emit_party(root)
        check("il gruppo generato non esclude nessun agente registrato",
              [a for a in mod.registered_agents(root) if f'"{a}"' not in toml], [])

    # --emit-party genera un gruppo installabile che contiene tutti.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        agent(root, "agent-frontend-taste", "Vesper — craft FE.", where=".claude/skills")
        agent(root, "agent-world-cpa", "Dan Arrow — Commercialista Mondiale (fiscale).",
              where=".claude/skills")
        toml = mod.emit_party(root)
        check("--emit-party include ogni agente installato",
              '"agent-world-cpa"' in toml and '"agent-frontend-taste"' in toml)
        check("--emit-party include i ruoli BMAD", '"bmad-agent-pm"' in toml)
        check("--emit-party dichiara il gruppo giusto", 'id = "super-esperti"' in toml)
        r = run(str(root), "--emit-party")
        check("CLI --emit-party esce 0", r.returncode, 0)

    # --- una directory senza SKILL.md non è un agente ------------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "skills" / "agent-bozza").mkdir(parents=True)
        check("cartella senza SKILL.md ignorata", mod.installed_agents(root), [])

    check("root inesistente rifiutata", run("/nonexistent-xyz").returncode != 0)

    print()
    print("tutti i test passati" if not fails else f"{fails} test falliti")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
