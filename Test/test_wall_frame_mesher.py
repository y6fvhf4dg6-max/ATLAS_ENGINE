import pytest

from CORE.atlas_wall_frame_mesher import AtlasWallFrameMesher
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


def _all_vertices(mesh):
    return [
        vertex
        for triangle in mesh["triangles"]
        for vertex in triangle
    ]


def test_default_wall_frame_mesher_builds_closed_rectangular_ring():
    spec = AtlasWallFrameSpec()

    mesh = AtlasWallFrameMesher.build(
        spec=spec,
        depth_mm=6.0,
    )

    assert mesh["type"] == "wall_frame"
    assert mesh["outer_width_mm"] == pytest.approx(150.0)
    assert mesh["outer_height_mm"] == pytest.approx(150.0)
    assert mesh["inner_width_mm"] == pytest.approx(134.0)
    assert mesh["inner_height_mm"] == pytest.approx(134.0)
    assert mesh["depth_mm"] == pytest.approx(6.0)
    assert len(mesh["triangles"]) == 32

    vertices = _all_vertices(mesh)

    assert min(x for x, _, _ in vertices) == pytest.approx(-75.0)
    assert max(x for x, _, _ in vertices) == pytest.approx(75.0)
    assert min(y for _, y, _ in vertices) == pytest.approx(-75.0)
    assert max(y for _, y, _ in vertices) == pytest.approx(75.0)
    assert min(z for _, _, z in vertices) == pytest.approx(0.0)
    assert max(z for _, _, z in vertices) == pytest.approx(6.0)


def test_wall_frame_mesher_preserves_center_opening():
    spec = AtlasWallFrameSpec()

    mesh = AtlasWallFrameMesher.build(
        spec=spec,
        depth_mm=6.0,
    )

    vertices = _all_vertices(mesh)

    inner_x = spec.inner_width_mm / 2.0
    inner_y = spec.inner_height_mm / 2.0

    assert any(
        abs(abs(x) - inner_x) < 1e-9
        and abs(abs(y) - inner_y) < 1e-9
        for x, y, _ in vertices
    )


def test_wall_frame_mesher_rejects_non_positive_depth():
    with pytest.raises(ValueError):
        AtlasWallFrameMesher.build(
            spec=AtlasWallFrameSpec(),
            depth_mm=0.0,
        )
