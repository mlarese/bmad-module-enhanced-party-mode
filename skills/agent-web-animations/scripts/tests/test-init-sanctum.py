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
        sanctum = root / "_bmad" / "memory" / "agent-web-animations"
        if r.returncode != 0 or not (sanctum / "PERSONA.md").is_file():
            print("FAIL: init", r.returncode, r.stdout, r.stderr)
            fails += 1
        else:
            caps = (sanctum / "CAPABILITIES.md").read_text()
            persona = (sanctum / "PERSONA.md").read_text()
            for code in ("AP", "CT", "DM", "RE", "AU"):
                if f"[{code}]" not in caps:
                    print("FAIL: missing cap", code)
                    fails += 1
                    break
            else:
                print("PASS: init scaffolds sanctum with 5 caps")
            if "Load the Source file before answering" not in caps:
                print("FAIL: missing load-on-invoke line in CAPABILITIES")
                fails += 1
            else:
                print("PASS: load-on-invoke line present")
            if "Vera Motion" not in persona:
                print("FAIL: PERSONA missing Vera Motion")
                fails += 1
            else:
                print("PASS: PERSONA seeded Vera Motion")
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

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
