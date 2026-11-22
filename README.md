# STL2CAD

FreeCAD workbench that converts an STL, or the model on screen, into a STEP file.

It is free for FreeCAD users. Sponsored by [RAG Box](https://ragbox.llc/) — get help there.

## Install

After FreeCAD lists it, open **Tools → Addon Manager**, find **STL2CAD**, and install it. Then switch to the **STL2CAD** workbench.

**Minimum FreeCAD:** 1.0 (`package.xml` → `<freecadmin>1.0.0</freecadmin>`).

**Tested by the maintainer:** FreeCAD **1.0** on Windows (2026-11-22) — workbench, icon, consent, Load STL, Convert. Newer releases may work but are **not** listed as verified unless noted in [docs/verified-freecad.md](docs/verified-freecad.md).

The workbench uses the modern namespaced layout: `freecad/stl2cad/` with `init_gui.py` (see `package.xml`).

## Use

1. Open a model, or leave the screen empty if you will upload an STL.
2. **Load STL** sends the model on screen. **Upload STL** picks a file.
3. Move the density slider if you want a coarser or finer mesh, then click **Convert**.
4. **Consider extrusions** is on by default. Turn it off if you do not like that result.
5. **Open viewer** shows the STL and the STEP. **Save STEP** writes the STEP file where you name it.

The add-on asks inside FreeCAD before the first request to that service. You can revoke consent under **Edit → Preferences → STL2CAD**.

## Privacy and external services

| Service | Endpoint | Data sent | Trigger | Frequency | Retention | Consent | Opt-out |
|--------|----------|-----------|---------|-----------|-----------|---------|---------|
| STL2CAD converter | `https://www.stl2cad.com` (`/api/jobs/*`) | STL mesh (triangle coordinates), original file name, job id, conversion options | **Convert** | Once per Convert | Set by service operator; not controlled by this add-on | In-app dialog before first request; stored in FreeCAD user parameters (`STL2CAD/Consent`); re-prompt when scope changes | **Edit → Preferences → STL2CAD → Revoke consent** (blocks further requests) |
| STL2CAD web viewer | `https://www.stl2cad.com/?job_id=…` | Job id in URL (browser) | **Open viewer** | Per click | Browser/session | Same consent as above | Revoke consent; do not open viewer |

People who open https://www.stl2cad.com on their own are using a separate product.

## Known limitations

- Conversion requires network access to stl2cad.com after in-app consent.
- Large selections can produce dense meshes; use the deviation slider or upload a coarser STL.
- STEP preview in the panel is best-effort; **Save STEP** may still work if preview fails.
- Maintainer-verified platform list: [docs/verified-freecad.md](docs/verified-freecad.md) (not every OS/version).

## Security

Report vulnerabilities privately. See [SECURITY.md](SECURITY.md).

## License

LGPL-2.1-or-later. See `LICENSE`.
