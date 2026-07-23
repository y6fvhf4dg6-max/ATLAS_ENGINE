import pytest

from CORE.atlas_building_roof_profiler import AtlasBuildingRoofProfiler


def test_explicit_gable_roof_shape_is_preserved():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape="gable",
        aspect_ratio=1.10,
        rectangularity=0.95,
        is_building_part=False,
    )

    assert result["roof_profile"] == "gable"
    assert result["decision_source"] == "osm"


def test_explicit_hipped_roof_shape_is_preserved():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape="hipped",
        aspect_ratio=2.20,
        rectangularity=0.95,
        is_building_part=False,
    )

    assert result["roof_profile"] == "hipped"
    assert result["decision_source"] == "osm"


def test_explicit_pyramidal_roof_shape_is_preserved():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape="pyramidal",
        aspect_ratio=1.05,
        rectangularity=0.95,
        is_building_part=False,
    )

    assert result["roof_profile"] == "pyramidal"
    assert result["decision_source"] == "osm"


def test_long_rectangular_building_uses_gable_fallback():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape=None,
        aspect_ratio=2.10,
        rectangularity=0.91,
        is_building_part=False,
    )

    assert result["roof_profile"] == "gable"
    assert result["decision_source"] == "inferred"


def test_moderately_rectangular_building_uses_gable_fallback():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape=None,
        aspect_ratio=1.45,
        rectangularity=0.80,
        is_building_part=False,
    )

    assert result["roof_profile"] == "gable"
    assert result["decision_source"] == "inferred"


def test_near_square_rectangular_building_uses_hipped_fallback():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape=None,
        aspect_ratio=1.20,
        rectangularity=0.92,
        is_building_part=False,
    )

    assert result["roof_profile"] == "hipped"
    assert result["decision_source"] == "inferred"


def test_complex_footprint_remains_flat():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape=None,
        aspect_ratio=2.40,
        rectangularity=0.60,
        is_building_part=False,
    )

    assert result["roof_profile"] == "flat"
    assert result["decision_source"] == "fallback"


def test_building_part_does_not_receive_inferred_roof():
    result = AtlasBuildingRoofProfiler.classify(
        roof_shape=None,
        aspect_ratio=2.00,
        rectangularity=0.95,
        is_building_part=True,
    )

    assert result["roof_profile"] == "flat"
    assert result["decision_source"] == "building_part"


@pytest.mark.parametrize(
    "aspect_ratio, rectangularity",
    [
        (0.0, 0.90),
        (-1.0, 0.90),
        (1.50, -0.10),
        (1.50, 1.10),
    ],
)
def test_invalid_geometry_metrics_are_rejected(
    aspect_ratio,
    rectangularity,
):
    with pytest.raises(ValueError):
        AtlasBuildingRoofProfiler.classify(
            roof_shape=None,
            aspect_ratio=aspect_ratio,
            rectangularity=rectangularity,
            is_building_part=False,
        )
