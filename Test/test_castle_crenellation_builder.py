"""
ATLAS Castle Crenellation Builder Regression Tests

Sur üstünde ölçeğe duyarlı, baskıya uygun mazgal dişleri
üretilmesini doğrular.
"""

from CORE.atlas_castle_crenellation_builder import (
    AtlasCastleCrenellationBuilder,
)


def test_straight_wall_generates_repeating_crenellations():
    mesh = AtlasCastleCrenellationBuilder.build_crenellations(
        start_left=(0.0, 1.0, 10.0),
        start_right=(0.0, -1.0, 10.0),
        end_left=(20.0, 1.0, 10.0),
        end_right=(20.0, -1.0, 10.0),
        tooth_width_mm=2.0,
        gap_width_mm=2.0,
        tooth_height_mm=1.2,
    )

    assert mesh is not None
    assert mesh["type"] == "castle_wall_crenellations"
    assert mesh["tooth_count"] == 5
    assert len(mesh["triangles"]) == 60


def test_short_wall_skips_unprintable_crenellations():
    mesh = AtlasCastleCrenellationBuilder.build_crenellations(
        start_left=(0.0, 1.0, 10.0),
        start_right=(0.0, -1.0, 10.0),
        end_left=(2.5, 1.0, 10.0),
        end_right=(2.5, -1.0, 10.0),
        tooth_width_mm=2.0,
        gap_width_mm=2.0,
        tooth_height_mm=1.2,
    )

    assert mesh is None


def test_crenellation_mesh_is_closed():
    mesh = AtlasCastleCrenellationBuilder.build_crenellations(
        start_left=(0.0, 1.0, 10.0),
        start_right=(0.0, -1.0, 10.0),
        end_left=(12.0, 1.0, 10.0),
        end_right=(12.0, -1.0, 10.0),
        tooth_width_mm=2.0,
        gap_width_mm=2.0,
        tooth_height_mm=1.2,
    )

    assert mesh is not None

    edge_counts = {}

    for triangle in mesh["triangles"]:
        for index in range(3):
            first = triangle[index]
            second = triangle[(index + 1) % 3]
            edge = tuple(sorted((first, second)))
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

    assert all(count == 2 for count in edge_counts.values())


def test_crenellation_mesh_passes_shared_validator():
    from CORE.atlas_mesh_validator import AtlasMeshValidator

    mesh = AtlasCastleCrenellationBuilder.build_crenellations(
        start_left=(0.0, 1.0, 10.0),
        start_right=(0.0, -1.0, 10.0),
        end_left=(12.0, 1.0, 10.0),
        end_right=(12.0, -1.0, 10.0),
        tooth_width_mm=2.0,
        gap_width_mm=2.0,
        tooth_height_mm=1.2,
    )

    report = AtlasMeshValidator.report(mesh)

    assert report["valid"] is True
    assert report["structure_valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_wall_builder_creates_crenellations_from_wall_mesh():
    from CORE.atlas_castle_wall_builder import AtlasCastleWallBuilder

    wall_mesh = {
        "top": [
            (0.0, 1.0, 10.0),
            (12.0, 1.0, 10.0),
            (24.0, 1.0, 10.0),
            (0.0, -1.0, 10.0),
            (12.0, -1.0, 10.0),
            (24.0, -1.0, 10.0),
        ],
        "left_points": [
            (0.0, 1.0),
            (12.0, 1.0),
            (24.0, 1.0),
        ],
        "right_points": [
            (0.0, -1.0),
            (12.0, -1.0),
            (24.0, -1.0),
        ],
        "closed": False,
    }

    meshes = AtlasCastleWallBuilder._build_crenellation_meshes(
        wall_mesh=wall_mesh,
    )

    assert len(meshes) == 2
    assert all(
        mesh["type"] == "castle_wall_crenellations"
        for mesh in meshes
    )
    assert sum(mesh["tooth_count"] for mesh in meshes) > 0
