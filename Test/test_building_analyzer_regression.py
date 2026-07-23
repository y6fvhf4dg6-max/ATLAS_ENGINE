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
    geometry=None,
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
        geometry=geometry,
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



def test_aspect_ratio_uses_real_meter_dimensions():
    building = make_building(
        geometry=[
            (60.0000, 10.0000),
            (60.0000, 10.0020),
            (60.0010, 10.0020),
            (60.0010, 10.0000),
        ],
    )

    assert AtlasBuildingAnalyzer.aspect_ratio(building) == 1.0


def test_rectangular_footprint_is_not_concave():
    building = make_building(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.0020),
            (0.0010, 0.0020),
            (0.0010, 0.0),
        ],
    )

    assert AtlasBuildingAnalyzer.reflex_vertex_count(building) == 0
    assert AtlasBuildingAnalyzer.is_concave(building) is False


def test_l_shaped_footprint_has_one_reflex_vertex():
    building = make_building(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.0030),
            (0.0010, 0.0030),
            (0.0010, 0.0010),
            (0.0030, 0.0010),
            (0.0030, 0.0),
        ],
    )

    assert AtlasBuildingAnalyzer.reflex_vertex_count(building) == 1
    assert AtlasBuildingAnalyzer.is_concave(building) is True


def test_analysis_includes_footprint_complexity_metrics():
    building = make_building(
        geometry=[
            (0.0, 0.0),
            (0.0, 0.0030),
            (0.0010, 0.0030),
            (0.0010, 0.0010),
            (0.0030, 0.0010),
            (0.0030, 0.0),
        ],
    )

    result = AtlasBuildingAnalyzer.analyze(building)

    assert result["reflex_vertices"] == 1
    assert result["is_concave"] is True


def test_oriented_aspect_ratio_detects_rotated_long_rectangle():
    building = make_building(
        geometry=[
            (0.0000, 0.0000),
            (0.0010, 0.0010),
            (0.0012, 0.0008),
            (0.0002, -0.0002),
        ],
    )

    ratio = AtlasBuildingAnalyzer.oriented_aspect_ratio(building)

    assert ratio > 4.0


def test_rectangular_footprint_has_full_rectangularity():
    building = make_building(
        geometry=[
            (0.0000, 0.0000),
            (0.0000, 0.0020),
            (0.0010, 0.0020),
            (0.0010, 0.0000),
        ],
    )

    rectangularity = AtlasBuildingAnalyzer.rectangularity(building)

    assert rectangularity == 1.0


def test_l_shaped_footprint_has_lower_rectangularity():
    building = make_building(
        geometry=[
            (0.0000, 0.0000),
            (0.0000, 0.0030),
            (0.0010, 0.0030),
            (0.0010, 0.0010),
            (0.0030, 0.0010),
            (0.0030, 0.0000),
        ],
    )

    rectangularity = AtlasBuildingAnalyzer.rectangularity(building)

    assert 0.0 < rectangularity < 0.75


def test_oriented_metrics_return_zero_for_missing_geometry():
    building = make_building(
        geometry=None,
    )

    assert AtlasBuildingAnalyzer.oriented_aspect_ratio(building) == 0.0
    assert AtlasBuildingAnalyzer.rectangularity(building) == 0.0


def test_analysis_includes_oriented_footprint_metrics():
    building = make_building(
        geometry=[
            (0.0000, 0.0000),
            (0.0000, 0.0020),
            (0.0010, 0.0020),
            (0.0010, 0.0000),
        ],
    )

    result = AtlasBuildingAnalyzer.analyze(building)

    assert result["oriented_aspect_ratio"] == 2.0
    assert result["rectangularity"] == 1.0
