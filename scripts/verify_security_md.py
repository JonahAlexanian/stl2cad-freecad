#!/usr/bin/env python3
"""Check SECURITY.md exists and has required sections."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "SECURITY.md"

REQUIRED = (
    "Supported versions",
    "Reporting a vulnerability",
    "security/advisories",
    "Response expectation",
)


def main() -> int:
    if not SECURITY.is_file():
        print("FAIL: SECURITY.md missing")
        return 1
    text = SECURITY.read_text(encoding="utf-8")
    missing = [bit for bit in REQUIRED if bit not in text]
    if missing:
        print("FAIL: SECURITY.md missing:", ", ".join(missing))
        return 1
    if (ROOT / "ADDON_STATUS.md").is_file():
        print("FAIL: ADDON_STATUS.md still in tree (remove from public repo)")
        return 1
    print("PASS SECURITY.md present; ADDON_STATUS.md not published")
    return 0


if __name__ == "__main__":
    sys.exit(main())