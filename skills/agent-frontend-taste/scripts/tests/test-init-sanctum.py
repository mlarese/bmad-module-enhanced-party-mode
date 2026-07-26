# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for init-sanctum.py — run: uv run scripts/tests/test-init-sanctum.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

INIT = Path(__file__).resolve().parents[1] / "init-sanctum.py"
SKILL = Path(__file__).resolve().parents[2]


def main() -> int:
    fails = 0
    r = subprocess.run([sys.executable, str(INIT)], capture_output=True, text=True)
    if r.returncode == 0:
        print("FAIL: expected non-zero without args")
        fails += 1
    else:
        print("PASS: usage without args")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bmad = root / "_bmad"
        bmad.mkdir()
        (bmad / "config.yaml").write_text(
            "user_name: Test\ncommunication_language: Italiano\n"
        )
        r = subprocess.run(
            [sys.executable, str(INIT), str(root), str(SKILL)],
            capture_output=True,
            text=True,
        )
        sanctum = root / "_bmad" / "memory" / "agent-frontend-taste"
        if r.returncode != 0 or not (sanctum / "PERSONA.md").is_file():
            print("FAIL: init", r.returncode, r.stdout, r.stderr)
            fails += 1
        else:
            caps = (sanctum / "CAPABILITIES.md").read_text()
            persona = (sanctum / "PERSONA.md").read_text()
            for code in ("DX", "AW", "AF", "UE"):
                if f"[{code}]" not in caps:
                    print("FAIL: missing cap", code)
                    fails += 1
                    break
            else:
                print("PASS: init scaffolds sanctum with DX/AW/AF/UE")
            if "Load the Source file before answering" not in caps:
                print("FAIL: missing load-on-invoke line in CAPABILITIES")
                fails += 1
            else:
                print("PASS: load-on-invoke line present")
            if "Vesper" not in persona:
                print("FAIL: PERSONA missing Vesper")
                fails += 1
            else:
                print("PASS: PERSONA seeded Vesper")
            r2 = subprocess.run(
                [sys.executable, str(INIT), str(root), str(SKILL)],
                capture_output=True,
                text=True,
            )
            if "already" not in r2.stdout.lower() and "Skipping" not in r2.stdout:
                print("FAIL: idempotent", r2.returncode, r2.stdout)
                fails += 1
            else:
                print("PASS: idempotent skip")

            # --- refresh: materials re-sync, identity untouched ------------
            def check(label, got, want=True):
                nonlocal fails
                if got == want:
                    print(f"PASS: {label}")
                else:
                    print(f"FAIL: {label} (atteso {want}, ottenuto {got})")
                    fails += 1

            # The sanctum drifts: a reference is edited, another deleted, and
            # the identity files carry the agent's own history.
            (sanctum / "references" / "craft-rules.md").write_text("VECCHIO\n")
            (sanctum / "references" / "craft-marketing.md").unlink(missing_ok=True)
            for name in ("PERSONA.md", "CREED.md", "BOND.md", "MEMORY.md", "INDEX.md", "CAPABILITIES.md"):
                (sanctum / name).write_text(f"IDENTITÀ {name} — non toccare\n")
            (sanctum / "capabilities" / "learned.md").write_text("appresa\n")
            (sanctum / "sessions" / "2026-01-01.md").write_text("log\n")

            r3 = subprocess.run(
                [sys.executable, str(INIT), str(root), str(SKILL), "--refresh"],
                capture_output=True, text=True,
            )
            check("refresh esce 0", r3.returncode, 0)
            check("il reference modificato è risincronizzato",
                  (sanctum / "references" / "craft-rules.md").read_text() != "VECCHIO\n")
            check("il reference mancante è ricomparso",
                  (sanctum / "references" / "craft-marketing.md").is_file())
            check("first-breath.md resta fuori dal sanctum",
                  (sanctum / "references" / "first-breath.md").exists(), False)
            for name in ("PERSONA.md", "CREED.md", "BOND.md", "MEMORY.md", "INDEX.md", "CAPABILITIES.md"):
                check(f"identità intatta: {name}",
                      (sanctum / name).read_text(), f"IDENTITÀ {name} — non toccare\n")
            check("capability apprese intatte",
                  (sanctum / "capabilities" / "learned.md").read_text(), "appresa\n")
            check("session log intatto",
                  (sanctum / "sessions" / "2026-01-01.md").read_text(), "log\n")
            check("i template di nascita non finiscono negli asset",
                  (sanctum / "assets" / "MEMORY-template.md").exists(), False)
            check("gli asset di runtime sono sincronizzati",
                  (sanctum / "assets" / "hero-catalog.json").is_file())

            # --- refresh rifiuta una sorgente che non è questa skill --------
            wrong = root / "altra-skill"
            (wrong / "references").mkdir(parents=True)
            (wrong / "SKILL.md").write_text("---\nname: altra-skill\n---\n")
            (wrong / "references" / "x.md").write_text("roba di un'altra skill\n")
            r4 = subprocess.run(
                [sys.executable, str(INIT), str(root), str(wrong), "--refresh"],
                capture_output=True, text=True,
            )
            check("refresh da un'altra skill è rifiutato", r4.returncode != 0)
            check("il sanctum non è stato contaminato",
                  (sanctum / "references" / "x.md").exists(), False)
            r5 = subprocess.run(
                [sys.executable, str(INIT), str(root), str(root / "vuoto"), "--refresh"],
                capture_output=True, text=True,
            )
            check("refresh da una directory inesistente è rifiutato", r5.returncode != 0)

    # --- refresh senza sanctum: non crea nulla di nascosto ------------------
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        r6 = subprocess.run(
            [sys.executable, str(INIT), str(root), str(SKILL), "--refresh"],
            capture_output=True, text=True,
        )
        if r6.returncode == 0 or (root / "_bmad" / "memory" / "agent-frontend-taste").exists():
            print("FAIL: refresh senza sanctum dovrebbe fallire senza creare nulla")
            fails += 1
        else:
            print("PASS: refresh senza sanctum rifiutato")

    # --- project-root inesistente: mai una seconda nascita ------------------
    # `mkdir(parents=True)` costruiva l'intero sanctum dentro una directory che
    # un istante prima non esisteva: identità nuova, MEMORY vuota, e nessun
    # segnale. Creare il project root non è compito di questo script.
    with tempfile.TemporaryDirectory() as td:
        ghost = Path(td) / "progetto-mai-esistito"
        r7 = subprocess.run(
            [sys.executable, str(INIT), str(ghost), str(SKILL)],
            capture_output=True, text=True,
        )
        if r7.returncode == 0 or ghost.exists():
            print("FAIL: root inesistente ha prodotto un sanctum fantasma")
            fails += 1
        else:
            print("PASS: project-root inesistente rifiutato, nessun sanctum fantasma")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
