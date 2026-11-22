#!/usr/bin/env python3
"""GUI polish checks (#6, #13, #17–#20)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    panel = (ROOT / "freecad/stl2cad/panel.py").read_text(encoding="utf-8")
    if "def _qt(" in panel or "PySide6" in panel or "PySide2" in panel:
        errors.append("panel.py must use PySide shim only")
    if "from PySide import" not in panel:
        errors.append("panel.py missing from PySide import in GUI path")
    if "PySide6" in panel or "PySide2" in panel:
        errors.append("panel.py must not import PySide6/2 directly")
    if '_EVENTS = queue.Queue()' in panel:
        errors.append("panel must not use module-global event queue")
    if 'setObjectName("STL2CAD_Dock")' not in panel:
        errors.append("panel missing dock objectName")
    if "widget_is_valid" not in panel:
        errors.append("panel missing dock validity guard")

    init = (ROOT / "freecad/stl2cad/init_gui.py").read_text(encoding="utf-8")
    if "from . import panel" not in init:
        errors.append("init_gui relative panel import")
    if "STL2CAD_OpenPanel" not in init:
        errors.append("init_gui missing OpenPanel command registration")

    commands = ROOT / "freecad/stl2cad/commands.py"
    if not commands.is_file():
        errors.append("commands.py missing")

    if errors:
        print("FAIL")
        for line in errors:
            print(" -", line)
        return 1
    print("PASS gui polish")
    return 0


if __name__ == "__main__":
    sys.exit(main())