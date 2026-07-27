from copy import deepcopy

from CORE.atlas_building_gable_roof_builder import (
    AtlasBuildingGableRoofBuilder,
)
from CORE.atlas_mesh_validator import AtlasMeshValidator


def build_rectangular_building_mesh():
    bottom = [
        (0.0, 0.0, 0.0),
        (8.0, 0.0, 0.0),
        (8.0, 3.0, 0.0),
        (0.0, 3.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 4.0),
        (8.0, 0.0, 4.0),
        (8.0, 3.0, 4.0),
        (0.0, 3.0, 4.0),
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

    walls = [
        (
            bottom[0],
            bottom[1],
            top[1],
            top[0],
        ),
        (
            bottom[1],
            bottom[2],
            top[2],
            top[1],
        ),
        (
            bottom[2],
            bottom[3],
            top[3],
            top[2],
        ),
        (
            bottom[3],
            bottom[0],
            top[0],
            top[3],
        ),
    ]

    return {
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": [
            *bottom_triangles,
            *top_triangles,
            *wall_triangles,
        ],
        "bottom_z": 0.0,
        "top_z": 4.0,
        "building_roof_profile": "gable",
    }


def test_gable_roof_is_applied_and_remains_manifold():
    mesh = build_rectangular_building_mesh()
    original_triangles = list(mesh["triangles"])

    before_report = AtlasMeshValidator.report(mesh)

    assert before_report["open_edge_count"] == 0
    assert before_report["non_manifold_edge_count"] == 0

    result = AtlasBuildingGableRoofBuilder.apply(mesh)

    assert result["building_gable_roof_applied"] is True
    assert result["roof_geometry"] == "gable"

    assert result["body_top_z"] == 4.0
    assert result["roof_top_z"] > 4.0
    assert result["top_z"] == result["roof_top_z"]

    assert len(result["building_gable_roof_triangles"]) == 8
    assert result["triangles"][: len(original_triangles)] == original_triangles

    ridge_start = result["roof_ridge_start"]
    ridge_end = result["roof_ridge_end"]

    ridge_dx = abs(ridge_end[0] - ridge_start[0])
    ridge_dy = abs(ridge_end[1] - ridge_start[1])

    assert ridge_dx > ridge_dy
    assert ridge_dx > 7.5

    after_report = AtlasMeshValidator.report(result)

    assert after_report["open_edge_count"] == 0
    assert after_report["non_manifold_edge_count"] == 0
    assert after_report["valid"] is True


def test_non_gable_profile_is_unchanged():
    mesh = build_rectangular_building_mesh()
    mesh["building_roof_profile"] = "flat"

    before = deepcopy(mesh)

    result = AtlasBuildingGableRoofBuilder.apply(mesh)

    assert result == before
    assert "building_gable_roof_applied" not in result


def build_rotated_rectangular_building_mesh():
    bottom = [
        (0.0, 0.0, 0.0),
        (6.0, 6.0, 0.0),
        (4.0, 8.0, 0.0),
        (-2.0, 2.0, 0.0),
    ]

    top = [
        (x, y, 4.0)
        for x, y, _ in bottom
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

    walls = [
        (
            bottom[0],
            bottom[1],
            top[1],
            top[0],
        ),
        (
            bottom[1],
            bottom[2],
            top[2],
            top[1],
        ),
        (
            bottom[2],
            bottom[3],
            top[3],
            top[2],
        ),
        (
            bottom[3],
            bottom[0],
            top[0],
            top[3],
        ),
    ]

    return {
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": [
            *bottom_triangles,
            *top_triangles,
            *wall_triangles,
        ],
        "bottom_z": 0.0,
        "top_z": 4.0,
        "building_roof_profile": "gable",
    }


def test_rotated_gable_ridge_follows_long_building_axis():
    mesh = build_rotated_rectangular_building_mesh()

    result = AtlasBuildingGableRoofBuilder.apply(mesh)

    assert result["building_gable_roof_applied"] is True

    ridge_start = result["roof_ridge_start"]
    ridge_end = result["roof_ridge_end"]

    ridge_dx = abs(
        ridge_end[0] - ridge_start[0]
    )
    ridge_dy = abs(
        ridge_end[1] - ridge_start[1]
    )

    assert ridge_dx > 5.5
    assert ridge_dy > 5.5
    assert abs(ridge_dx - ridge_dy) < 1e-9

    report = AtlasMeshValidator.report(result)

    assert report["structure_valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
    assert report["valid"] is True


def test_gable_roof_derives_z_levels_from_real_mesh_points():
    bottom = [
        (0.0, 0.0, 1.25),
        (8.0, 0.0, 1.25),
        (8.0, 3.0, 1.25),
        (0.0, 3.0, 1.25),
    ]

    top = [
        (0.0, 0.0, 5.25),
        (8.0, 0.0, 5.25),
        (8.0, 3.0, 5.25),
        (0.0, 3.0, 5.25),
    ]

    mesh = {
        "bottom": bottom,
        "top": top,
        "walls": [
            (bottom[0], bottom[1], top[1], top[0]),
            (bottom[1], bottom[2], top[2], top[1]),
            (bottom[2], bottom[3], top[3], top[2]),
            (bottom[3], bottom[0], top[0], top[3]),
        ],
        "triangles": [
            (bottom[0], bottom[2], bottom[1]),
            (bottom[0], bottom[3], bottom[2]),
            (top[0], top[1], top[2]),
            (top[0], top[2], top[3]),
            (bottom[0], bottom[1], top[1]),
            (bottom[0], top[1], top[0]),
            (bottom[1], bottom[2], top[2]),
            (bottom[1], top[2], top[1]),
            (bottom[2], bottom[3], top[3]),
            (bottom[2], top[3], top[2]),
            (bottom[3], bottom[0], top[0]),
            (bottom[3], top[0], top[3]),
        ],
        "foundation_z": 1.25,
        "building_roof_profile": "gable",
    }

    result = AtlasBuildingGableRoofBuilder.apply(mesh)

    assert result["building_gable_roof_applied"] is True
    assert result["body_top_z"] == 5.25
    assert result["roof_top_z"] > 5.25
    assert result["top_z"] == result["roof_top_z"]
    assert len(result["building_gable_roof_triangles"]) == 8
    assert len(result["triangles"]) == 20


def test_general_gable_roof_does_not_modify_castle_mesh():
    mesh = build_rectangular_building_mesh()
    mesh["is_castle_building"] = True

    original_triangles = list(mesh["triangles"])
    original_top_z = mesh.get("top_z")

    result = AtlasBuildingGableRoofBuilder.apply(mesh)

    assert result is mesh
    assert result["triangles"] == original_triangles
    assert result.get("top_z") == original_top_z
    assert "building_gable_roof_applied" not in result
    assert "roof_geometry" not in result



def test_gable_roof_updates_semantic_surface_metadata():
    mesh = build_rectangular_building_mesh()

    flat_roof_triangles = list(mesh["triangles"][2:4])
    wall_triangles = list(mesh["triangles"][4:12])

    mesh["building_flat_roof_triangles"] = (
        flat_roof_triangles
    )
    mesh["building_roof_triangles"] = (
        flat_roof_triangles
    )
    mesh["building_wall_triangles"] = wall_triangles

    result = AtlasBuildingGableRoofBuilder.apply(mesh)

    assert result["building_flat_roof_triangles"] == []
    assert result["building_roof_triangles"] == (
        result["building_gable_roof_triangles"]
    )
    assert result["building_wall_triangles"] == wall_triangles
