import pytest

from CORE.atlas_building_skillion_roof_builder import (
    AtlasBuildingSkillionRoofBuilder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


class DummyCoordinateEngine:
    scale_ratio = 3000.0

    @staticmethod
    def height_to_stl_mm(height_m):
        return float(height_m) * 1000.0 / 3000.0


def build_rectangular_skillion_mesh():
    bottom = [
        (0.0, 0.0, 0.0),
        (8.0, 0.0, 0.0),
        (8.0, 4.0, 0.0),
        (0.0, 4.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 5.0),
        (8.0, 0.0, 5.0),
        (8.0, 4.0, 5.0),
        (0.0, 4.0, 5.0),
    ]

    bottom_triangles = [
        (bottom[0], bottom[2], bottom[1]),
        (bottom[0], bottom[3], bottom[2]),
    ]

    top_triangles = [
        (top[0], top[1], top[2]),
        (top[0], top[2], top[3]),
    ]

    wall_triangles = [
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
        "triangles": [
            *bottom_triangles,
            *top_triangles,
            *wall_triangles,
        ],
        "bottom_z": 0.0,
        "top_z": 5.0,
        "building_roof_profile": "skillion",
        "is_castle_building": False,
    }


def test_skillion_roof_uses_osm_height_and_south_direction():
    mesh = build_rectangular_skillion_mesh()

    result = AtlasBuildingSkillionRoofBuilder.apply(
        mesh=mesh,
        roof_height_m="4",
        roof_direction="south",
        coordinate_engine=DummyCoordinateEngine(),
    )

    expected_roof_height_mm = 4_000.0 / 3000.0

    assert result["building_skillion_roof_applied"] is True
    assert result["roof_geometry"] == "skillion"
    assert result["body_top_z"] == pytest.approx(5.0)
    assert result["roof_height_mm"] == pytest.approx(
        expected_roof_height_mm
    )
    assert result["roof_top_z"] == pytest.approx(
        5.0 + expected_roof_height_mm
    )
    assert result["top_z"] == pytest.approx(
        5.0 + expected_roof_height_mm
    )
    assert result["roof_direction"] == "south"

    south_z_values = [
        point[2]
        for point in result["building_skillion_roof_points"]
        if point[1] == pytest.approx(0.0)
    ]
    north_z_values = [
        point[2]
        for point in result["building_skillion_roof_points"]
        if point[1] == pytest.approx(4.0)
    ]

    assert south_z_values
    assert north_z_values
    assert min(south_z_values) > max(north_z_values)

    report = AtlasMeshValidator.report(result)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
    assert report["valid"] is True
