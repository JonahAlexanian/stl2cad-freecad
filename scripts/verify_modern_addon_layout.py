#!/usr/bin/env python3
"""Layout checks for the modern FreeCAD namespaced add-on."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(1)


def ok(msg: str) -> None:
    print("OK:", msg)


def main() -> None:
    pkg = ROOT / "package.xml"
    text = pkg.read_text()
    if "<subdirectory>" in text:
        fail("package.xml must not use legacy <subdirectory> in modern layout")
    if "Stl2CadWorkbench" not in text:
        fail("package.xml missing Stl2CadWorkbench classname")
    ok("package.xml modern workbench manifest")

    if (ROOT / "freecad" / "__init__.py").exists():
        fail("freecad/__init__.py must not exist (shadows FreeCAD)")
    ok("no freecad/__init__.py")

    for name in ("init_gui.py", "panel.py", "client.py", "__init__.py"):
        path = ROOT / "freecad" / "stl2cad" / name
        if not path.is_file():
            fail("missing freecad/stl2cad/" + name)
    if (ROOT / "freecad" / "stl2cad" / "init.py").is_file():
        fail("freecad/stl2cad/init.py must not exist in modern layout")
    ok("workbench files present")

    init_gui = (ROOT / "freecad" / "stl2cad" / "init_gui.py").read_text()
    if "sys.path" in init_gui or "inspect" in init_gui:
        fail("init_gui.py must not manipulate sys.path")
    if "from . import panel" not in init_gui:
        fail("init_gui.py must use relative import for panel")
    ok("init_gui.py uses namespaced import")

    panel = (ROOT / "freecad" / "stl2cad" / "panel.py").read_text()
    if re.search(r"^import client\b", panel, re.M):
        fail("panel.py must use relative import for client")
    if "from . import client" not in panel:
        fail("panel.py missing from . import client")
    ok("panel.py imports client relatively")

    if (ROOT / "InitGui.py").is_file() or (ROOT / "Init.py").is_file():
        fail("legacy root Init.py / InitGui.py must be removed")
    ok("no legacy root Init files")

    client = (ROOT / "freecad" / "stl2cad" / "client.py").read_text()
    if "https://www.stl2cad.com" not in client:
        fail("client.py must call public converter")
    ok("client.py still targets https://www.stl2cad.com")

    compile((ROOT / "freecad" / "stl2cad" / "panel.py").read_text(), "panel.py", "exec")
    compile(client, "client.py", "exec")
    ok("panel and client compile")

    print("PASS: modern addon layout")
    sys.exit(0)


if __name__ == "__main__":
    main()