import pytest

from CORE.atlas_morphology_aware_terrain_product_resolver import (
    AtlasMorphologyAwareTerrainProductResolver,
)


@pytest.mark.parametrize(
    ("scene_morphology", "expected_emphasis"),
    (
        ("dense_urban", "secondary"),
        ("historic_core", "restrained"),
        ("suburban", "moderate"),
        ("rural", "important"),
        ("mountain", "dominant"),
        ("landscape_nature", "primary"),
    ),
)
def test_morphology_resolves_deterministic_terrain_emphasis(
    scene_morphology,
    expected_emphasis,
):
    result = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology=scene_morphology,
        source_elevation_range_m=120.0,
        product_size_mm=150.0,
        urban_density=0.50,
        landmark_present=True,
        physical_relief_range_mm=8.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    assert result["scene_morphology"] == scene_morphology
    assert result["terrain_emphasis"] == expected_emphasis


def test_dense_urban_uses_strong_vertical_compression():
    result = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="dense_urban",
        source_elevation_range_m=120.0,
        product_size_mm=150.0,
        urban_density=0.80,
        landmark_present=True,
        physical_relief_range_mm=8.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    assert result["vertical_compression"] == "strong"


def test_resolver_preserves_source_elevation_range():
    result = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="mountain",
        source_elevation_range_m=487.25,
        product_size_mm=170.0,
        urban_density=0.10,
        landmark_present=False,
        physical_relief_range_mm=14.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=18.0,
    )

    assert result["source_elevation_range_m"] == pytest.approx(
        487.25
    )
    assert result["source_elevation_modified"] is False


def test_resolver_records_product_decision_inputs():
    result = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="rural",
        source_elevation_range_m=83.0,
        product_size_mm=150.0,
        urban_density=0.18,
        landmark_present=False,
        physical_relief_range_mm=6.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    assert result["product_size_mm"] == pytest.approx(150.0)
    assert result["urban_density"] == pytest.approx(0.18)
    assert result["landmark_present"] is False
    assert result["physical_relief_range_mm"] == pytest.approx(6.0)
    assert result["minimum_printable_relief_mm"] == pytest.approx(0.30)
    assert result["maximum_printable_relief_mm"] == pytest.approx(12.0)


def test_resolver_is_deterministic():
    kwargs = {
        "scene_morphology": "rural",
        "source_elevation_range_m": 83.0,
        "product_size_mm": 150.0,
        "urban_density": 0.18,
        "landmark_present": False,
        "physical_relief_range_mm": 6.0,
        "minimum_printable_relief_mm": 0.30,
        "maximum_printable_relief_mm": 12.0,
    }

    assert (
        AtlasMorphologyAwareTerrainProductResolver.resolve(**kwargs)
        == AtlasMorphologyAwareTerrainProductResolver.resolve(**kwargs)
    )


def test_resolver_clamps_product_relief_to_printable_range():
    below = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="suburban",
        source_elevation_range_m=25.0,
        product_size_mm=150.0,
        urban_density=0.35,
        landmark_present=False,
        physical_relief_range_mm=0.10,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    above = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="mountain",
        source_elevation_range_m=800.0,
        product_size_mm=150.0,
        urban_density=0.05,
        landmark_present=False,
        physical_relief_range_mm=25.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    assert below["resolved_physical_relief_mm"] == pytest.approx(0.30)
    assert below["printability_adjustment"] == "raised_to_minimum"

    assert above["resolved_physical_relief_mm"] == pytest.approx(12.0)
    assert above["printability_adjustment"] == "limited_to_maximum"


def test_resolver_uses_product_size_for_relative_relief_context():
    result = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="rural",
        source_elevation_range_m=120.0,
        product_size_mm=150.0,
        urban_density=0.20,
        landmark_present=False,
        physical_relief_range_mm=7.5,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    assert result["relative_physical_relief"] == pytest.approx(
        7.5 / 150.0
    )


def test_resolver_exposes_semantic_protection_pressure():
    dense_landmark = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="historic_core",
        source_elevation_range_m=90.0,
        product_size_mm=150.0,
        urban_density=0.85,
        landmark_present=True,
        physical_relief_range_mm=8.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    rural_without_landmark = AtlasMorphologyAwareTerrainProductResolver.resolve(
        scene_morphology="rural",
        source_elevation_range_m=90.0,
        product_size_mm=150.0,
        urban_density=0.10,
        landmark_present=False,
        physical_relief_range_mm=8.0,
        minimum_printable_relief_mm=0.30,
        maximum_printable_relief_mm=12.0,
    )

    assert dense_landmark["semantic_content_priority"] == "protect"
    assert dense_landmark["urban_density_pressure"] == pytest.approx(0.85)

    assert rural_without_landmark["semantic_content_priority"] == "normal"
    assert rural_without_landmark["urban_density_pressure"] == pytest.approx(
        0.10
    )
