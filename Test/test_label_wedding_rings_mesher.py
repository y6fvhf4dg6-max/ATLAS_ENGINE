import pytest

from CORE.atlas_label_wedding_rings_mesher import (
    AtlasLabelWeddingRingsMesher,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


def test_wedding_rings_build_printable_closed_geometry():
    mesh = AtlasLabelWeddingRingsMesher.build(
        width_mm=8.0,
        height_mm=6.0,
        depth_mm=0.6,
    )

    assert mesh["type"] == "label_wedding_rings"
    assert mesh["width_mm"] == 8.0
    assert mesh["height_mm"] == 6.0
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

    assert min(x for x, _, _ in vertices) == pytest.approx(
        -4.0,
        abs=0.05,
    )
    assert max(x for x, _, _ in vertices) == pytest.approx(
        4.0,
        abs=0.05,
    )

    assert (
        max(y for _, y, _ in vertices)
        - min(y for _, y, _ in vertices)
    ) <= 6.0 + 1e-6


def test_wedding_rings_reject_non_positive_dimensions():
    for field_name in (
        "width_mm",
        "height_mm",
        "depth_mm",
    ):
        values = {
            "width_mm": 8.0,
            "height_mm": 6.0,
            "depth_mm": 0.6,
        }
        values[field_name] = 0.0

        with pytest.raises(ValueError):
            AtlasLabelWeddingRingsMesher.build(**values)
