"""STL2CAD preference page — review and revoke remote-service consent."""

from . import consent


def register():
    import FreeCADGui as Gui

    Gui.addPreferencePage(Stl2CadConsentPreferences, "STL2CAD")


class Stl2CadConsentPreferences:
    def __init__(self):
        from PySide import QtWidgets

        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.form)
        self._status = QtWidgets.QLabel("")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)
        hint = QtWidgets.QLabel(
            "Consent covers uploads of mesh data and file names, job polling, "
            "STEP download, preview mesh, and opening the web viewer for a job."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self._revoke = QtWidgets.QPushButton("Revoke consent")
        self._revoke.clicked.connect(self._on_revoke)
        layout.addWidget(self._revoke)
        layout.addStretch(1)
        self.loadSettings()

    def _on_revoke(self):
        consent.revoke_consent()
        self.loadSettings()

    def loadSettings(self):
        if consent.has_consent():
            self._status.setText(
                "Consent is granted for https://www.stl2cad.com (scope %s)."
                % consent.CONSENT_SCOPE
            )
            self._revoke.setEnabled(True)
        else:
            self._status.setText(
                "Consent is not granted. Convert will ask before the first request."
            )
            self._revoke.setEnabled(False)

    def saveSettings(self):
        pass