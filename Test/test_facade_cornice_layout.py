from CORE.atlas_facade_cornice_layout import (
    AtlasFacadeCorniceLayout,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)


def _four_floor_analysis():
    return AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "4",
        },
        total_height_m=14.0,
    )


def test_cornices_are_created_on_internal_floor_boundaries():
    layout = AtlasFacadeCorniceLayout.create(
        region_analysis=_four_floor_analysis(),
    )

    assert layout.cornice_count == 3

    assert tuple(
        (
            cornice.cornice_index,
            cornice.boundary_level_index,
            cornice.z,
            cornice.u_min,
            cornice.u_max,
        )
        for cornice in layout.cornices
    ) == (
        (0, 1, 3.5, 0.0, 1.0),
        (1, 2, 7.0, 0.0, 1.0),
        (2, 3, 10.5, 0.0, 1.0),
    )


def test_top_cornice_can_be_included_explicitly():
    layout = AtlasFacadeCorniceLayout.create(
        region_analysis=_four_floor_analysis(),
        include_top_cornice=True,
    )

    assert layout.cornice_count == 4

    top = layout.cornices[-1]

    assert top.cornice_kind == "top_cornice"
    assert top.boundary_level_index == 4
    assert top.z == 14.0


def test_single_floor_facade_has_no_internal_cornice():
    region_analysis = AtlasFacadeRegionAnalyzer.analyze(
        tags={
            "building:levels": "1",
        },
        total_height_m=3.5,
    )

    layout = AtlasFacadeCorniceLayout.create(
        region_analysis=region_analysis,
    )

    assert layout.cornice_count == 0
    assert layout.cornices == ()
