#!/usr/bin/env python3
"""Verify addon icon files and manifest wiring (no FreeCAD required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "freecad/stl2cad/resources/icons/stl2cad.svg"
INIT = ROOT / "freecad/stl2cad/init_gui.py"
MANIFEST = ROOT / "package.xml"


def main() -> int:
    errors: list[str] = []
    if not ICON.is_file():
        errors.append("missing stl2cad.svg")
    else:
        data = ICON.read_text(encoding="utf-8")
        if "viewBox" not in data:
            errors.append("icon missing viewBox")
        if "0 0 64 64" not in data:
            errors.append("icon should use 64x64 viewBox")

    manifest = MANIFEST.read_text(encoding="utf-8")
    if "<icon>freecad/stl2cad/resources/icons/stl2cad.svg</icon>" not in manifest:
        errors.append("package.xml missing icon element")

    init = INIT.read_text(encoding="utf-8")
    if "Icon = " not in init or "resources" not in init:
        errors.append("init_gui.py missing Icon path")
    if "addIconPath" not in init:
        errors.append("init_gui.py missing addIconPath")

    if errors:
        print("FAIL")
        for line in errors:
            print(" -", line)
        return 1
    print("PASS icon manifest and init_gui wiring")
    return 0


if __name__ == "__main__":
    sys.exit(main())