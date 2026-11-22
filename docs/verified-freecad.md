# Verified FreeCAD versions

`package.xml` sets `<freecadmin>1.0.0</freecadmin>` as the **minimum** version we target. We do **not** claim every newer release is tested unless listed here.

## Tested configurations

| FreeCAD | OS | Date | Verified by | Checks |
|---------|-----|------|-------------|--------|
| **1.0** (owner build) | Windows | 2026-11-22 | Maintainer (owner) | Modern workbench layout; icon; panel **Load STL** + **Convert**; consent dialog (No/Yes); consent remembered across restart; **Save STEP** path used earlier in session |

Install method for tests: `scp` from dev host into `%APPDATA%\FreeCAD\Mod\stl2cad-freecad` (see `HANDOFF_2026-11-22.md`).

## Not verified by maintainer (yet)

| Version | Note |
|---------|------|
| FreeCAD **1.1+** | Expected to work with the namespaced layout; no maintainer sign-off on record. |
| **Linux / macOS** | No maintainer smoke test logged for this add-on revision. |

When a version is tested, add a row to the first table and mention it in the release notes.