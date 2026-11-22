"""STL2CAD workbench — convert mesh or STL to STEP."""

from pathlib import Path

import FreeCADGui as Gui

_PKG = Path(__file__).resolve().parent
_ICON = str(_PKG / "resources" / "icons" / "stl2cad.svg")


class Stl2CadWorkbench(Gui.Workbench):
    MenuText = "STL2CAD"
    ToolTip = "Convert an STL or the selected model to STEP"
    Icon = _ICON

    def Initialize(self):
        from . import commands, preferences

        commands.register()
        preferences.register()
        self.appendToolbar("STL2CAD", ["STL2CAD_OpenPanel"])
        self.appendMenu("STL2CAD", ["STL2CAD_OpenPanel"])

    def Activated(self):
        from . import panel

        panel.show()

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addIconPath(str(_PKG / "resources" / "icons"))
Gui.addWorkbench(Stl2CadWorkbench())