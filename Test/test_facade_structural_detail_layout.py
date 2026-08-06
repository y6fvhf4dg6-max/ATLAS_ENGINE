from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalyzer,
)
from CORE.atlas_facade_region_analyzer import (
    AtlasFacadeRegionAnalyzer,
)
from CORE.atlas_facade_structural_detail_layout import (
    AtlasFacadeStructuralDetailLayout,
)
from CORE.atlas_physical_detail_resolver import (
    AtlasPhysicalDetailResolver,
)


def _three_bay_analysis():
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


def test_columns_are_placed_on_unique_bay_boundaries():
    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=1.20,
        scale_ratio=3000.0,
        nozzle_diameter_mm=0.4,
        detail_type="column",
    )

    layout = AtlasFacadeStructuralDetailLayout.create(
        bay_analysis=_three_bay_analysis(),
        detail_kind="column",
        physical_decision=decision,
    )

    assert layout.detail_kind == "column"
    assert layout.detail_count == 4

    assert tuple(
        detail.u_center
        for detail in layout.details
    ) == (
        0.0,
        1.0 / 3.0,
        2.0 / 3.0,
        1.0,
    )

    assert all(
        detail.min_z == 0.0
        and detail.max_z == 7.0
        for detail in layout.details
    )


def test_buttresses_preserve_print_resolution_decision():
    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=1.0,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        detail_type="buttress",
    )

    layout = AtlasFacadeStructuralDetailLayout.create(
        bay_analysis=_three_bay_analysis(),
        detail_kind="buttress",
        physical_decision=decision,
    )

    assert layout.detail_count == 4
    assert all(
        detail.detail_kind == "buttress"
        for detail in layout.details
    )
    assert all(
        detail.action == "enlarge"
        for detail in layout.details
    )
    assert all(
        detail.resolved_size_mm == 0.4
        for detail in layout.details
    )


def test_omitted_physical_details_create_no_placements():
    decision = AtlasPhysicalDetailResolver.resolve(
        real_size_m=0.10,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        detail_type="buttress",
    )

    layout = AtlasFacadeStructuralDetailLayout.create(
        bay_analysis=_three_bay_analysis(),
        detail_kind="buttress",
        physical_decision=decision,
    )

    assert layout.detail_count == 0
    assert layout.details == ()
