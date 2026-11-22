"""Small Qt helpers using FreeCAD's PySide shim."""


def dock_widget_area_left(QtCore):
    area = getattr(QtCore.Qt, "DockWidgetArea", None)
    if area is not None and hasattr(area, "LeftDockWidgetArea"):
        return area.LeftDockWidgetArea
    return QtCore.Qt.LeftDockWidgetArea


def rich_text_format(QtCore):
    rich = getattr(QtCore.Qt, "RichText", None)
    if rich is None:
        rich = QtCore.Qt.TextFormat.RichText
    return rich


def widget_is_valid(widget):
    if widget is None:
        return False
    try:
        from PySide import shiboken
    except ImportError:
        import shiboken2 as shiboken

    return shiboken.isValid(widget)