import pytest

from CORE.atlas_morphology_composition_policy import (
    AtlasMorphologyCompositionPolicy,
)


@pytest.mark.parametrize(
    "morphology,expected",
    [
        (
            "dense_urban",
            {
                "terrain_emphasis": 0.35,
                "road_emphasis": 0.90,
                "urban_block_emphasis": 0.90,
                "vegetation_emphasis": 0.45,
                "water_emphasis": 0.55,
                "infrastructure_emphasis": 0.85,
                "landmark_emphasis": 0.90,
            },
        ),
        (
            "historic_core",
            {
                "terrain_emphasis": 0.35,
                "road_emphasis": 0.90,
                "urban_block_emphasis": 0.95,
                "vegetation_emphasis": 0.40,
                "water_emphasis": 0.55,
                "infrastructure_emphasis": 0.70,
                "landmark_emphasis": 1.00,
            },
        ),
        (
            "suburban",
            {
                "terrain_emphasis": 0.60,
                "road_emphasis": 0.70,
                "urban_block_emphasis": 0.65,
                "vegetation_emphasis": 0.75,
                "water_emphasis": 0.60,
                "infrastructure_emphasis": 0.60,
                "landmark_emphasis": 0.80,
            },
        ),
        (
            "forest",
            {
                "terrain_emphasis": 0.70,
                "road_emphasis": 0.60,
                "urban_block_emphasis": 0.35,
                "vegetation_emphasis": 1.00,
                "water_emphasis": 0.65,
                "infrastructure_emphasis": 0.50,
                "landmark_emphasis": 0.75,
            },
        ),
        (
            "rural",
            {
                "terrain_emphasis": 0.90,
                "road_emphasis": 0.55,
                "urban_block_emphasis": 0.45,
                "vegetation_emphasis": 0.80,
                "water_emphasis": 0.65,
                "infrastructure_emphasis": 0.45,
                "landmark_emphasis": 0.70,
            },
        ),
        (
            "river_city",
            {
                "terrain_emphasis": 0.55,
                "road_emphasis": 0.70,
                "urban_block_emphasis": 0.65,
                "vegetation_emphasis": 0.60,
                "water_emphasis": 1.00,
                "infrastructure_emphasis": 0.90,
                "landmark_emphasis": 0.85,
            },
        ),
        (
            "coastal",
            {
                "terrain_emphasis": 0.60,
                "road_emphasis": 0.65,
                "urban_block_emphasis": 0.60,
                "vegetation_emphasis": 0.60,
                "water_emphasis": 1.00,
                "infrastructure_emphasis": 0.90,
                "landmark_emphasis": 0.85,
            },
        ),
        (
            "mountain",
            {
                "terrain_emphasis": 1.00,
                "road_emphasis": 0.55,
                "urban_block_emphasis": 0.45,
                "vegetation_emphasis": 0.70,
                "water_emphasis": 0.55,
                "infrastructure_emphasis": 0.50,
                "landmark_emphasis": 0.80,
            },
        ),
    ],
)
def test_morphology_composition_policy_resolves_profile(
    morphology,
    expected,
):
    result = AtlasMorphologyCompositionPolicy.resolve(
        morphology=morphology,
    )

    assert result["morphology"] == morphology

    for key, value in expected.items():
        assert result[key] == pytest.approx(value)


def test_morphology_composition_policy_is_deterministic():
    first = AtlasMorphologyCompositionPolicy.resolve(
        morphology="dense_urban",
    )
    second = AtlasMorphologyCompositionPolicy.resolve(
        morphology="dense_urban",
    )

    assert first == second


def test_morphology_composition_policy_rejects_unknown_morphology():
    with pytest.raises(
        ValueError,
        match="morphology",
    ):
        AtlasMorphologyCompositionPolicy.resolve(
            morphology="bonn",
        )


def test_mixed_morphology_blends_measured_scene_evidence():
    result = AtlasMorphologyCompositionPolicy.resolve(
        morphology="mixed",
        scene_evidence={
            "building_density": 0.55,
            "road_density": 0.50,
            "block_compactness": 0.45,
            "vegetation_coverage": 0.35,
            "forest_coverage": 0.10,
            "water_coverage": 0.30,
            "railway_presence": True,
            "terrain_relief": 0.20,
            "landmark_density": 0.08,
        },
    )

    assert result["morphology"] == "mixed"
    assert result["profile_source"] == "evidence_blend"

    assert result["water_emphasis"] > 0.65
    assert result["road_emphasis"] > 0.65
    assert result["infrastructure_emphasis"] > 0.65

    assert 0.0 <= result["terrain_emphasis"] <= 1.0
    assert 0.0 <= result["vegetation_emphasis"] <= 1.0


def test_non_mixed_morphology_remains_profile_driven_with_evidence():
    result = AtlasMorphologyCompositionPolicy.resolve(
        morphology="dense_urban",
        scene_evidence={
            "building_density": 0.10,
            "road_density": 0.10,
            "block_compactness": 0.10,
            "vegetation_coverage": 0.90,
            "forest_coverage": 0.80,
            "water_coverage": 0.50,
            "railway_presence": False,
            "terrain_relief": 0.90,
            "landmark_density": 0.00,
        },
    )

    assert result["morphology"] == "dense_urban"
    assert result["profile_source"] == "named_profile"
    assert result["road_emphasis"] == pytest.approx(0.90)
    assert result["terrain_emphasis"] == pytest.approx(0.35)
