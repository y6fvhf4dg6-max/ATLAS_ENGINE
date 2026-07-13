"""
ATLAS Building Analyzer Regression Tests

Bina sınıflandırma ve oran hesaplama davranışını otomatik
regresyon testleriyle güvence altına alır.
"""

from types import SimpleNamespace

from CORE.atlas_building_analyzer import AtlasBuildingAnalyzer


def make_building(
    *,
    area_m2=100.0,
    building_type="yes",
    width=1.0,
    depth=1.0,
    quality_score=100,
):
    return SimpleNamespace(
        building_id="test-building",
        building_type=building_type,
        area_m2=area_m2,
        perimeter_m=40.0,
        estimated_height=10.0,
        levels=3,
        roof_type=None,
        quality_score=quality_score,
        tags={"building": building_type},
        bbox={
            "west": 0.0,
            "east": width,
            "south": 0.0,
            "north": depth,
        },
    )


def test_square_building_has_unit_aspect_ratio():
    building = make_building(
        width=2.0,
        depth=2.0,
    )

    assert AtlasBuildingAnalyzer.aspect_ratio(building) == 1.0


def test_long_building_is_classified_as_too_long():
    building = make_building(
        width=10.0,
        depth=1.0,
    )

    assert AtlasBuildingAnalyzer.category(building) == "too_long"


def test_large_building_is_classified_as_large_complex():
    building = make_building(
        area_m2=6000.0,
        width=4.0,
        depth=2.0,
    )

    assert AtlasBuildingAnalyzer.category(building) == "large_complex"


def test_residential_building_is_classified_as_residential():
    building = make_building(
        building_type="apartments",
    )

    assert AtlasBuildingAnalyzer.category(building) == "residential"


def test_quality_score_caps_print_score():
    building = make_building(
        quality_score=72,
    )

    assert AtlasBuildingAnalyzer.print_score(building) == 72
