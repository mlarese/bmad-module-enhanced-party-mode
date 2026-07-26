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

        # With sanctum + --pulse → PULSE mode
        sanctum = root / "_bmad" / "memory" / "agent-world-cpa"
        sanctum.mkdir(parents=True)
        for name in ("INDEX.md", "PERSONA.md", "CREED.md", "BOND.md", "MEMORY.md", "CAPABILITIES.md", "PULSE.md"):
            (sanctum / name).write_text(f"# {name}\n", encoding="utf-8")

        r = subprocess.run(
            [sys.executable, str(WAKE), str(root), "--pulse"],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0 or "MODE: PULSE" not in r.stdout or "PULSE.md" not in r.stdout:
            print("FAIL: pulse mode", r.returncode, r.stdout)
            fails += 1
        else:
            print("PASS: PULSE mode with sanctum")

        r = subprocess.run([sys.executable, str(WAKE), str(root)], capture_output=True, text=True)
        if r.returncode != 0 or "MODE: WAKING" not in r.stdout:
            print("FAIL: waking", r.returncode, r.stdout)
            fails += 1
        else:
            print("PASS: WAKING mode")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
