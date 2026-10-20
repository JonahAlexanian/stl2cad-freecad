"""STL2CAD workbench. Opens the RAG Box and GAID panel."""

import inspect
import os
import sys

import FreeCADGui as Gui

# FreeCAD runs this file with exec() and does not set __file__.
_ROOT = os.path.dirname(os.path.abspath(inspect.currentframe().f_code.co_filename))
_PKG = os.path.join(_ROOT, "Stl2Cad")
if _PKG not in sys.path:
    sys.path.insert(0, _PKG)

class Stl2CadWorkbench(Gui.Workbench):
    MenuText = "STL2CAD"
    ToolTip = "RAG Box and GAID"

    def Initialize(self):
        pass

    def Activated(self):
        # Import here. A top-level import is not visible to this method.
        import panel
        panel.show()

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(Stl2CadWorkbench())
