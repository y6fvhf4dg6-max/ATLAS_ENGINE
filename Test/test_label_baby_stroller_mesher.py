import pytest

from CORE.atlas_label_baby_stroller_mesher import (
    AtlasLabelBabyStrollerMesher,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


def test_baby_stroller_builds_printable_closed_geometry():
    mesh = AtlasLabelBabyStrollerMesher.build(
        width_mm=9.0,
        height_mm=7.0,
        depth_mm=0.6,
    )

    assert mesh["type"] == "label_baby_stroller"
    assert mesh["width_mm"] == 9.0
    assert mesh["height_mm"] == 7.0
    assert mesh["depth_mm"] == 0.6
    assert mesh["triangles"]

    topology = AtlasMeshValidator._topology_report(mesh)

    assert topology["open_edge_count"] == 0
    assert topology["non_manifold_edge_count"] == 0

    vertices = [
        point
        for triangle in mesh["triangles"]
        for point in triangle
    ]

    width = (
        max(x for x, _, _ in vertices)
        - min(x for x, _, _ in vertices)
    )
    height = (
        max(y for _, y, _ in vertices)
        - min(y for _, y, _ in vertices)
    )

    assert width <= 9.0 + 1e-6
    assert height <= 7.0 + 1e-6


def test_baby_stroller_rejects_non_positive_dimensions():
    for field_name in (
        "width_mm",
        "height_mm",
        "depth_mm",
    ):
        values = {
            "width_mm": 9.0,
            "height_mm": 7.0,
            "depth_mm": 0.6,
        }
        values[field_name] = 0.0

        with pytest.raises(ValueError):
            AtlasLabelBabyStrollerMesher.build(**values)
