from collections import Counter

import pytest

from CORE.atlas_wall_collection_tiered_corner_support_mesher import (
    AtlasWallCollectionTieredCornerSupportMesher,
)
from CORE.atlas_wall_collection_tiered_corner_support_spec import (
    AtlasWallCollectionTieredCornerSupportSpec,
)


def _edge_key(first, second):
    first = tuple(round(float(value), 6) for value in first)
    second = tuple(round(float(value), 6) for value in second)
    return tuple(sorted((first, second)))


def _assert_closed_manifold(mesh):
    edge_counts = Counter()

    for first, second, third in mesh["triangles"]:
        edge_counts[_edge_key(first, second)] += 1
        edge_counts[_edge_key(second, third)] += 1
        edge_counts[_edge_key(third, first)] += 1

    assert edge_counts
    assert all(count == 2 for count in edge_counts.values())


@pytest.fixture
def bonn_spec():
    return AtlasWallCollectionTieredCornerSupportSpec.for_scene(
        frame_width_mm=10.0,
        frame_depth_mm=6.0,
        scene_max_height_mm=29.0286,
    )


def test_mesher_builds_four_oriented_corner_supports(bonn_spec):
    meshes = AtlasWallCollectionTieredCornerSupportMesher.build_set(
        spec=bonn_spec,
        product_width_mm=170.0,
        product_height_mm=170.0,
    )

    assert tuple(meshes) == (
        "lower_left",
        "lower_right",
        "upper_right",
        "upper_left",
    )

    for corner, mesh in meshes.items():
        assert mesh["type"] == "wall_collection_tiered_corner_support"
        assert mesh["corner"] == corner
        assert mesh["frame_contact_width_mm"] == pytest.approx(8.0)
        assert mesh["next_plate_base_z_mm"] == pytest.approx(31.2)
        assert mesh["total_height_mm"] == pytest.approx(37.6)
        _assert_closed_manifold(mesh)


def test_support_set_registers_only_at_product_corners(bonn_spec):
    meshes = AtlasWallCollectionTieredCornerSupportMesher.build_set(
        spec=bonn_spec,
        product_width_mm=170.0,
        product_height_mm=170.0,
    )

    expected_anchors = {
        "lower_left": (-85.0, -85.0),
        "lower_right": (85.0, -85.0),
        "upper_right": (85.0, 85.0),
        "upper_left": (-85.0, 85.0),
    }

    for corner, mesh in meshes.items():
        assert mesh["product_corner_anchor_mm"] == pytest.approx(
            expected_anchors[corner]
        )
        vertices = [
            point
            for triangle in mesh["triangles"]
            for point in triangle
        ]
        assert min(point[2] for point in vertices) == pytest.approx(0.0)
        assert max(point[2] for point in vertices) == pytest.approx(37.6)


def test_mesher_is_deterministic_and_does_not_modify_spec(bonn_spec):
    first = AtlasWallCollectionTieredCornerSupportMesher.build_set(
        spec=bonn_spec,
        product_width_mm=170.0,
        product_height_mm=170.0,
    )
    second = AtlasWallCollectionTieredCornerSupportMesher.build_set(
        spec=bonn_spec,
        product_width_mm=170.0,
        product_height_mm=170.0,
    )

    assert first == second
    assert bonn_spec.scene_max_height_mm == pytest.approx(29.0286)



@pytest.mark.parametrize("capacity_mm", (25.0, 50.0))
def test_mesher_builds_one_universal_stackable_corner_support(
    capacity_mm,
):
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_module(
        product_capacity_mm=capacity_mm,
    )

    mesh = (
        AtlasWallCollectionTieredCornerSupportMesher
        .build_universal_support(spec=spec)
    )

    assert mesh["type"] == (
        "wall_collection_universal_tiered_corner_support"
    )
    assert mesh["product_capacity_mm"] == pytest.approx(
        capacity_mm
    )
    assert mesh["bottom_connector"] == "female"
    assert mesh["top_connector"] == "male"
    assert mesh["triangles"]
    _assert_closed_manifold(mesh)


def test_universal_support_geometry_is_independent_of_product_xy_size():
    spec = AtlasWallCollectionTieredCornerSupportSpec.for_module(
        product_capacity_mm=25.0,
    )

    mesh = (
        AtlasWallCollectionTieredCornerSupportMesher
        .build_universal_support(spec=spec)
    )

    assert "product_width_mm" not in mesh
    assert "product_height_mm" not in mesh
    assert mesh["frame_contact_width_mm"] == pytest.approx(8.0)
