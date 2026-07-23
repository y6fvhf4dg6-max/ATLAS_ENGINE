import math

from CORE.atlas_building_hipped_roof_builder import (
    AtlasBuildingHippedRoofBuilder,
)


def _rectangular_mesh():
    bottom = [
        (0.0, 0.0, 1.0),
        (8.0, 0.0, 1.0),
        (8.0, 5.0, 1.0),
        (0.0, 5.0, 1.0),
    ]

    top = [
        (0.0, 0.0, 5.0),
        (8.0, 0.0, 5.0),
        (8.0, 5.0, 5.0),
        (0.0, 5.0, 5.0),
    ]

    triangles = [
        # Alt kapak
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
        # Üst kapak
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
        "walls": [
            (bottom[0], bottom[1], top[1], top[0]),
            (bottom[1], bottom[2], top[2], top[1]),
            (bottom[2], bottom[3], top[3], top[2]),
            (bottom[3], bottom[0], top[0], top[3]),
        ],
        "triangles": triangles,
        "foundation_z": 1.0,
        "building_roof_profile": "hipped",
    }


def test_hipped_roof_replaces_flat_top_with_four_slopes():
    mesh = _rectangular_mesh()
    original_triangles = list(mesh["triangles"])

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    assert result["building_hipped_roof_applied"] is True
    assert result["roof_geometry"] == "hipped"

    assert result["body_top_z"] == 5.0
    assert result["roof_top_z"] > 5.0
    assert result["top_z"] == result["roof_top_z"]

    assert result["building_hipped_removed_top_triangles"] == 2
    assert len(result["building_hipped_roof_triangles"]) == 4

    # 12 başlangıç - 2 düz üst kapak + 4 eğimli yüz
    assert len(result["triangles"]) == 14

    for top_triangle in original_triangles[2:4]:
        assert top_triangle not in result["triangles"]


def test_hipped_roof_apex_is_centered_over_footprint():
    mesh = _rectangular_mesh()

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    apex = result["roof_apex"]

    assert math.isclose(apex[0], 4.0)
    assert math.isclose(apex[1], 2.5)
    assert apex[2] > 5.0


def test_non_hipped_profile_is_unchanged():
    mesh = _rectangular_mesh()
    mesh["building_roof_profile"] = "flat"

    original_triangles = list(mesh["triangles"])

    result = AtlasBuildingHippedRoofBuilder.apply(mesh)

    assert result is mesh
    assert result["triangles"] == original_triangles
    assert "building_hipped_roof_applied" not in result
