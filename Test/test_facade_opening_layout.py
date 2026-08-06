from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_opening_layout import (
    AtlasFacadeOpeningLayout,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)


def _two_by_three_bay_analysis():
    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "2",
        },
        total_height_m=7.0,
    )

    return AtlasFacadeBayAnalyzer.analyze(
        region_analysis=region_analysis,
        bay_count=3,
    )


def test_one_centered_opening_is_created_for_each_bay():
    layout = AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=_two_by_three_bay_analysis(),
        opening_kind="window",
        horizontal_margin_ratio=0.20,
        vertical_margin_ratio=0.25,
    )

    assert layout.opening_count == 6
    assert len(layout.openings) == 6

    first = layout.openings[0]

    assert first.level_index == 0
    assert first.bay_index == 0
    assert first.opening_index == 0
    assert first.opening_kind == "window"
    assert first.region_name == "ground_floor"
    assert first.u_min == 0.20
    assert first.u_max == 0.80
    assert first.v_min == 0.25
    assert first.v_max == 0.75


def test_openings_can_be_queried_by_level_and_bay():
    layout = AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=_two_by_three_bay_analysis(),
        opening_kind="window",
    )

    openings = layout.openings_for_bay(
        level_index=1,
        bay_index=2,
    )

    assert len(openings) == 1
    assert openings[0].level_index == 1
    assert openings[0].bay_index == 2
    assert openings[0].region_name == "top_floor"


def test_uniform_opening_identities_are_unique_and_ordered():
    layout = AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=_two_by_three_bay_analysis(),
        opening_kind="generic_opening",
    )

    assert tuple(
        (
            opening.level_index,
            opening.bay_index,
            opening.opening_index,
        )
        for opening in layout.openings
    ) == (
        (0, 0, 0),
        (0, 1, 0),
        (0, 2, 0),
        (1, 0, 0),
        (1, 1, 0),
        (1, 2, 0),
    )


def test_invalid_opening_margins_are_rejected():
    bay_analysis = _two_by_three_bay_analysis()

    for field_name, value in (
        ("horizontal_margin_ratio", -0.01),
        ("horizontal_margin_ratio", 0.50),
        ("vertical_margin_ratio", -0.01),
        ("vertical_margin_ratio", 0.50),
    ):
        arguments = {
            "bay_analysis": bay_analysis,
            "opening_kind": "window",
            field_name: value,
        }

        try:
            AtlasFacadeOpeningLayout.create_uniform(
                **arguments
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"{field_name}={value!r} was accepted"
            )


def test_bay_analysis_type_is_required():
    try:
        AtlasFacadeOpeningLayout.create_uniform(
            bay_analysis={},
            opening_kind="window",
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "invalid bay_analysis was accepted"
        )


def test_blank_opening_kind_is_rejected():
    try:
        AtlasFacadeOpeningLayout.create_uniform(
            bay_analysis=_two_by_three_bay_analysis(),
            opening_kind="   ",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "blank opening_kind was accepted"
        )


def test_opening_kind_is_normalized():
    layout = AtlasFacadeOpeningLayout.create_uniform(
        bay_analysis=_two_by_three_bay_analysis(),
        opening_kind="  Generic Opening  ",
    )

    assert all(
        opening.opening_kind
        == "generic_opening"
        for opening in layout.openings
    )

