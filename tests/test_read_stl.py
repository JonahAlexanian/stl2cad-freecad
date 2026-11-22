"""STL reader tests (no FreeCAD)."""
from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from freecad.stl2cad import client  # noqa: E402


def _one_triangle_binary(extra_tail=b""):
    header = b"\0" * 80
    facet = struct.pack(
        "<12fH",
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0,
    )
    return header + struct.pack("<I", 1) + facet + extra_tail


def test_padded_binary_stl():
    payload = _one_triangle_binary(b"PAD")
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as handle:
        path = handle.name
        handle.write(payload)
    facets = client.read_stl(path)
    assert len(facets) == 1


def test_sanitize_upload_filename():
    assert client._sanitize_upload_filename('bad"\r\nname.stl') == "badname.stl"

