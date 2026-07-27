import pytest

from CORE.atlas_bridge_road_approach_target_resolver import (
    AtlasBridgeRoadApproachTargetResolver,
)


def test_target_resolver_preserves_bridge_end_width():
    road_meshes = (
        {
            "triangles": (
                (
                    (1.0, -3.0, 0.8),
                    (3.0, -3.0, 0.8),
                    (3.0, 0.0, 0.8),
                ),
                (
                    (1.0, -3.0, 0.8),
                    (3.0, 0.0, 0.8),
                    (1.0, 0.0, 0.8),
                ),
            ),
        },
        {
            "triangles": (
                (
                    (1.0, 0.0, 0.8),
                    (3.0, 0.0, 0.8),
                    (3.0, 3.0, 0.8),
                ),
                (
                    (1.0, 0.0, 0.8),
                    (3.0, 3.0, 0.8),
                    (1.0, 3.0, 0.8),
                ),
            ),
        },
    )

    target = AtlasBridgeRoadApproachTargetResolver.resolve(
        start_edge=(
            (0.0, -3.0),
            (0.0, 3.0),
        ),
        outward_axis=(1.0, 0.0),
        road_meshes=road_meshes,
    )

    first, second = target["target_edge"]

    assert first == pytest.approx(
        (1.0, -3.0)
    )
    assert second == pytest.approx(
        (1.0, 3.0)
    )
    assert target["length_mm"] == pytest.approx(
        1.0
    )
    assert target["road_top_z"] == pytest.approx(
        0.8
    )


def test_target_resolver_uses_aggregated_fragmented_road_corridor():
    road_meshes = (
        {
            "triangles": (
                (
                    (0.8, -4.0, 0.8),
                    (2.0, -4.0, 0.8),
                    (2.0, -0.2, 0.8),
                ),
            ),
        },
        {
            "triangles": (
                (
                    (0.8, 0.2, 0.8),
                    (2.0, 0.2, 0.8),
                    (2.0, 4.0, 0.8),
                ),
            ),
        },
    )

    target = AtlasBridgeRoadApproachTargetResolver.resolve(
        start_edge=(
            (0.0, -3.0),
            (0.0, 3.0),
        ),
        outward_axis=(1.0, 0.0),
        road_meshes=road_meshes,
    )

    first, second = target["target_edge"]

    assert first[0] == pytest.approx(0.8)
    assert second[0] == pytest.approx(0.8)
    assert second[1] - first[1] == pytest.approx(
        6.0
    )


def test_target_resolver_rejects_empty_road_meshes():
    with pytest.raises(ValueError):
        AtlasBridgeRoadApproachTargetResolver.resolve(
            start_edge=(
                (0.0, -3.0),
                (0.0, 3.0),
            ),
            outward_axis=(1.0, 0.0),
            road_meshes=(),
        )
