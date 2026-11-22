# STL2CAD add-on status

Updated 2026-11-22 (end of listing/layout work).

## Where we are (read this first)

**Waiting on FreeCAD.** Nothing more to submit unless they comment on the issue.

| Item | Status |
|------|--------|
| Addon Manager listing | **Not listed yet** |
| Active request | [FreeCAD/Addons#213](https://github.com/FreeCAD/Addons/issues/213) — **open**, wait for team |
| Do not reopen | [#180](https://github.com/FreeCAD/Addons/issues/180) (30-day wait; closed 2026-10-26) |
| Our repo | [JonahAlexanian/stl2cad-freecad](https://github.com/JonahAlexanian/stl2cad-freecad) `main` |
| Add-on version in `package.xml` | **0.1.1** |

### Timeline

1. **2026-10-20** — Public repo created; first listing request **#180**.
2. **2026-10-26** — **chennes**: mandatory **30-day** repo age; closed **#180**.
3. **2026-11-22** — Resubmitted **#213**.
4. **2026-11-22** — **mnesarco**: use **modern** layout, not legacy `Init.py` / `InitGui.py`.
5. **2026-11-22** — Migrated to `freecad/stl2cad/`; removed legacy root + `Stl2Cad/` (commits `697ae48`, `77705bc`). Replied on **#213**.
6. **2026-11-22** — **Owner verified on Windows (FreeCAD 1.0):** panel loads, convert works. Must select all document objects, then **Load STL**, then **Convert**.

### What happens next

- Watch **#213** and GitHub email for accept or more feedback.
- After acceptance, **Tools → Addon Manager** → **STL2CAD** (often ~1 day later).
- Until then, install from git/`scp` is fine (see below).

## Layout (modern only)

```
package.xml
freecad/stl2cad/
  init_gui.py
  init.py
  __init__.py
  panel.py
  client.py
```

- **No** root `Init.py`, `InitGui.py`, or `Stl2Cad/`.
- **No** `freecad/__init__.py` at repo root (would break FreeCAD).

Machine check: `python3 scripts/verify_modern_addon_layout.py` → `PASS`.

## Windows install (owner PC)

```powershell
Remove-Item -Recurse -Force $env:APPDATA\FreeCAD\Mod\stl2cad-freecad
scp -r rgesaah@192.168.1.15:/home/rgesaah/stl2cad-freecad "$env:APPDATA\FreeCAD\Mod\stl2cad-freecad"
```

Fully quit FreeCAD, reopen, select **STL2CAD** workbench. For multi-body documents, select all objects in the tree before **Load STL**.

## What the add-on is

- Free **STL → STEP** inside FreeCAD; calls **https://www.stl2cad.com** (same converter as public product).
- Help: **https://ragbox.llc/**. Sponsors: RAG Box, GAID.
- **stl2cad.com** direct visitors = separate paid product.

## Other notes

- Follow-up reminder doc: `/home/rgesaah/reminders/stl2cad-freecad-FOLLOW-UP.md`
- Longer handoff: `HANDOFF_2026-11-22.md`
- Product/engine rules: `/home/rgesaah/factai/project_status/2026-10-18_stl2cad_one_engine_two_interfaces_handoff.md`