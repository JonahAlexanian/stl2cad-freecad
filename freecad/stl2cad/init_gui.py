"""STL2CAD workbench. Opens the RAG Box and GAID panel."""

import FreeCADGui as Gui


class Stl2CadWorkbench(Gui.Workbench):
    MenuText = "STL2CAD"
    ToolTip = "RAG Box and GAID"

    def Initialize(self):
        pass

    def Activated(self):
        from freecad.stl2cad import panel

        panel.show()

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(Stl2CadWorkbench())