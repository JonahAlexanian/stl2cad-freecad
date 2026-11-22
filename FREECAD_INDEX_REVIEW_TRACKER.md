# FreeCAD Addon Index — review tracker (issue #213)

**Reviewer:** mnesarco (2026-11-22)  
**Full review:** `docs/freecad-addons-review-213-email.md`  
**Issue:** https://github.com/FreeCAD/Addons/issues/213  

**Rule:** Fix **one item at a time**. Change status only when implemented and verified; then note the commit/date in the session log.

**Legend:** `open` | `in progress` | `fixed` | `wontfix`

---

## Admission blockers (must fix for Index)

| ID | Status | Summary |
|----|--------|---------|
| 1 | **fixed** | In-app privacy consent before uploads; revocable prefs; guard all upload paths — **owner verified Win/FC 1.0: No blocks, Yes converts** |
| 2 | **fixed** | Icon SVG + workbench `Icon` + `package.xml` `<icon>` (owner saw icon on Windows) |
| 3 | **fixed** (local) | `<freecadmin>1.0.0` + tested 1.0 on Windows documented in `docs/verified-freecad.md` |

---

## Medium — governance / manifest / docs

| ID | Status | Summary |
|----|--------|---------|
| 4 | **fixed** (local) | `SECURITY.md`; `ADDON_STATUS.md` removed from repo + gitignore |
| 5 | **fixed** | Neutral descriptions; drop RAG/GAID from manifest, tooltip, panel lead |
| 14 | **fixed** | Remove `<subdirectory>` from `package.xml` |
| 15 | **fixed** | README URL → raw.githubusercontent.com |
| 16 | **fixed** | Add author, tags, pythonmin to manifest |
| 24 | open | README: privacy table, limitations, SECURITY link (**SECURITY link done**) |
| 25 | **in progress** | pyproject + CHANGELOG done; release tag pending push |
| 26 | **fixed** | .gitignore dev artifacts |
| 27 | **fixed** (init.py) | Remove `init.py`, stale public notes |
| 29 | open | Single version source of truth |

---

## Medium — correctness / robustness

| ID | Status | Summary |
|----|--------|---------|
| 6 | **fixed** | FreeCAD PySide shim |
| 7 | **fixed** | Preview download failure must not break Save STEP |
| 8 | **fixed** | Padded binary STL accepted |
| 9 | **fixed** (local) | Load STL in worker + progress; preview cache / half-res while dragging |
| 10 | **fixed** | Private temp dir removed after upload (`mkdtemp`) |
| 11 | **fixed** (local) | pyproject, pytest, GitHub Actions CI |
| 12 | **fixed** | Removed unused mesh-reduction code in client.py |
| 13 | **fixed** | `from . import panel` in init_gui |
| 23 | **fixed** | Sanitize multipart filename |

---

## Medium / low — UX & tooling

| ID | Status | Summary |
|----|--------|---------|
| 17 | **fixed** | STL2CAD_OpenPanel command |
| 18 | **fixed** | Dock objectName |
| 19 | **fixed** | _DOCK validity / destroyed hook |
| 20 | **fixed** | Per-instance event queue |
| 21 | open | Translations |
| 22 | open | Preview palette colors |
| 28 | **in progress** | Layout verify script updated; CI still open (#11) |

---

## Reviewer suggested order

1. #1 + README privacy (with #24 partially) + #4 SECURITY  
2. #2 icon, #3 compatibility  
3. #4 (ADDON_STATUS), #5, #14–#16  
4. #6, #13, #17–#20  
5. #7, #8, #10, #23  
6. #9 performance  
7. #11, #12, #28  
8. #21, #22, #25–#27, #29  

---

## Pre-submission verification (reviewer)

```text
python3 scripts/verify_modern_addon_layout.py
uv run ruff check .
uv run bandit -r freecad/
uv run pytest
```

Plus manual smoke: consent yes/no, Save after preview fail, padded STL; document FreeCAD version.

---

## Session log

| Date | Action |
|------|--------|
| 2026-11-22 | Saved review email; created tracker; **29 items = open**. |
| 2026-11-22 | **#1** consent + README privacy table — `consent.py`, prefs page, `_request` guard. |
| 2026-11-22 | Owner smoke **#1** on Windows: dialog on Convert; No stops; Yes uploads and converts. |