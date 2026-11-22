"""Preview renderer smoke test."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from freecad.stl2cad import client


def test_render_view_small():
    tri = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
    shades = client.render_view([tri], 0.0, 0.0, 1.0, 32, 32)
    assert len(shades) == 32 * 32