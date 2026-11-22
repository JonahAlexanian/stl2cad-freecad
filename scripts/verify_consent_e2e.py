#!/usr/bin/env python3
"""Static checks for in-app consent (no FreeCAD runtime required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []

    client = (ROOT / "freecad/stl2cad/client.py").read_text(encoding="utf-8")
    if "_ensure_service_consent" not in client:
        errors.append("client.py: missing _ensure_service_consent")
    if "_service_url" not in client or "_ensure_service_consent()" not in client:
        errors.append("client.py: _request must guard service URLs")

    panel = (ROOT / "freecad/stl2cad/panel.py").read_text(encoding="utf-8")
    if "consent.ensure_consent()" not in panel:
        errors.append("panel.py: missing ensure_consent before network actions")

    consent_py = ROOT / "freecad/stl2cad/consent.py"
    if not consent_py.is_file():
        errors.append("consent.py: missing")
    else:
        text = consent_py.read_text(encoding="utf-8")
        for token in ("CONSENT_SCOPE", "revoke_consent", "ensure_consent"):
            if token not in text:
                errors.append("consent.py: missing %s" % token)

    prefs = ROOT / "freecad/stl2cad/preferences.py"
    if not prefs.is_file():
        errors.append("preferences.py: missing")

    init = (ROOT / "freecad/stl2cad/init_gui.py").read_text(encoding="utf-8")
    if "preferences.register" not in init:
        errors.append("init_gui.py: preferences not registered")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "## Privacy and external services" not in readme:
        errors.append("README.md: missing privacy table section")

    sys.path.insert(0, str(ROOT))
    try:
        from freecad.stl2cad import client as client_mod
        from freecad.stl2cad import consent as consent_mod

        consent_mod._test_override = False
        try:
            client_mod._ensure_service_consent()
            errors.append("client should raise when consent is denied")
        except RuntimeError:
            pass
        consent_mod._test_override = True
        client_mod._ensure_service_consent()
        consent_mod._test_override = None
    except Exception as exc:
        errors.append("runtime consent guard check failed: %s" % exc)

    if errors:
        print("FAIL")
        for line in errors:
            print(" -", line)
        return 1

    print("PASS consent guards and docs present")
    return 0


if __name__ == "__main__":
    sys.exit(main())