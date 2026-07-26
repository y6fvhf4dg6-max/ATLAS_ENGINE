import pytest

from CORE.atlas_bridge_segmented_deck_builder import (
    AtlasBridgeSegmentedDeckBuilder,
)


def polygon_area(points):
    return abs(
        sum(
            x1 * y2 - x2 * y1
            for (x1, y1), (x2, y2) in zip(
                points,
                points[1:] + points[:1],
            )
        )
    ) / 2.0


def test_segmented_deck_splits_rectangular_bridge_into_three_sections():
    footprint = (
        (0.0, -3.0),
        (20.0, -3.0),
        (20.0, 3.0),
        (0.0, 3.0),
    )

    sections = AtlasBridgeSegmentedDeckBuilder.split(
        footprint=footprint,
        approach_ratio=0.20,
    )

    assert len(sections) == 3

    assert sections[0]["kind"] == "start_approach"
    assert sections[1]["kind"] == "main_deck"
    assert sections[2]["kind"] == "end_approach"


def test_segmented_deck_sections_preserve_total_footprint_area():
    footprint = (
        (0.0, -3.0),
        (20.0, -3.0),
        (20.0, 3.0),
        (0.0, 3.0),
    )

    sections = AtlasBridgeSegmentedDeckBuilder.split(
        footprint=footprint,
        approach_ratio=0.20,
    )

    section_area = sum(
        polygon_area(list(section["footprint"]))
        for section in sections
    )

    assert section_area == pytest.approx(
        polygon_area(list(footprint))
    )


def test_segmented_deck_uses_requested_approach_ratio():
    footprint = (
        (0.0, -3.0),
        (20.0, -3.0),
        (20.0, 3.0),
        (0.0, 3.0),
    )

    sections = AtlasBridgeSegmentedDeckBuilder.split(
        footprint=footprint,
        approach_ratio=0.20,
    )

    bounds = [
        section["longitudinal_bounds"]
        for section in sections
    ]

    assert bounds == [
        pytest.approx((0.0, 0.20)),
        pytest.approx((0.20, 0.80)),
        pytest.approx((0.80, 1.0)),
    ]


def test_segmented_deck_preserves_concave_footprint_area():
    footprint = (
        (0.0, 0.0),
        (12.0, 0.0),
        (12.0, 6.0),
        (8.0, 6.0),
        (8.0, 3.0),
        (4.0, 3.0),
        (4.0, 6.0),
        (0.0, 6.0),
    )

    sections = AtlasBridgeSegmentedDeckBuilder.split(
        footprint=footprint,
        approach_ratio=0.25,
    )

    section_area = sum(
        polygon_area(list(section["footprint"]))
        for section in sections
    )

    assert len(sections) == 3
    assert section_area == pytest.approx(
        polygon_area(list(footprint))
    )


@pytest.mark.parametrize(
    "approach_ratio",
    (0.0, -0.1, 0.5, 0.7),
)
def test_segmented_deck_rejects_invalid_approach_ratios(
    approach_ratio,
):
    with pytest.raises(ValueError):
        AtlasBridgeSegmentedDeckBuilder.split(
            footprint=(
                (0.0, 0.0),
                (10.0, 0.0),
                (10.0, 4.0),
                (0.0, 4.0),
            ),
            approach_ratio=approach_ratio,
        )
