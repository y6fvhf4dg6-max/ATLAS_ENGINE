import pytest

from CORE.atlas_galata_bridge_support_mesher import (
    AtlasGalataBridgeSupportMesher,
)


def _supports():
    return (
        {
            "side": "positive",
            "center": (10.0, 5.0),
            "longitudinal_position": 0.38,
            "lateral_offset": 7.5,
            "support_width": 2.0,
            "support_depth": 3.0,
        },
        {
            "side": "negative",
            "center": (10.0, -5.0),
            "longitudinal_position": 0.39,
            "lateral_offset": -7.5,
            "support_width": 2.0,
            "support_depth": 3.0,
        },
        {
            "side": "positive",
            "center": (20.0, 5.0),
            "longitudinal_position": 0.59,
            "lateral_offset": 7.5,
            "support_width": 2.0,
            "support_depth": 3.0,
        },
        {
            "side": "negative",
            "center": (20.0, -5.0),
            "longitudinal_position": 0.60,
            "lateral_offset": -7.5,
            "support_width": 2.0,
            "support_depth": 3.0,
        },
    )


def test_support_mesher_builds_four_closed_supports():
    meshes = AtlasGalataBridgeSupportMesher.build(
        supports=_supports(),
        axis=(1.0, 0.0),
        base_z=0.80,
        top_z=1.40,
    )

    assert len(meshes) == 4

    for mesh in meshes:
        assert len(mesh["bottom"]) == 4
        assert len(mesh["top"]) == 4
        assert len(mesh["triangles"]) == 12


def test_support_mesher_uses_requested_vertical_extent():
    meshes = AtlasGalataBridgeSupportMesher.build(
        supports=_supports(),
        axis=(1.0, 0.0),
        base_z=0.80,
        top_z=1.40,
    )

    for mesh in meshes:
        assert {
            point[2]
            for point in mesh["bottom"]
        } == {0.80}

        assert {
            point[2]
            for point in mesh["top"]
        } == {1.40}


def test_support_mesher_preserves_support_centers():
    meshes = AtlasGalataBridgeSupportMesher.build(
        supports=_supports(),
        axis=(1.0, 0.0),
        base_z=0.80,
        top_z=1.40,
    )

    expected_centers = [
        support["center"]
        for support in _supports()
    ]

    resolved_centers = []

    for mesh in meshes:
        xs = [point[0] for point in mesh["bottom"]]
        ys = [point[1] for point in mesh["bottom"]]

        resolved_centers.append(
            (
                sum(xs) / len(xs),
                sum(ys) / len(ys),
            )
        )

    assert resolved_centers == pytest.approx(
        expected_centers
    )


def test_support_mesher_follows_diagonal_bridge_axis():
    meshes = AtlasGalataBridgeSupportMesher.build(
        supports=(_supports()[0],),
        axis=(1.0, 1.0),
        base_z=0.80,
        top_z=1.40,
    )

    bottom = meshes[0]["bottom"]

    longitudinal_edge = (
        bottom[1][0] - bottom[0][0],
        bottom[1][1] - bottom[0][1],
    )

    assert longitudinal_edge[0] > 0.0
    assert longitudinal_edge[1] > 0.0
    assert abs(
        longitudinal_edge[0]
        - longitudinal_edge[1]
    ) < 1e-12


def test_support_mesher_rejects_invalid_vertical_extent():
    with pytest.raises(ValueError):
        AtlasGalataBridgeSupportMesher.build(
            supports=_supports(),
            axis=(1.0, 0.0),
            base_z=1.40,
            top_z=0.80,
        )
