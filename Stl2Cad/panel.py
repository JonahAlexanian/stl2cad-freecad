"""STL2CAD panel. Names RAG Box and GAID, then sends a chosen STL to the converter."""

import os
import queue
import tempfile

import client

RAG_BOX = (
    "RAG Box sponsors free STL2STEP for FreeCAD. "
    '<a href="https://ragbox.llc/">Get help at RAG Box</a>.'
)
GAID = (
    "GAID (Guide AI Dev Pro) guides AI programming. "
    "It was used to build this FreeCAD add-on."
)

_DOCK = None
_EVENTS = queue.Queue()


def panel_lines():
    return (RAG_BOX, GAID)


def large_view_size(width, height):
    """Size of the large STL and STEP window."""
    return max(int(width) * 9 // 10, 960), max(int(height) * 17 // 20, 640)


def _qt():
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
    except ImportError:
        from PySide2 import QtCore, QtGui, QtWidgets
    return QtCore, QtGui, QtWidgets


def _left_area(QtCore):
    dock = getattr(QtCore.Qt, "DockWidgetArea", None)
    if dock is not None and hasattr(dock, "LeftDockWidgetArea"):
        return dock.LeftDockWidgetArea
    return QtCore.Qt.LeftDockWidgetArea


def _deviation_mm(slider_value):
    """Surface deviation. 0 is coarse (2 mm). 100 is fine (0.02 mm)."""
    t = max(0, min(100, int(slider_value))) / 100.0
    return 2.0 * ((0.02 / 2.0) ** t)


def _shape_facets(shape, deviation):
    """Mesh one shape the way FreeCAD's STL export does."""
    try:
        import MeshPart

        mesh = MeshPart.meshFromShape(
            Shape=shape,
            LinearDeflection=float(deviation),
            AngularDeflection=0.5,
            Relative=False,
        )
        return [
            tuple(tuple(point) for point in facet.Points) for facet in mesh.Facets
        ]
    except Exception:
        points, triangles = shape.tessellate(float(deviation))
        return [
            tuple(tuple(points[index]) for index in tri) for tri in triangles
        ]


def _has_export_shape(obj):
    mesh = getattr(obj, "Mesh", None)
    if mesh is not None and getattr(mesh, "CountFacets", 0):
        return True
    shape = getattr(obj, "Shape", None)
    return shape is not None and not shape.isNull() and bool(shape.Faces)


def _facets_from_selection(deviation):
    """STL triangles for the selected FreeCAD objects."""
    import FreeCADGui as Gui

    selected = list(Gui.Selection.getSelection())
    if not selected:
        raise RuntimeError("Select the object, then Load STL.")
    chosen = []
    for obj in selected:
        if not _has_export_shape(obj):
            continue
        covered = False
        for other in selected:
            if other is obj:
                continue
            if obj in getattr(other, "OutList", []) and _has_export_shape(other):
                covered = True
                break
        if not covered:
            chosen.append(obj)
    facets = []
    for obj in chosen:
        mesh = getattr(obj, "Mesh", None)
        if mesh is not None and getattr(mesh, "CountFacets", 0):
            for facet in mesh.Facets:
                facets.append(tuple(tuple(point) for point in facet.Points))
            continue
        facets.extend(_shape_facets(obj.Shape, deviation))
    if not facets:
        raise RuntimeError("The selection has no solid to export.")
    return facets


def _step_triangles(job, status):
    done = (status or {}).get("state") == "done" or bool((job or {}).get("has_step"))
    if not done:
        return None
    payload = client.read_step_preview(job.get("id"))
    return client.step_preview_triangles(payload)


def _run_convert(stl_path, facets, remove_after=False, consider_extrusions=True):
    try:
        job = client.upload_stl(stl_path)
        job_id = job.get("id")
        if not job_id:
            raise RuntimeError("The converter did not return a job.")
        job["id"] = job_id
        client.start_convert(job_id, consider_extrusions=consider_extrusions)
        status = client.read_status(job_id)
        _EVENTS.put(("update", job, status, facets, _step_triangles(job, status)))
    except Exception as exc:
        _EVENTS.put(("error", str(exc)))
    finally:
        if remove_after:
            try:
                os.remove(stl_path)
            except OSError:
                pass


def _poll_job(job_id, facets):
    try:
        status = client.read_status(job_id)
        job = client.read_job(job_id)
        job["id"] = job_id
        _EVENTS.put(("update", job, status, facets, _step_triangles(job, status)))
    except Exception as exc:
        _EVENTS.put(("error", str(exc)))


def _shape_view(QtCore, QtGui, QtWidgets):
    class _View(QtWidgets.QWidget):
        def __init__(self, empty_text):
            super(_View, self).__init__()
            self._empty = empty_text
            self._triangles = []
            self._yaw = 0.9
            self._pitch = 0.45
            self._zoom = 1.0
            self._last = None
            self.setMinimumSize(280, 240)
            policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
            )
            self.setSizePolicy(policy)

        def set_triangles(self, triangles):
            triangles = list(triangles or [])
            if triangles == self._triangles:
                return
            self._triangles = triangles
            self._yaw = 0.9
            self._pitch = 0.45
            self._zoom = 1.0
            self.update()

        def mousePressEvent(self, event):
            self._last = event.pos()

        def mouseMoveEvent(self, event):
            if self._last is None or not (event.buttons() & QtCore.Qt.LeftButton):
                return
            pos = event.pos()
            self._yaw += (pos.x() - self._last.x()) * 0.01
            self._pitch += (pos.y() - self._last.y()) * 0.01
            self._last = pos
            self.update()

        def mouseReleaseEvent(self, _event):
            self._last = None

        def wheelEvent(self, event):
            step = event.angleDelta().y()
            self._zoom *= 1.1 if step > 0 else 0.9
            self._zoom = max(0.2, min(self._zoom, 8.0))
            self.update()

        def paintEvent(self, _event):
            painter = QtGui.QPainter(self)
            painter.fillRect(self.rect(), QtGui.QColor(32, 34, 38))
            if not self._triangles:
                painter.setPen(QtGui.QColor(190, 190, 190))
                painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self._empty)
                return
            shades = client.render_view(
                self._triangles, self._yaw, self._pitch, self._zoom,
                self.width(), self.height(),
            )
            if not shades:
                painter.setPen(QtGui.QColor(190, 190, 190))
                painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self._empty)
                return
            width = self.width()
            height = self.height()
            pixels = bytearray(width * height * 4)
            for index, shade in enumerate(shades):
                offset = index * 4
                if shade:
                    pixels[offset] = shade
                    pixels[offset + 1] = shade
                    pixels[offset + 2] = shade
                else:
                    pixels[offset] = 38
                    pixels[offset + 1] = 34
                    pixels[offset + 2] = 32
                pixels[offset + 3] = 255
            image = QtGui.QImage(
                bytes(pixels), width, height, width * 4, QtGui.QImage.Format_RGB32
            )
            painter.drawImage(0, 0, image)

    return _View


def show():
    """Open the panel in the FreeCAD main window."""
    global _DOCK
    import threading

    import FreeCADGui as Gui

    QtCore, QtGui, QtWidgets = _qt()
    window = Gui.getMainWindow()
    if _DOCK is not None:
        _DOCK.show()
        _DOCK.raise_()
        return

    view_cls = _shape_view(QtCore, QtGui, QtWidgets)
    dock = QtWidgets.QDockWidget("STL2CAD", window)
    dock.setMinimumSize(680, 420)
    body = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(body)
    rich = getattr(QtCore.Qt, "RichText", None)
    if rich is None:
        rich = QtCore.Qt.TextFormat.RichText
    for line in panel_lines():
        label = QtWidgets.QLabel(line)
        label.setWordWrap(True)
        label.setTextFormat(rich)
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        layout.addWidget(label)

    density = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    density.setRange(0, 100)
    density.setValue(65)
    deviation = QtWidgets.QLabel("")
    layout.addWidget(deviation)
    layout.addWidget(density)
    buttons = QtWidgets.QHBoxLayout()
    load_button = QtWidgets.QPushButton("Load STL")
    upload_button = QtWidgets.QPushButton("Upload STL")
    button = QtWidgets.QPushButton("Convert")
    buttons.addWidget(load_button, 1)
    buttons.addWidget(upload_button, 1)
    buttons.addWidget(button, 1)
    layout.addLayout(buttons)
    consider_box = QtWidgets.QCheckBox("Consider extrusions")
    consider_box.setChecked(True)
    consider_box.setToolTip(
        "After Paint All, replace straight pulls and round holes. Uncheck if a result looks wrong."
    )
    progress = QtWidgets.QProgressBar()
    progress.setTextVisible(True)
    progress.setVisible(False)
    bigger_button = QtWidgets.QPushButton("Open viewer")
    save_button = QtWidgets.QPushButton("Save STEP")
    second = QtWidgets.QHBoxLayout()
    second.addWidget(consider_box)
    second.addWidget(progress, 1)
    second.addWidget(bigger_button)
    second.addWidget(save_button)
    layout.addLayout(second)
    status = QtWidgets.QLabel(client.status_line(None))
    status.setWordWrap(True)
    layout.addWidget(status)

    columns = QtWidgets.QHBoxLayout()
    left_box = QtWidgets.QGroupBox("STL")
    left_layout = QtWidgets.QVBoxLayout(left_box)
    left_view = view_cls("Select an object, then Load STL")
    left_layout.addWidget(left_view)
    right_box = QtWidgets.QGroupBox("STEP")
    right_layout = QtWidgets.QVBoxLayout(right_box)
    right_view = view_cls("The result")
    right_layout.addWidget(right_view)
    columns.addWidget(left_box)
    columns.addWidget(right_box)
    layout.addLayout(columns)
    dock.setWidget(body)

    state = {
        "job_id": None,
        "busy": False,
        "facets": [],
        "path": None,
        "step": [],
        "source": None,
    }

    def show_deviation():
        deviation.setText(
            "Deviation %.2f mm. Slide right for a finer mesh."
            % _deviation_mm(density.value())
        )

    def set_busy(locked):
        load_button.setEnabled(not locked)
        upload_button.setEnabled(not locked)
        button.setEnabled(not locked)
        consider_box.setEnabled(not locked)
        save_button.setEnabled(not locked)
        density.setEnabled(not locked)

    def apply_event():
        try:
            kind, *rest = _EVENTS.get_nowait()
        except queue.Empty:
            return
        if kind == "error":
            state["busy"] = False
            state["job_id"] = None
            status.setText(rest[0])
            progress.setVisible(False)
            set_busy(False)
            return
        if kind == "saved":
            state["busy"] = False
            set_busy(False)
            status.setText("Saved %s" % rest[0])
            return
        job, job_status, facets, step = rest
        state["facets"] = facets or []
        finished = step is not None or (job_status or {}).get("state") in ("done", "error")
        if job.get("id"):
            state["done_id"] = job.get("id")
        if job.get("step_file"):
            state["step_name"] = job.get("step_file")
        state["job_id"] = None if finished else job.get("id")
        left_view.set_triangles(state["facets"])
        if step is not None:
            state["step"] = step
            right_view.set_triangles(step)
        status.setText(client.status_line(job_status, has_picture=bool(step)))
        done = (job_status or {}).get("progress_done")
        total = (job_status or {}).get("progress_total")
        if total and not finished:
            progress.setVisible(True)
            progress.setMaximum(max(int(total), 1))
            progress.setValue(max(0, min(int(done or 0), int(total))))
            progress.setFormat("%v / %m")
        else:
            progress.setVisible(False)
        if state["job_id"] is None:
            state["busy"] = False
            set_busy(False)

    def on_tick():
        apply_event()
        job_id = state["job_id"]
        if job_id and not state.get("polling"):
            state["polling"] = True
            facets = state["facets"]

            def worker():
                try:
                    _poll_job(job_id, facets)
                finally:
                    state["polling"] = False

            threading.Thread(target=worker, daemon=True).start()

    def show_facets(facets, message):
        state["facets"] = facets
        state["step"] = []
        left_view.set_triangles(facets)
        right_view.set_triangles([])
        status.setText(message)

    def on_load():
        if state["busy"]:
            return
        try:
            facets = _facets_from_selection(_deviation_mm(density.value()))
        except Exception as exc:
            status.setText(str(exc))
            return
        state["source"] = "model"
        state["path"] = None
        show_facets(
            facets,
            "Loaded %s triangles at %.2f mm. Press Convert."
            % (format(len(facets), ","), _deviation_mm(density.value())),
        )

    def on_upload():
        if state["busy"]:
            return
        chosen, _selected = QtWidgets.QFileDialog.getOpenFileName(
            dock, "Upload STL", "", "STL files (*.stl)"
        )
        if not chosen:
            return
        try:
            facets = client.read_stl(chosen)
        except Exception as exc:
            status.setText(str(exc))
            return
        state["source"] = "file"
        state["path"] = chosen
        show_facets(
            facets,
            "Uploaded %s (%s triangles). Press Convert."
            % (os.path.basename(chosen), format(len(facets), ",")),
        )

    def on_convert():
        if state["busy"]:
            return
        facets = state.get("facets") or []
        if not facets:
            status.setText("Load the selected object, or upload an STL, then Convert.")
            return
        handle = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
        handle.close()
        client.write_stl(handle.name, facets)
        state["busy"] = True
        state["step"] = []
        set_busy(True)
        right_view.set_triangles([])
        status.setText("Sending %s triangles." % format(len(facets), ","))
        threading.Thread(
            target=_run_convert,
            args=(handle.name, facets, True, consider_box.isChecked()),
            daemon=True,
        ).start()

    def on_save():
        if state["busy"]:
            return
        job_id = state.get("done_id")
        if not job_id:
            status.setText("Convert first. Then Save writes the STEP.")
            return
        suggested = state.get("step_name") or "model.step"
        chosen, _selected = QtWidgets.QFileDialog.getSaveFileName(
            dock, "Save STEP", suggested, "STEP files (*.step *.stp)"
        )
        if not chosen:
            return
        if not chosen.lower().endswith((".step", ".stp")):
            chosen += ".step"
        state["busy"] = True
        set_busy(True)
        status.setText("Saving the STEP.")

        def worker():
            try:
                client.save_step(job_id, chosen)
                _EVENTS.put(("saved", chosen))
            except Exception as exc:
                _EVENTS.put(("error", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def on_bigger():
        job_id = state.get("job_id") or state.get("done_id")
        if not job_id:
            status.setText("Convert first. Then Open viewer uses the stl2cad page.")
            return
        url = "%s/?job_id=%s&freecad=1" % (client.DEFAULT_BASE, job_id)
        opened = QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        if not opened:
            status.setText("Browser did not open. Use this address: %s" % url)
            return
        status.setText("Opened the stl2cad viewer.")

    def on_density_done():
        show_deviation()
        if state.get("source") == "model":
            on_load()

    show_deviation()
    load_button.clicked.connect(on_load)
    upload_button.clicked.connect(on_upload)
    density.sliderReleased.connect(on_density_done)
    density.valueChanged.connect(lambda _value: show_deviation())
    button.clicked.connect(on_convert)
    bigger_button.clicked.connect(on_bigger)
    save_button.clicked.connect(on_save)
    timer = QtCore.QTimer(dock)
    timer.setInterval(1000)
    timer.timeout.connect(on_tick)
    timer.start()

    window.addDockWidget(_left_area(QtCore), dock)
    _DOCK = dock
