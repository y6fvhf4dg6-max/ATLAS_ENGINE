import pytest

from CORE.atlas_scene_morphology_classifier import (
    AtlasSceneMorphologyClassifier,
)


@pytest.mark.parametrize(
    "expected,evidence",
    [
        (
            "dense_urban",
            {
                "building_density": 0.82,
                "road_density": 0.78,
                "block_compactness": 0.80,
                "vegetation_coverage": 0.12,
                "forest_coverage": 0.02,
                "water_coverage": 0.01,
                "railway_presence": True,
                "terrain_relief": 0.08,
                "landmark_density": 0.18,
            },
        ),
        (
            "forest",
            {
                "building_density": 0.04,
                "road_density": 0.08,
                "block_compactness": 0.05,
                "vegetation_coverage": 0.88,
                "forest_coverage": 0.82,
                "water_coverage": 0.03,
                "railway_presence": False,
                "terrain_relief": 0.18,
                "landmark_density": 0.01,
            },
        ),
        (
            "river_city",
            {
                "building_density": 0.52,
                "road_density": 0.48,
                "block_compactness": 0.50,
                "vegetation_coverage": 0.24,
                "forest_coverage": 0.08,
                "water_coverage": 0.28,
                "railway_presence": True,
                "terrain_relief": 0.10,
                "landmark_density": 0.08,
            },
        ),
        (
            "rural",
            {
                "building_density": 0.08,
                "road_density": 0.12,
                "block_compactness": 0.10,
                "vegetation_coverage": 0.48,
                "forest_coverage": 0.18,
                "water_coverage": 0.02,
                "railway_presence": False,
                "terrain_relief": 0.16,
                "landmark_density": 0.01,
            },
        ),
    ],
)
def test_scene_morphology_classifier_resolves_dominant_character(
    expected,
    evidence,
):
    result = AtlasSceneMorphologyClassifier.resolve(
        **evidence,
    )

    assert result["morphology"] == expected
    assert result["confidence"] > 0.0
    assert result["evidence"] == evidence


def test_scene_morphology_classifier_is_deterministic():
    evidence = {
        "building_density": 0.60,
        "road_density": 0.58,
        "block_compactness": 0.62,
        "vegetation_coverage": 0.18,
        "forest_coverage": 0.03,
        "water_coverage": 0.01,
        "railway_presence": False,
        "terrain_relief": 0.06,
        "landmark_density": 0.20,
    }

    first = AtlasSceneMorphologyClassifier.resolve(
        **evidence,
    )
    second = AtlasSceneMorphologyClassifier.resolve(
        **evidence,
    )

    assert first == second


def test_scene_morphology_classifier_does_not_accept_location_identity():
    with pytest.raises(
        TypeError,
    ):
        AtlasSceneMorphologyClassifier.resolve(
            building_density=0.50,
            road_density=0.50,
            block_compactness=0.50,
            vegetation_coverage=0.20,
            forest_coverage=0.05,
            water_coverage=0.05,
            railway_presence=False,
            terrain_relief=0.10,
            landmark_density=0.05,
            location_name="Bonn",
        )
