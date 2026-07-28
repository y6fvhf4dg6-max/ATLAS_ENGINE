import pytest

from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_wall_frame_hanger_mesher import (
    AtlasWallFrameHangerMesher,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec


def _all_vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def test_150mm_frame_contains_single_hidden_keyhole_recess():
    frame_spec = AtlasWallFrameSpec()
    hanger_spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=150.0,
        outer_height_mm=150.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    mesh = AtlasWallFrameHangerMesher.build(
        frame_spec=frame_spec,
        hanger_spec=hanger_spec,
        frame_depth_mm=6.0,
    )

    assert mesh["type"] == "wall_frame_with_hidden_hangers"
    assert mesh["hanger_count"] == 1
    assert mesh["hanger_center_x_positions_mm"] == pytest.approx((0.0,))
    assert mesh["recess_depth_mm"] == pytest.approx(3.0)
    assert mesh["front_wall_thickness_mm"] == pytest.approx(3.0)

    vertices = _all_vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-75.0)
    assert max(x for x, _, _ in vertices) == pytest.approx(75.0)
    assert min(y for _, y, _ in vertices) == pytest.approx(-75.0)
    assert max(y for _, y, _ in vertices) == pytest.approx(75.0)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(6.0)

    assert any(
        z == pytest.approx(3.0)
        and abs(x) <= hanger_spec.head_diameter_mm / 2.0 + 1e-6
        and y >= frame_spec.inner_height_mm / 2.0
        for x, y, z in vertices
    )


def test_260mm_frame_contains_center_and_two_side_hangers():
    frame_spec = AtlasWallFrameSpec(
        outer_width_mm=260.0,
        outer_height_mm=260.0,
        frame_width_mm=8.0,
    )
    hanger_spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=260.0,
        outer_height_mm=260.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    mesh = AtlasWallFrameHangerMesher.build(
        frame_spec=frame_spec,
        hanger_spec=hanger_spec,
        frame_depth_mm=6.0,
    )

    assert mesh["hanger_count"] == 3
    assert mesh["hanger_center_x_positions_mm"] == pytest.approx(
        (-65.0, 0.0, 65.0)
    )


def test_wall_frame_with_hidden_hangers_is_closed_and_manifold():
    frame_spec = AtlasWallFrameSpec()
    hanger_spec = AtlasWallHangerSpec.for_product_size(
        outer_width_mm=150.0,
        outer_height_mm=150.0,
        frame_width_mm=8.0,
        frame_depth_mm=6.0,
    )

    mesh = AtlasWallFrameHangerMesher.build(
        frame_spec=frame_spec,
        hanger_spec=hanger_spec,
        frame_depth_mm=6.0,
    )

    topology = AtlasMeshValidator._topology_report(mesh)

    assert topology["open_edge_count"] == 0
    assert topology["non_manifold_edge_count"] == 0
