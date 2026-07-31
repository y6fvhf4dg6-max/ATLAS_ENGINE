import math

import pytest

from CORE.atlas_building_pyramidal_roof_builder import (
    AtlasBuildingPyramidalRoofBuilder,
)


class _CoordinateEngine:
    scale_ratio = 3000.0


def _square_tower_mesh():
    bottom = [
        (0.0, 0.0, 2.0),
        (6.0, 0.0, 2.0),
        (6.0, 6.0, 2.0),
        (0.0, 6.0, 2.0),
    ]

    top = [
        (0.0, 0.0, 16.0),
        (6.0, 0.0, 16.0),
        (6.0, 6.0, 16.0),
        (0.0, 6.0, 16.0),
    ]

    triangles = [
        # Alt kapak
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        # Düz üst kapak
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
        # Duvarlar
        (bottom[0], bottom[1], top[1]),
        (bottom[0], top[1], top[0]),
        (bottom[1], bottom[2], top[2]),
        (bottom[1], top[2], top[1]),
        (bottom[2], bottom[3], top[3]),
        (bottom[2], top[3], top[2]),
        (bottom[3], bottom[0], top[0]),
        (bottom[3], top[0], top[3]),
    ]

    return {
        "bottom": bottom,
        "top": top,
        "triangles": triangles,
        "bottom_z": 2.0,
        "top_z": 16.0,
        "building_roof_profile": "pyramidal",
        "is_castle_building": False,
    }


def test_pyramidal_roof_replaces_flat_top_with_apex_faces():
    mesh = _square_tower_mesh()

    result = AtlasBuildingPyramidalRoofBuilder.apply(
        mesh=mesh,
        roof_height_m="40",
        coordinate_engine=_CoordinateEngine(),
    )

    assert result["building_pyramidal_roof_applied"] is True
    assert result["roof_geometry"] == "pyramidal"

    assert result["body_top_z"] == pytest.approx(16.0)
    assert result["roof_height_mm"] == pytest.approx(
        40_000.0 / 3000.0
    )
    assert result["roof_top_z"] == pytest.approx(
        16.0 + 40_000.0 / 3000.0
    )
    assert result["top_z"] == result["roof_top_z"]

    assert (
        result["building_pyramidal_removed_top_triangles"]
        == 2
    )
    assert len(
        result["building_pyramidal_roof_triangles"]
    ) == 4

    # 12 başlangıç - 2 düz kapak + 4 çatı yüzü
    assert len(result["triangles"]) == 14


def test_pyramidal_roof_apex_is_centered_over_tower():
    result = AtlasBuildingPyramidalRoofBuilder.apply(
        mesh=_square_tower_mesh(),
        roof_height_m="40",
        coordinate_engine=_CoordinateEngine(),
    )

    apex = result["roof_apex"]

    assert math.isclose(apex[0], 3.0)
    assert math.isclose(apex[1], 3.0)
    assert apex[2] == pytest.approx(
        16.0 + 40_000.0 / 3000.0
    )


def test_non_pyramidal_profile_is_unchanged():
    mesh = _square_tower_mesh()
    mesh["building_roof_profile"] = "flat"

    original_triangles = list(mesh["triangles"])

    result = AtlasBuildingPyramidalRoofBuilder.apply(
        mesh=mesh,
        roof_height_m="40",
        coordinate_engine=_CoordinateEngine(),
    )

    assert result is mesh
    assert result["triangles"] == original_triangles
    assert "building_pyramidal_roof_applied" not in result
