"""Call the existing STL→STEP service. Save writes the STEP that service already made."""

import json
import math
import os
import struct
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://www.stl2cad.com"
_CLIENT_HEADERS = {"User-Agent": "STL2CAD-FreeCAD"}
COMFORT_TRIANGLES = 60000
FINISH_TRIANGLES = 2500
# The face finder turns a 0.1 mm tessellation of this engine into 92 faces.
# A 1 percent grid erased the flutes and left a block.
SCREEN_TRIANGLES = 30000


def mesh_deflection(longest_mm):
    """Tessellation step that still keeps the flutes. About 0.1 mm on this engine."""
    longest = max(float(longest_mm), 1.0)
    return min(max(longest * 0.0005, 0.1), 0.5)


def coarser_deflection(current, triangle_count, limit=COMFORT_TRIANGLES):
    """Return a larger step when the mesh is still too dense, else None."""
    if triangle_count <= limit:
        return None
    return float(current) * 2


def _triangle_area(points):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = points
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    return (nx * nx + ny * ny + nz * nz) ** 0.5 * 0.5


def _cluster_facets(facets, origin, cell):
    """Merge vertices that share a grid cell, keeping their real position."""
    sums = {}
    counts = {}
    merged = []
    seen = set()
    for tri in facets:
        keys = []
        raw = []
        for point in tri:
            key = tuple(
                int((float(point[axis]) - origin[axis]) / cell) for axis in range(3)
            )
            if key in keys:
                continue
            keys.append(key)
            raw.append(tuple(float(point[axis]) for axis in range(3)))
        if len(raw) < 3 or _triangle_area(raw) <= 1e-6:
            continue
        identity = tuple(sorted(keys))
        if identity in seen:
            continue
        seen.add(identity)
        for key, point in zip(keys, raw):
            if key in sums:
                sums[key] = tuple(sums[key][axis] + point[axis] for axis in range(3))
                counts[key] += 1
            else:
                sums[key] = point
                counts[key] = 1
        merged.append(keys)
    placed = []
    for keys in merged:
        points = tuple(
            tuple(sums[key][axis] / counts[key] for axis in range(3)) for key in keys
        )
        if _triangle_area(points) <= 1e-6:
            continue
        placed.append(points)
    return placed


def reduce_facets(facets, limit=FINISH_TRIANGLES):
    """Merge a dense mesh, but never coarser than 2 percent of the part."""
    facets = list(facets)
    if len(facets) <= limit:
        return facets
    mins = [
        min(point[axis] for tri in facets for point in tri) for axis in range(3)
    ]
    maxs = [
        max(point[axis] for tri in facets for point in tri) for axis in range(3)
    ]
    longest = max(maxs[axis] - mins[axis] for axis in range(3))
    longest = max(longest, 1.0)
    max_cell = max(longest * 0.01, 0.5)
    cell = min(max(longest / (limit ** 0.5), 0.5), max_cell)
    reduced = facets
    for _ in range(8):
        reduced = _cluster_facets(facets, mins, cell)
        if len(reduced) <= limit or cell >= max_cell - 1e-9:
            return reduced
        cell = min(cell * 2, max_cell)
    return reduced


def screen_mesh(facets):
    """Pass the tessellation through. The converter groups these triangles into faces."""
    return list(facets)


def _facet_normal(tri):
    """Unit normal. A zero normal stops the converter from joining triangles into a face."""
    ax = float(tri[1][0]) - float(tri[0][0])
    ay = float(tri[1][1]) - float(tri[0][1])
    az = float(tri[1][2]) - float(tri[0][2])
    bx = float(tri[2][0]) - float(tri[0][0])
    by = float(tri[2][1]) - float(tri[0][1])
    bz = float(tri[2][2]) - float(tri[0][2])
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    length = (nx * nx + ny * ny + nz * nz) ** 0.5
    if length < 1e-12:
        return 0.0, 0.0, 0.0
    return nx / length, ny / length, nz / length


def write_stl(path, facets):
    """Write a binary STL from triangles of three (x, y, z) points."""
    facets = list(facets)
    with open(path, "wb") as handle:
        handle.write(b"\0" * 80)
        handle.write(struct.pack("<I", len(facets)))
        for tri in facets:
            flat = list(_facet_normal(tri))
            for point in tri:
                flat.extend(float(v) for v in point)
            handle.write(struct.pack("<12fH", *flat, 0))
    return path


def preview_sides(job, status):
    """Text for the left STL pane and the right conversion pane."""
    job = job or {}
    status = status or {}
    stl_name = job.get("stl_file") or "STL"
    triangles = (job.get("stl_geometry") or {}).get("triangles")
    left = stl_name if triangles is None else "%s\n%s triangles" % (stl_name, triangles)

    message = status.get("message") or ""
    state = status.get("state") or ""
    if job.get("has_step"):
        step_name = job.get("step_file") or "STEP"
        right = step_name if not message else "%s\n%s" % (step_name, message)
    elif state == "error":
        right = message or "Conversion failed"
    else:
        right = message or "Waiting"
        if status.get("pct") is not None:
            right = "%s\n%s%%" % (right, status.get("pct"))
    return left, right


def _request(url, data=None, headers=None, timeout=120):
    sent = dict(_CLIENT_HEADERS)
    if headers:
        sent.update(headers)
    req = urllib.request.Request(
        url,
        data=data,
        headers=sent,
        method="POST" if data is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        detail = raw
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and parsed.get("detail"):
                detail = parsed["detail"]
        except json.JSONDecodeError:
            pass
        raise RuntimeError(str(detail)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("Cannot reach the converter at %s" % url) from exc


def read_stl(path):
    """Triangles from an STL file. The file is not changed."""
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) >= 84:
        count = struct.unpack_from("<I", data, 80)[0]
        if count > 0 and 84 + count * 50 == len(data):
            facets = []
            for index in range(count):
                vals = struct.unpack_from("<12fH", data, 84 + index * 50)
                facets.append((vals[3:6], vals[6:9], vals[9:12]))
            return facets
    facets = []
    current = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0].lower() == "vertex":
            current.append(tuple(float(part) for part in parts[1:4]))
            if len(current) == 3:
                facets.append(tuple(current))
                current = []
    if not facets:
        raise RuntimeError("That file is not an STL.")
    return facets


def upload_stl(path, base=DEFAULT_BASE):
    filename = os.path.basename(path)
    boundary = "----stl2cadboundary"
    with open(path, "rb") as handle:
        payload = handle.read()
    head = (
        "--%s\r\n"
        'Content-Disposition: form-data; name="file"; filename="%s"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n" % (boundary, filename)
    ).encode()
    tail = ("\r\n--%s--\r\n" % boundary).encode()
    return _request(
        base.rstrip("/") + "/api/jobs/upload",
        data=head + payload + tail,
        headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary},
    )


def start_convert(job_id, base=DEFAULT_BASE, consider_extrusions=True):
    payload = json.dumps({"consider_extrusions": bool(consider_extrusions)}).encode()
    return _request(
        base.rstrip("/") + "/api/jobs/%s/convert" % job_id,
        data=payload,
        headers={"Content-Type": "application/json"},
    )


def read_status(job_id, base=DEFAULT_BASE):
    return _request(base.rstrip("/") + "/api/jobs/%s/process-status" % job_id)


def read_job(job_id, base=DEFAULT_BASE):
    return _request(base.rstrip("/") + "/api/jobs/%s" % job_id)


def save_step(job_id, dest_path, base=DEFAULT_BASE):
    """Write the converter's STEP to dest_path. This is not the website download."""
    job = read_job(job_id, base=base)
    name = (job or {}).get("step_file")
    if not (job or {}).get("has_step") or not name:
        raise RuntimeError("Convert first. Then Save writes the STEP.")
    url = "%s/api/jobs/%s/files/%s" % (
        base.rstrip("/"),
        urllib.parse.quote(str(job_id)),
        urllib.parse.quote(str(name)),
    )
    req = urllib.request.Request(url, headers=dict(_CLIENT_HEADERS))
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            payload = resp.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError("The STEP is not ready yet.") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("Cannot reach the converter at %s" % url) from exc
    if not payload.startswith(b"ISO-10303-21"):
        raise RuntimeError("The converter did not return a STEP file.")
    with open(dest_path, "wb") as handle:
        handle.write(payload)
    return dest_path


def read_step_preview(job_id, base=DEFAULT_BASE):
    """Mesh of the finished STEP. This is the picture, not the STEP file."""
    return _request(base.rstrip("/") + "/api/jobs/%s/saved-step-view" % job_id)


def step_preview_triangles(payload):
    """Triangles from a saved-step-view payload."""
    mesh = (payload or {}).get("face_mesh") or {}
    positions = mesh.get("positions") or []
    indices = mesh.get("indices") or []
    triangles = []
    for start in range(0, len(indices) - 2, 3):
        points = []
        for index in indices[start:start + 3]:
            base = int(index) * 3
            points.append((positions[base], positions[base + 1], positions[base + 2]))
        triangles.append(tuple(points))
    return triangles


def status_line(status, has_picture=False):
    """One plain sentence for the panel."""
    status = status or {}
    state = status.get("state") or ""
    message = status.get("message") or ""
    if state == "error":
        return message or "Conversion failed."
    if has_picture:
        return "Complete. Drag a picture to turn it. Scroll to zoom."
    if state == "done":
        return "Complete. Loading the picture."
    if message:
        return "Working. " + message
    return "Press Convert to use the model on screen, or Load STL to use a file."


def view_triangles(triangles, yaw, pitch, zoom, width, height):
    """Project triangles onto the panel. Each item is three (x, y) points."""
    if not triangles or width < 2 or height < 2:
        return []
    points = [point for tri in triangles for point in tri]
    center = [
        (min(point[axis] for point in points) + max(point[axis] for point in points)) / 2
        for axis in range(3)
    ]
    span = max(
        max(point[axis] for point in points) - min(point[axis] for point in points)
        for axis in range(3)
    ) or 1.0
    scale = min(width, height) * 0.75 / span * float(zoom)
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
    cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)
    painted = []
    for tri in triangles:
        screen = []
        depth = 0.0
        for point in tri:
            x = float(point[0]) - center[0]
            y = float(point[1]) - center[1]
            z = float(point[2]) - center[2]
            x, z = x * cos_yaw - z * sin_yaw, x * sin_yaw + z * cos_yaw
            y, z = y * cos_pitch - z * sin_pitch, y * sin_pitch + z * cos_pitch
            screen.append((width / 2 + x * scale, height / 2 - y * scale))
            depth += z
        painted.append((depth, screen))
    painted.sort(key=lambda item: item[0])
    return [screen for _depth, screen in painted]


def render_view(triangles, yaw, pitch, zoom, width, height):
    """Shade of the nearest face at each pixel. Zero is empty background."""
    width = int(width)
    height = int(height)
    if not triangles or width < 2 or height < 2:
        return bytearray()
    points = [point for tri in triangles for point in tri]
    center = [
        (min(point[axis] for point in points) + max(point[axis] for point in points)) / 2
        for axis in range(3)
    ]
    span = max(
        max(point[axis] for point in points) - min(point[axis] for point in points)
        for axis in range(3)
    ) or 1.0
    scale = min(width, height) * 0.75 / span * float(zoom)
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
    cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)

    def camera(point):
        x = float(point[0]) - center[0]
        y = float(point[1]) - center[1]
        z = float(point[2]) - center[2]
        x, y = x * cos_yaw - y * sin_yaw, x * sin_yaw + y * cos_yaw
        y, z = y * cos_pitch - z * sin_pitch, y * sin_pitch + z * cos_pitch
        return x, y, z

    shades = bytearray(width * height)
    depths = [-1e30] * (width * height)
    for tri in triangles:
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = [camera(point) for point in tri]
        ux, uy, uz = x1 - x0, y1 - y0, z1 - z0
        vx, vy, vz = x2 - x0, y2 - y0, z2 - z0
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        length = (nx * nx + ny * ny + nz * nz) ** 0.5 or 1.0
        light = abs(nx * 0.55 + ny * 0.2 + nz * 0.75) / length
        shade = max(1, int(70 + 170 * min(light, 1.0)))
        sx0, sy0 = width / 2 + x0 * scale, height / 2 - z0 * scale
        sx1, sy1 = width / 2 + x1 * scale, height / 2 - z1 * scale
        sx2, sy2 = width / 2 + x2 * scale, height / 2 - z2 * scale
        minx = max(int(min(sx0, sx1, sx2)), 0)
        maxx = min(int(max(sx0, sx1, sx2)) + 1, width)
        miny = max(int(min(sy0, sy1, sy2)), 0)
        maxy = min(int(max(sy0, sy1, sy2)) + 1, height)
        den = (sy1 - sy2) * (sx0 - sx2) + (sx2 - sx1) * (sy0 - sy2)
        if maxx <= minx or maxy <= miny or den == 0:
            for sx, sy, sz in ((sx0, sy0, y0), (sx1, sy1, y1), (sx2, sy2, y2)):
                ix, iy = int(sx), int(sy)
                if 0 <= ix < width and 0 <= iy < height and sz > depths[iy * width + ix]:
                    depths[iy * width + ix] = sz
                    shades[iy * width + ix] = shade
            continue
        for py in range(miny, maxy):
            fy = py + 0.5
            row = py * width
            for px in range(minx, maxx):
                fx = px + 0.5
                w0 = ((sy1 - sy2) * (fx - sx2) + (sx2 - sx1) * (fy - sy2)) / den
                w1 = ((sy2 - sy0) * (fx - sx2) + (sx0 - sx2) * (fy - sy2)) / den
                w2 = 1.0 - w0 - w1
                if w0 < 0 or w1 < 0 or w2 < 0:
                    continue
                slot = row + px
                view_z = w0 * y0 + w1 * y1 + w2 * y2
                if view_z > depths[slot]:
                    depths[slot] = view_z
                    shades[slot] = shade
    return shades
