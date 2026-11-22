# STL2CAD add-on status

Saved 2026-11-22.

## Listing

- FreeCAD Addon Manager: **not listed yet** (waiting on review)
- Public repo: https://github.com/JonahAlexanian/stl2cad-freecad
- Branch: `main`
- GitHub account: JonahAlexanian
- Topics: freecad, addon
- First request: https://github.com/FreeCAD/Addons/issues/180 (closed 2026-10-26 — 30-day wait)
- **Current request:** https://github.com/FreeCAD/Addons/issues/213 (open, filed 2026-11-22)
- **Reviewer:** mnesarco asked for modern namespaced layout (2026-11-22). Migrated in **v0.1.1** to `freecad/stl2cad/`.

FreeCAD closed issue 180 because a new repo must be 30 days old (repo created 2026-10-20). We resubmitted on 2026-11-22 as issue 213. Do not reopen issue 180. Watch issue 213 and GitHub email until they accept; then STL2CAD should appear in **Tools → Addon Manager** about a day later. Follow-up note: `/home/rgesaah/reminders/stl2cad-freecad-FOLLOW-UP.md`.

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
