import pytest
import math

from CORE.atlas_liedberg_muehlenturm_ruin_top_builder import (
    AtlasLiedbergMuehlenturmRuinTopBuilder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


def make_muehlenturm_mesh():
    return {
        "landmark_id": 143975860,
        "type": "tower",
        "profile": "generic",
        "top": [
            (10.0, 0.0, 20.0),
            (7.1, 7.1, 20.0),
            (0.0, 10.0, 20.0),
            (-7.1, 7.1, 20.0),
            (-10.0, 0.0, 20.0),
            (-7.1, -7.1, 20.0),
            (0.0, -10.0, 20.0),
            (7.1, -7.1, 20.0),
        ],
        "bottom": [
            (10.0, 0.0, 1.0),
            (7.1, 7.1, 1.0),
            (0.0, 10.0, 1.0),
            (-7.1, 7.1, 1.0),
            (-10.0, 0.0, 1.0),
            (-7.1, -7.1, 1.0),
            (0.0, -10.0, 1.0),
            (7.1, -7.1, 1.0),
        ],
    }


def radial_extent(points):
    center_x = sum(point[0] for point in points) / len(points)
    center_y = sum(point[1] for point in points) / len(points)

    return max(
        math.hypot(
            point[0] - center_x,
            point[1] - center_y,
        )
        for point in points
    )


def test_muehlenturm_receives_irregular_ruin_top_and_larger_body():
    original = make_muehlenturm_mesh()
    original_radius = radial_extent(original["top"])

    result = AtlasLiedbergMuehlenturmRuinTopBuilder.apply(
        tower_mesh=original,
    )

    assert result["muehlenturm_ruin_top_applied"] is True
    assert result["muehlenturm_body_scaled"] is True
    assert result["architectural_role"] == "muehlenturm_ruin_body"
    assert result["radius_scale"] == 1.12
    assert result["muehlenturm_open_top"] is True
    assert result["muehlenturm_top_cap_triangles"] == []
    assert result["muehlenturm_hollow_body"] is True
    assert result["wall_thickness_mm"] == 0.35

    topology = AtlasMeshValidator._topology_report(result)

    assert topology["open_edge_count"] == 0
    assert topology["non_manifold_edge_count"] == 0

    top_z_values = {
        round(point[2], 6)
        for point in result["top"]
    }

    assert len(top_z_values) >= 3
    assert max(top_z_values) - min(top_z_values) >= 0.20
    assert max(top_z_values) - min(top_z_values) <= 0.30

    enlarged_radius = radial_extent(result["top"])

    assert enlarged_radius > original_radius
    assert enlarged_radius == pytest.approx(
        original_radius * 1.12,
        rel=1e-3,
    )

    assert len(result["triangles"]) > 0


def test_unrelated_tower_remains_unchanged():
    mesh = make_muehlenturm_mesh()
    mesh["landmark_id"] = 999

    result = AtlasLiedbergMuehlenturmRuinTopBuilder.apply(
        tower_mesh=mesh,
    )

    assert result is mesh
    assert "muehlenturm_ruin_top_applied" not in result
    assert "muehlenturm_body_scaled" not in result
