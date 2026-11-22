#!/usr/bin/env python3
"""Manifest and neutral copy checks (#5, #14–#16)."""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "package.xml"
NS = {"m": "https://wiki.freecad.org/Package_Metadata"}


def main() -> int:
    errors: list[str] = []
    text = MANIFEST.read_text(encoding="utf-8")
    if "<subdirectory>" in text:
        errors.append("subdirectory element must be removed")
    if "raw.githubusercontent.com" not in text:
        errors.append("readme url must be raw GitHub")
    for token in ("GAID", "RAG Box sponsors", "was used to build"):
        if token in text:
            errors.append("package description still has marketing: %s" % token)

    tree = ET.parse(MANIFEST)
    root = tree.getroot()
    for tag in ("author", "pythonmin"):
        if root.find("m:%s" % tag, NS) is None and root.find(tag) is None:
            errors.append("missing <%s>" % tag)
    tags = root.findall("m:tag", NS) or root.findall("tag")
    if len(tags) < 3:
        errors.append("expected at least 3 package tags")

    init = (ROOT / "freecad/stl2cad/init_gui.py").read_text(encoding="utf-8")
    if "RAG" in init or "GAID" in init:
        errors.append("init_gui marketing text")

    panel = (ROOT / "freecad/stl2cad/panel.py").read_text(encoding="utf-8")
    if "GAID" in panel or "RAG Box sponsors" in panel:
        errors.append("panel marketing blocks")

    if (ROOT / "freecad/stl2cad/init.py").exists():
        errors.append("init.py should be removed")

    if errors:
        print("FAIL")
        for line in errors:
            print(" -", line)
        return 1
    print("PASS manifest polish")
    return 0


if __name__ == "__main__":
    sys.exit(main())