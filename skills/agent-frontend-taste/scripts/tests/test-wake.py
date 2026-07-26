# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for wake.py — run: uv run scripts/tests/test-wake.py"""
import subprocess
import sys
import tempfile
from pathlib import Path

WAKE = Path(__file__).resolve().parents[1] / "wake.py"


def main() -> int:
    fails = 0

    r = subprocess.run([sys.executable, str(WAKE)], capture_output=True, text=True)
    if r.returncode != 2:
        print("FAIL: expected exit 2 without args, got", r.returncode)
        fails += 1
    else:
        print("PASS: usage exit 2")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "_bmad").mkdir()
        r = subprocess.run([sys.executable, str(WAKE), str(root)], capture_output=True, text=True)
        if r.returncode != 0 or "MODE: FIRST_BREATH" not in r.stdout:
            print("FAIL: first breath", r.returncode, r.stdout, r.stderr)
            fails += 1
        else:
            print("PASS: FIRST_BREATH without sanctum")

        r = subprocess.run(
            [sys.executable, str(WAKE), str(root), "--pulse"],
            capture_output=True,
            text=True,
        )
        if "MODE: PULSE" in r.stdout:
            print("FAIL: --pulse still emits MODE: PULSE")
            fails += 1
        elif "NOTE: --pulse ignored" not in r.stderr:
            print("FAIL: expected --pulse ignore note on stderr")
            fails += 1
        else:
            print("PASS: --pulse ignored (no Pulse mode)")

        sanctum = root / "_bmad" / "memory" / "agent-frontend-taste"
        sanctum.mkdir(parents=True)
        (sanctum / "CREED.md").write_text("# Creed\n")
        (sanctum / "MEMORY.md").write_text("# Memory\n")
        r = subprocess.run([sys.executable, str(WAKE), str(root)], capture_output=True, text=True)
        if "MODE: WAKING" not in r.stdout or "PARTIAL_SANCTUM" not in r.stdout:
            print("FAIL: partial sanctum", r.stdout)
            fails += 1
        else:
            print("PASS: PARTIAL_SANCTUM when identity files missing")

    # A mistyped root used to resolve happily and answer FIRST_BREATH: the
    # agent was "born again" with an empty MEMORY while its real sanctum sat
    # untouched somewhere else. A path that does not exist is an error.
    r = subprocess.run([sys.executable, str(WAKE), "/tmp/vesper-non-esiste-xyz"],
                       capture_output=True, text=True)
    if r.returncode == 0 or "FIRST_BREATH" in r.stdout:
        print("FAIL: project-root inesistente trattato come nascita", r.stdout)
        fails += 1
    else:
        print("PASS: project-root inesistente rifiutato, non è una nascita")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
