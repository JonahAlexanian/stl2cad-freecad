"""STL2CAD FreeCAD commands."""

from pathlib import Path

import FreeCADGui as Gui

_PKG = Path(__file__).resolve().parent
_ICON = str(_PKG / "resources" / "icons" / "stl2cad.svg")


class Stl2CadOpenPanelCommand:
    """Reopen the STL2CAD dock after it was closed."""

    def GetResources(self):
        return {
            "Pixmap": _ICON,
            "MenuText": "Open STL2CAD panel",
            "ToolTip": "Show the STL2CAD conversion panel",
        }

    def Activated(self):
        from . import panel

        panel.show()

    def IsActive(self):
        return True


def register():
    Gui.addCommand("STL2CAD_OpenPanel", Stl2CadOpenPanelCommand())