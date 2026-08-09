import pytest

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_semantic_surface_texture_mesher import (
    AtlasSemanticSurfaceTextureMesher,
)
from CORE.atlas_semantic_surface_texture_pattern import (
    AtlasSemanticSurfaceTexturePattern,
)


def _paving_pattern():
    return AtlasSemanticSurfaceTexturePattern(
        texture_language="paving",
        relief_depth_mm=0.14,
        feature_pitch_mm=1.80,
    )


def _build_square():
    return AtlasSemanticSurfaceTextureMesher.build(
        boundary_points=(
            (0.0, 0.0),
            (12.0, 0.0),
            (12.0, 12.0),
            (0.0, 12.0),
        ),
        bottom_z=1.0,
        surface_z=1.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )


def test_semantic_surface_adds_interior_vertices():
    result = _build_square()

    assert len(result["top"]) > 4
    assert result["surface_texture_enabled"] is True
    assert result["surface_vertex_count"] == len(
        result["top"]
    )


def test_semantic_surface_boundary_stays_at_nominal_height():
    result = _build_square()

    boundary_z_values = {
        round(point[2], 9)
        for point in result["boundary_top"]
    }

    assert boundary_z_values == {1.30}


def test_semantic_surface_interior_contains_emboss():
    result = _build_square()

    interior_z_values = {
        round(point[2], 6)
        for point in result["interior_top"]
    }

    assert interior_z_values
    assert min(interior_z_values) >= 1.30
    assert max(interior_z_values) > 1.30
    assert max(interior_z_values) <= (
        1.30 + 0.14 + 1e-6
    )


def test_semantic_surface_preserves_flat_bottom():
    result = _build_square()

    assert {
        round(point[2], 9)
        for point in result["bottom"]
    } == {1.0}


def test_semantic_surface_is_closed_and_manifold():
    result = _build_square()

    report = AtlasMeshValidator.report(
        result
    )

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_dense_surface_structure_uses_boundary_vertex_count_for_walls():
    result = _build_square()

    assert len(result["top"]) > len(result["boundary_top"])
    assert len(result["walls"]) == len(result["boundary_top"])

    report = AtlasMeshValidator._structure_report(
        result
    )

    assert report["structure_valid"] is True
    assert report["walls"] == len(result["boundary_top"])


def _sloped_terrain():
    return {
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (20.0, 0.0, 2.0),
            ],
            [
                (0.0, 20.0, 2.0),
                (20.0, 20.0, 3.0),
            ],
        ],
        "metadata": {
            "size_x_mm": 20.0,
            "size_y_mm": 20.0,
            "size_mm": 20.0,
        },
    }


def test_semantic_surface_can_follow_real_terrain_height():
    result = AtlasSemanticSurfaceTextureMesher.build_terrain_following(
        boundary_points=(
            (2.0, 2.0),
            (18.0, 2.0),
            (18.0, 18.0),
            (2.0, 18.0),
        ),
        terrain_mesh=_sloped_terrain(),
        foundation_height_mm=0.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )

    bottom_z_values = {
        round(point[2], 6)
        for point in result["bottom"]
    }

    assert len(bottom_z_values) > 2

    for bottom, top in zip(
        result["bottom"],
        result["top"],
    ):
        assert top[2] >= (
            bottom[2] + 0.30 - 1e-9
        )
        assert top[2] <= (
            bottom[2] + 0.30 + 0.14 + 1e-9
        )


def test_terrain_following_boundary_keeps_nominal_foundation_height():
    result = AtlasSemanticSurfaceTextureMesher.build_terrain_following(
        boundary_points=(
            (2.0, 2.0),
            (18.0, 2.0),
            (18.0, 18.0),
            (2.0, 18.0),
        ),
        terrain_mesh=_sloped_terrain(),
        foundation_height_mm=0.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )

    bottom_by_xy = {
        (
            round(point[0], 9),
            round(point[1], 9),
        ): point[2]
        for point in result["bottom"]
    }

    for top in result["boundary_top"]:
        key = (
            round(top[0], 9),
            round(top[1], 9),
        )

        assert (
            top[2] - bottom_by_xy[key]
            == pytest.approx(
                0.30,
                abs=1e-9,
            )
        )


def test_terrain_following_semantic_surface_remains_closed_and_manifold():
    result = AtlasSemanticSurfaceTextureMesher.build_terrain_following(
        boundary_points=(
            (2.0, 2.0),
            (18.0, 2.0),
            (18.0, 18.0),
            (2.0, 18.0),
        ),
        terrain_mesh=_sloped_terrain(),
        foundation_height_mm=0.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )

    report = AtlasMeshValidator.report(
        result
    )

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_semantic_surface_concave_boundary_remains_closed_and_manifold():
    result = AtlasSemanticSurfaceTextureMesher.build(
        boundary_points=(
            (0.0, 0.0),
            (12.0, 0.0),
            (12.0, 12.0),
            (8.0, 12.0),
            (8.0, 4.0),
            (4.0, 4.0),
            (4.0, 12.0),
            (0.0, 12.0),
        ),
        bottom_z=1.0,
        surface_z=1.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )

    report = AtlasMeshValidator.report(result)

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_real_koeln_boundary_fixture_remains_closed_and_manifold():
    result = AtlasSemanticSurfaceTextureMesher.build(
        boundary_points=(
            (122.63728054088443, 79.33526800009815),
            (123.37332399760301, 79.3615799999742),
            (123.60421457935121, 79.5660040000621),
            (123.58252872360856, 80.98988800001933),
            (123.5608428678659, 82.41377199997657),
            (122.23545439032593, 82.36317200010433),
            (122.34260803047371, 80.88767600004729),
            (122.44976167062151, 79.41217999999026),
        ),
        bottom_z=1.0,
        surface_z=1.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )

    report = AtlasMeshValidator.report(result)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0

def test_real_koeln_predense_boundary_preserves_wall_perimeter():
    result = AtlasSemanticSurfaceTextureMesher.build(
        boundary_points=(
            (122.63728054088443, 79.33526800009815),
            (123.37332399760301, 79.3615799999742),
            (123.60421457935121, 79.5660040000621),
            (123.5608428678659, 82.41377199997657),
            (122.23545439032593, 82.36317200010433),
            (122.44976167062151, 79.41217999999026),
        ),
        bottom_z=1.0,
        surface_z=1.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=1.80,
    )

    report = AtlasMeshValidator.report(result)

    assert report["valid"] is True
    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0

def test_semantic_surface_limits_long_interior_edges():
    import math

    pitch = 1.80

    result = AtlasSemanticSurfaceTextureMesher.build(
        boundary_points=(
            (0.0, 0.0),
            (12.0, 0.0),
            (12.0, 12.0),
            (0.0, 12.0),
        ),
        bottom_z=1.0,
        surface_z=1.30,
        pattern=_paving_pattern(),
        maximum_edge_length_mm=pitch,
    )

    triangles = list(result["triangles"])
    wall_triangle_count = len(result["walls"]) * 2
    surface_triangle_count = (
        len(triangles) - wall_triangle_count
    ) // 2

    top_triangles = triangles[:surface_triangle_count]

    boundary = result["boundary_top"]

    def key2(point):
        return (
            round(float(point[0]), 9),
            round(float(point[1]), 9),
        )

    def edge_key(first, second):
        return tuple(
            sorted(
                (
                    key2(first),
                    key2(second),
                )
            )
        )

    boundary_edges = {
        edge_key(
            boundary[index],
            boundary[(index + 1) % len(boundary)],
        )
        for index in range(len(boundary))
    }

    long_interior_edges = set()

    for triangle in top_triangles:
        for first, second in (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        ):
            edge = edge_key(first, second)

            if edge in boundary_edges:
                continue

            length = math.hypot(
                float(second[0]) - float(first[0]),
                float(second[1]) - float(first[1]),
            )

            if length > pitch * 2.0:
                long_interior_edges.add(edge)

    assert long_interior_edges == set()
