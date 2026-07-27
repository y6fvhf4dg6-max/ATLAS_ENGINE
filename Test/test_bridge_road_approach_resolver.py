import pytest

from CORE.atlas_bridge_road_approach_resolver import (
    AtlasBridgeRoadApproachResolver,
)


def test_resolver_finds_two_transverse_bridge_end_edges():
    deck_top = (
        (0.0, -3.0, 1.60),
        (10.0, -3.0, 1.80),
        (20.0, -3.0, 1.60),
        (20.0, 3.0, 1.60),
        (10.0, 3.0, 1.80),
        (0.0, 3.0, 1.60),
    )

    approaches = AtlasBridgeRoadApproachResolver.resolve(
        deck_top
    )

    assert len(approaches) == 2

    first, second = approaches

    assert first["start_edge"] == (
        (0.0, 3.0),
        (0.0, -3.0),
    )
    assert first["outward_axis"] == pytest.approx(
        (-1.0, 0.0)
    )
    assert first["bridge_top_z"] == pytest.approx(
        1.60
    )

    assert second["start_edge"] == (
        (20.0, -3.0),
        (20.0, 3.0),
    )
    assert second["outward_axis"] == pytest.approx(
        (1.0, 0.0)
    )
    assert second["bridge_top_z"] == pytest.approx(
        1.60
    )


def test_resolver_handles_diagonal_bridge_axis():
    deck_top = (
        (-1.0, 1.0, 1.60),
        (9.0, 11.0, 1.80),
        (11.0, 9.0, 1.80),
        (1.0, -1.0, 1.60),
    )

    approaches = AtlasBridgeRoadApproachResolver.resolve(
        deck_top
    )

    assert len(approaches) == 2

    axis_lengths = [
        (
            approach["outward_axis"][0] ** 2
            + approach["outward_axis"][1] ** 2
        ) ** 0.5
        for approach in approaches
    ]

    assert axis_lengths == pytest.approx(
        [1.0, 1.0]
    )

    dot = (
        approaches[0]["outward_axis"][0]
        * approaches[1]["outward_axis"][0]
        + approaches[0]["outward_axis"][1]
        * approaches[1]["outward_axis"][1]
    )

    assert dot == pytest.approx(-1.0)


@pytest.mark.parametrize(
    "deck_top",
    (
        (),
        ((0.0, 0.0, 1.0),),
        (
            (0.0, 0.0, 1.0),
            (1.0, 0.0, 1.0),
        ),
    ),
)
def test_resolver_rejects_insufficient_deck_geometry(
    deck_top,
):
    with pytest.raises(ValueError):
        AtlasBridgeRoadApproachResolver.resolve(
            deck_top
        )


def test_resolver_merges_adjacent_transverse_segments_at_bridge_end():
    deck_top = (
        (0.0, -3.0, 1.60),
        (20.0, -3.0, 1.60),
        (20.0, -1.0, 1.60),
        (20.0, 1.0, 1.60),
        (20.0, 3.0, 1.60),
        (0.0, 3.0, 1.60),
    )

    approaches = AtlasBridgeRoadApproachResolver.resolve(
        deck_top
    )

    assert len(approaches) == 2

    right = max(
        approaches,
        key=lambda approach: (
            approach["start_edge"][0][0]
            + approach["start_edge"][1][0]
        ),
    )

    assert right["start_edge"] == (
        (20.0, -3.0),
        (20.0, 3.0),
    )
