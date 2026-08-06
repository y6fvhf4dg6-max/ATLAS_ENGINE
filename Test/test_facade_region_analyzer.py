from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)


def test_explicit_building_levels_create_ordered_floor_regions():
    analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "4",
        },
        total_height_m=14.0,
    )

    assert analysis.level_count == 4
    assert analysis.min_z == 0.0
    assert analysis.max_z == 14.0

    assert tuple(
        (
            band.level_index,
            band.region_name,
            band.min_z,
            band.max_z,
        )
        for band in analysis.floor_bands
    ) == (
        (0, "ground_floor", 0.0, 3.5),
        (1, "upper_floor", 3.5, 7.0),
        (2, "upper_floor", 7.0, 10.5),
        (3, "top_floor", 10.5, 14.0),
    )


def test_height_without_levels_uses_default_floor_height():
    analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={},
        total_height_m=10.0,
    )

    assert analysis.level_count == 3

    assert tuple(
        band.region_name
        for band in analysis.floor_bands
    ) == (
        "ground_floor",
        "upper_floor",
        "top_floor",
    )

    assert analysis.floor_bands[0].min_z == 0.0
    assert analysis.floor_bands[-1].max_z == 10.0


def test_single_level_facade_is_ground_and_top_region():
    analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "1",
        },
        total_height_m=3.5,
    )

    assert analysis.level_count == 1
    assert len(analysis.floor_bands) == 1
    assert (
        analysis.floor_bands[0].region_name
        == "ground_top_floor"
    )


def test_elevated_facade_regions_preserve_min_z():
    analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "2",
        },
        total_height_m=7.0,
        min_z=4.0,
    )

    assert analysis.min_z == 4.0
    assert analysis.max_z == 11.0

    assert tuple(
        (
            band.min_z,
            band.max_z,
        )
        for band in analysis.floor_bands
    ) == (
        (4.0, 7.5),
        (7.5, 11.0),
    )


def test_invalid_explicit_levels_fall_back_to_height_analysis():
    for levels in (
        "0",
        "-2",
        "invalid",
        None,
    ):
        analysis = AtlasFacadeRegionAnalyzer.analyze(
            tags={
                "building:levels": levels,
            },
            total_height_m=10.0,
        )

        assert analysis.level_count == 3


def test_floor_bands_cover_facade_without_gaps_or_overlap():
    analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "5",
        },
        total_height_m=17.0,
        min_z=2.0,
    )

    assert (
        analysis.floor_bands[0].min_z
        == analysis.min_z
    )
    assert (
        analysis.floor_bands[-1].max_z
        == analysis.max_z
    )

    assert all(
        current.max_z == following.min_z
        for current, following in zip(
            analysis.floor_bands,
            analysis.floor_bands[1:],
        )
    )

