#!/usr/bin/env python3
"""Run the same checks as .github/workflows/ci.yml."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "verify_modern_addon_layout.py",
    "verify_consent_e2e.py",
    "verify_manifest_polish.py",
    "verify_gui_polish.py",
    "verify_robustness.py",
    "verify_icon_manifest.py",
    "verify_freecad_compat.py",
    "verify_security_md.py",
]


def main() -> int:
    for name in SCRIPTS:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name)],
            cwd=str(ROOT),
        )
        if proc.returncode != 0:
            print("FAIL:", name)
            return proc.returncode
    for cmd in (
        [sys.executable, "-m", "pytest", "-q"],
        [sys.executable, "-m", "ruff", "check", "freecad/", "tests/"],
        [sys.executable, "-m", "bandit", "-r", "freecad/", "-q", "-c", "bandit.yaml"],
    ):
        proc = subprocess.run(cmd, cwd=str(ROOT))
        if proc.returncode != 0:
            print("FAIL:", " ".join(cmd))
            return proc.returncode
    print("PASS ci local")
    return 0


if __name__ == "__main__":
    sys.exit(main())