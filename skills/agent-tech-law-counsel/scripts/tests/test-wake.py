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

        # Legacy --pulse must not invent a Pulse mode on this memory-only agent
        r = subprocess.run(
            [sys.executable, str(WAKE), str(root), "--pulse"],
            capture_output=True,
            text=True,
        )
        if "MODE: PULSE" in r.stdout:
            print("FAIL: --pulse still emits MODE: PULSE")
            fails += 1
        else:
            print("PASS: --pulse ignored (no Pulse mode)")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
