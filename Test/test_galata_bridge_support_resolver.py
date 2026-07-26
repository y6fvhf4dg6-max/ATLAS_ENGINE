import pytest

from CORE.atlas_galata_bridge_support_resolver import (
    AtlasGalataBridgeSupportResolver,
)


def _galata_like_footprint():
    return (
        (0.0, -3.0),
        (28.0, -3.0),
        (30.0, -7.0),
        (34.0, -8.0),
        (38.0, -7.0),
        (40.0, -3.0),
        (48.0, -3.0),
        (50.0, -7.0),
        (54.0, -8.0),
        (58.0, -7.0),
        (60.0, -3.0),
        (80.0, -3.0),
        (80.0, 3.0),
        (60.0, 3.0),
        (58.0, 7.0),
        (54.0, 8.0),
        (50.0, 7.0),
        (48.0, 3.0),
        (40.0, 3.0),
        (38.0, 7.0),
        (34.0, 8.0),
        (30.0, 7.0),
        (28.0, 3.0),
        (0.0, 3.0),
    )


def test_resolver_finds_four_galata_support_regions():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    assert len(supports) == 4


def test_resolver_returns_two_supports_on_each_side():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    positive = [
        support
        for support in supports
        if support["side"] == "positive"
    ]
    negative = [
        support
        for support in supports
        if support["side"] == "negative"
    ]

    assert len(positive) == 2
    assert len(negative) == 2


def test_resolver_orders_supports_along_bridge_axis():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    positions = [
        support["longitudinal_position"]
        for support in supports
    ]

    assert positions == sorted(positions)


def test_resolver_detects_expected_longitudinal_clusters():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    clustered_positions = sorted(
        {
            round(
                support["longitudinal_position"],
                2,
            )
            for support in supports
        }
    )

    assert clustered_positions == pytest.approx(
        [0.43, 0.68],
        abs=0.05,
    )


def test_resolver_support_centers_are_outside_main_deck_width():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    for support in supports:
        assert abs(
            support["lateral_offset"]
        ) >= 6.0


def test_resolver_returns_printable_support_dimensions():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    for support in supports:
        assert support["support_width"] >= 2.0
        assert support["support_depth"] >= 3.0


def test_resolver_rejects_invalid_footprint():
    with pytest.raises(ValueError):
        AtlasGalataBridgeSupportResolver.resolve(
            footprint=((0.0, 0.0), (1.0, 1.0)),
        )


def test_resolver_insets_support_centers_toward_bridge_centerline():
    supports = AtlasGalataBridgeSupportResolver.resolve(
        footprint=_galata_like_footprint(),
    )

    lateral_offsets = sorted(
        abs(support["lateral_offset"])
        for support in supports
    )

    assert lateral_offsets == pytest.approx(
        [6.0, 6.0, 6.0, 6.0]
    )
