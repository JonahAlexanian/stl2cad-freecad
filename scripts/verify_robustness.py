#!/usr/bin/env python3
"""Robustness checks (#7–#8, #10, #23)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    client = (ROOT / "freecad/stl2cad/client.py").read_text(encoding="utf-8")
    panel = (ROOT / "freecad/stl2cad/panel.py").read_text(encoding="utf-8")

    if "_safe_step_preview" not in panel:
        errors.append("panel missing best-effort preview helper")
    if "mkdtemp(prefix=\"stl2cad_\"" not in panel:
        errors.append("panel should use private mkdtemp for uploads")
    if "_read_binary_stl" not in client or "_sanitize_upload_filename" not in client:
        errors.append("client missing binary/sanitize helpers")
    if "84 + count * 50 == len(data)" in client:
        errors.append("client still requires exact STL byte length")

    test_file = ROOT / "tests/test_read_stl.py"
    if not test_file.is_file():
        errors.append("missing tests/test_read_stl.py")
    elif subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(test_file)],
        cwd=str(ROOT),
    ).returncode:
        errors.append("read_stl pytest failed")

    if errors:
        print("FAIL")
        for line in errors:
            print(" -", line)
        return 1
    print("PASS robustness")
    return 0


if __name__ == "__main__":
    sys.exit(main())