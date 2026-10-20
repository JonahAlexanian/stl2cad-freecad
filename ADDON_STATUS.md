# STL2CAD add-on status

Saved 2026-10-20.

## Listing

- FreeCAD Addon Manager: **not listed yet**
- Public repo: https://github.com/JonahAlexanian/stl2cad-freecad
- Branch: `main`
- GitHub account: JonahAlexanian
- Topics: freecad, addon
- Addition request: https://github.com/FreeCAD/Addons/issues/180 (open)

FreeCAD still has to review issue 180. After they accept it, STL2CAD shows up in **Tools → Addon Manager**, usually about a day later.

## What the add-on is

- Name: STL2CAD
- Version: 0.1.0
- FreeCAD: 1.0 or newer
- License: LGPL-2.1-or-later
- It converts an STL, or the model on screen, into a STEP file and saves that file.
- It is free for FreeCAD users.
- Help: https://ragbox.llc/
- GAID (Guide AI Dev Pro) was used to build it.
- The add-on calls https://www.stl2cad.com. https://stl2cad.com is the same converter. Both were answering when this was published.
- People who open that website on their own are using a separate product.

## What was published

These files are on the public repo:

- `package.xml`
- `README.md`
- `LICENSE`
- `.gitignore`
- `Init.py`
- `InitGui.py`
- `Stl2Cad/client.py`
- `Stl2Cad/panel.py`

Local notes, CPFS logs, and agent rules were not published.

## Checked

- Repo page returned 200
- `package.xml` on GitHub names the repo and LGPL-2.1-or-later
- Published `Stl2Cad/client.py` calls https://www.stl2cad.com
- FreeCAD issue 180 returned 200

Proof of that check: `logs/publish-freecad-addon.txt`

The full day note, including the disk, the sites, and what not to redo, is `/home/rgesaah/factai/project_status/2026-10-20_long_day_handoff.md`.
