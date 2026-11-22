#!/usr/bin/env python3
"""Honest FreeCAD compatibility docs vs package.xml."""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    manifest = ROOT / "package.xml"
    tree = ET.parse(manifest)
    root = tree.getroot()
    ns = {"m": "https://wiki.freecad.org/Package_Metadata"}
    admin = root.find("m:freecadmin", ns)
    if admin is None:
        admin = root.find("freecadmin")
    if admin is None or not (admin.text or "").strip():
        errors.append("package.xml missing freecadmin")
    elif admin.text.strip() != "1.0.0":
        errors.append("unexpected freecadmin: %s" % admin.text)

    verified = ROOT / "docs/verified-freecad.md"
    if not verified.is_file():
        errors.append("missing docs/verified-freecad.md")
    else:
        text = verified.read_text(encoding="utf-8")
        if "2026-11-22" not in text or "1.0" not in text:
            errors.append("verified-freecad.md missing 1.0 test record")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "verified-freecad.md" not in readme:
        errors.append("README must link verified-freecad.md")
    if "1.0 or newer" in readme.lower():
        errors.append('README must not claim blind "1.0 or newer"')

    if errors:
        print("FAIL")
        for line in errors:
            print(" -", line)
        return 1
    print("PASS freecadmin 1.0.0 with documented verification")
    return 0


if __name__ == "__main__":
    sys.exit(main())