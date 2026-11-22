"""In-app consent for sending model data to the STL2CAD converter service."""

SERVICE_ID = "stl2cad.com"
CONSENT_SCOPE = 1
PARAM_GROUP = "User parameter:BaseApp/Preferences/Mod/STL2CAD/Consent"

CONSENT_BODY = (
    "This sends the model mesh (triangle coordinates) and the file name "
    "to https://www.stl2cad.com for conversion. Each Convert sends data once. "
    "Open viewer shares the job id with the same site.\n\nContinue?"
)

_test_override = None


def _consent_key(service_id=SERVICE_ID):
    return "%s:scope%s" % (service_id, CONSENT_SCOPE)


def _param_group():
    import FreeCAD as App

    return App.ParamGet(PARAM_GROUP)


def has_consent(service_id=SERVICE_ID):
    if _test_override is not None:
        return bool(_test_override)
    return _param_group().GetBool(_consent_key(service_id), False)


def set_consent(granted, service_id=SERVICE_ID):
    _param_group().SetBool(_consent_key(service_id), bool(granted))


def revoke_consent(service_id=SERVICE_ID):
    set_consent(False, service_id)


def ensure_consent(service_id=SERVICE_ID):
    """Prompt once per scope; store answer in the parameter group."""
    if has_consent(service_id):
        return True
    import FreeCADGui as Gui

    from PySide import QtWidgets

    answer = QtWidgets.QMessageBox.warning(
        Gui.getMainWindow(),
        "External service",
        CONSENT_BODY,
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )
    if answer != QtWidgets.QMessageBox.Yes:
        return False
    set_consent(True, service_id)
    return True