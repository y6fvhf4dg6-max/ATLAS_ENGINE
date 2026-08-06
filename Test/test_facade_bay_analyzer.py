from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)


def _three_floor_analysis():
    return AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "3",
        },
        total_height_m=10.5,
    )


def test_uniform_bays_are_created_for_every_floor_band():
    analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=_three_floor_analysis(),
        bay_count=4,
    )

    assert analysis.bay_count == 4
    assert analysis.level_count == 3
    assert len(analysis.bays) == 12

    first_floor = analysis.bays_for_level(0)

    assert tuple(
        (
            bay.bay_index,
            bay.u_min,
            bay.u_max,
        )
        for bay in first_floor
    ) == (
        (0, 0.0, 0.25),
        (1, 0.25, 0.5),
        (2, 0.5, 0.75),
        (3, 0.75, 1.0),
    )


def test_bays_preserve_floor_region_and_vertical_bounds():
    analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=_three_floor_analysis(),
        bay_count=2,
    )

    top_bays = analysis.bays_for_level(2)

    assert len(top_bays) == 2

    assert all(
        bay.region_name == "top_floor"
        for bay in top_bays
    )
    assert all(
        bay.min_z == 7.0
        and bay.max_z == 10.5
        for bay in top_bays
    )


def test_bay_grid_covers_facade_without_horizontal_gaps():
    analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=_three_floor_analysis(),
        bay_count=5,
    )

    for level_index in range(
        analysis.level_count
    ):
        bays = analysis.bays_for_level(
            level_index
        )

        assert bays[0].u_min == 0.0
        assert bays[-1].u_max == 1.0

        assert all(
            current.u_max == following.u_min
            for current, following in zip(
                bays,
                bays[1:],
            )
        )


def test_invalid_bay_counts_are_rejected():
    region_analysis = _three_floor_analysis()

    for bay_count in (
        0,
        -1,
        1.5,
        True,
    ):
        try:
            AtlasFacadeBayAnalyzer.analyze(
                region_analysis=region_analysis,
                bay_count=bay_count,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"bay_count={bay_count!r} was accepted"
            )


def test_region_analysis_type_is_required():
    try:
        AtlasFacadeBayAnalyzer.analyze(
            region_analysis={},
            bay_count=3,
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "invalid region_analysis was accepted"
        )


def test_level_queries_reject_out_of_range_indices():
    analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=_three_floor_analysis(),
        bay_count=3,
    )

    for level_index in (
        -1,
        3,
        True,
    ):
        try:
            analysis.bays_for_level(
                level_index
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"level_index={level_index!r} was accepted"
            )


def test_bay_identities_are_unique_and_ordered():
    analysis = AtlasFacadeBayAnalyzer.analyze(
        region_analysis=_three_floor_analysis(),
        bay_count=3,
    )

    identities = tuple(
        (
            bay.level_index,
            bay.bay_index,
        )
        for bay in analysis.bays
    )

    assert identities == (
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    )

