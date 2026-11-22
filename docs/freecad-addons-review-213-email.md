# STL2CAD FreeCAD add-on — review and recommendations

**Source:** GitHub notification, Re: [FreeCAD/Addons] STL2CAD (Issue #213)  
**Author:** mnesarco  
**Received:** 2026-11-22  
**Repository:** https://github.com/JonahAlexanian/stl2cad-freecad  
**Branch / commit:** main @ 77705bc (2026-11-22)  
**Version reviewed:** package.xml 0.1.1  

---

Repository: https://github.com/JonahAlexanian/stl2cad-freecad  
Branch / commit: main @ 77705bc (2026-11-22)  
Version reviewed: package.xml 0.1.1  
Scope: read every tracked file, checked layout, manifest, startup, UI lifecycle, network/privacy, error handling, and release readiness against the FreeCAD Addon Index expectations and modern add-on conventions.

**Verdict:** the modernization to freecad/stl2cad/ is correct and the code is clean and dependency-free. Three items block Addon Index admission (privacy consent, icon, honest compatibility), and a handful of correctness and robustness issues should be fixed before the next release. Nothing here requires a rewrite. Most fixes are small and local.

## What is already right

- Modern namespaced layout: freecad/stl2cad/, no root __init__.py, no freecad/__init__.py, no legacy Init.py / InitGui.py.
- __init__.py is console-safe; init_gui.py only defines and registers the workbench; the Qt panel is imported lazily in Activated().
- panel.py imports client relatively; no sys.path manipulation.
- package.xml classname matches the workbench class, branch="main" matches the branch, and the SPDX id matches LICENSE and the README.
- Standard library only, no vendoring, no runtime package installs, no eval/exec/subprocess, TLS verification left at the urllib default.
- STEP output is validated (ISO-10303-21) before being written.
- Mesh work and rendering live in a pure module (client.py) that can be tested without FreeCAD.

## Blockers before Addon Index admission

### 1. HIGH — Data leaves the machine without in-app consent

Where: freecad/stl2cad/panel.py:439-458 (on_convert → upload_stl), panel.py:488-498 (on_bigger), client.py:220-235.

What happens: on Convert, the add-on uploads the entire STL (the selected model tessellation or the chosen file) plus its filename to https://www.stl2cad.com/api/jobs/upload. Open viewer also sends the job id to the same site. A README sentence naming the host is disclosure, not consent; the Index requires consent inside FreeCAD, before the first request, naming the service and every kind of data sent, per service, revocable, and re-asked when the service or data changes. No default remote service is allowed.

Recommendation: Ask before the first upload, from the panel, store in parameter store keyed by service and scope version; guard upload path; preference page to revoke; README privacy table.

### 2. HIGH — No icon

Where: init_gui.py:6, package.xml, no resources/ directory. Add svg, Icon, addIconPath, `<icon>` in manifest.

### 3. HIGH — Compatibility is claimed but not honest/tested

Where: package.xml freecadmin 1.0.0, README FreeCAD 1.0. Raise to 1.1.0 or test 1.0 with evidence.

### 4. MEDIUM — No SECURITY.md and internal notes are published

Add SECURITY.md. Remove ADDON_STATUS.md from public repo (local paths, stale file list).

### 5. MEDIUM — Description carries sponsor/AI marketing text

Neutral functional description; sponsor credit README only.

## Correctness and robustness (6–13, 23)

6. Use FreeCAD Qt shim (PySide), not _qt() PySide6/2.  
7. Preview failure must not discard successful conversion.  
8. Valid binary STLs with trailing bytes rejected — use `>=` length test.  
9. Heavy work on GUI thread (mesh + preview paint).  
10. Model data in shared temp — private dir or bytes upload.  
11. No tests and no CI — pyproject, pytest, ruff, bandit.  
12. Dead mesh-reduction code in client.py — delete or wire.  
13. Intra-package import should be `from . import panel`.  
23. Sanitize filename in multipart header.

## Polish table (14–29)

14. Remove `<subdirectory>`.  
15. README raw URL in package.xml.  
16. author, tag, pythonmin.  
17. Register STL2CAD_OpenPanel command.  
18. dock.setObjectName.  
19. _DOCK destroyed / isValid.  
20. Per-panel event queue.  
21. Translations.  
22. Preview colors from palette.  
24. README privacy, limitations, screenshots.  
25. pyproject, CHANGELOG, tag v0.1.2.  
26. .gitignore.  
27. Remove ADDON_STATUS, init.py.  
28. Fix verify_modern_addon_layout.py.  
29. Version single source of truth.

## Suggested order of work

1. Consent + privacy table (#1) and SECURITY.md (#4)  
2. Icon (#2) and honest compatibility (#3)  
3. Remove ADDON_STATUS.md, fix manifest (#4, #14–16), clean sponsor text (#5)  
4. Qt shim (#6), from . import panel (#13), dock/command (#17–20)  
5. Robustness: preview (#7), padded STL (#8), temp (#10), headers (#23)  
6. Performance (#9)  
7. Dead code (#12), tests/CI (#11), layout script (#28)  
8. Translations, palette, gitignore, CHANGELOG/tag (#21–22, #25–26, #29)  

## Verification before the next submission

- python3 scripts/verify_modern_addon_layout.py  
- uv run ruff check .  
- uv run bandit -r freecad/  
- uv run pytest  
- Manual smoke: consent declined/accepted, Save after preview fail, padded binary STL; state FreeCAD version in release notes.

---

[Issue #213](https://github.com/FreeCAD/Addons/issues/213) — reply on GitHub when fixes ship.