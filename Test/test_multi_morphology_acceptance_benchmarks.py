import pytest

from CORE.atlas_morphology_composition_policy import (
    AtlasMorphologyCompositionPolicy,
)
from CORE.atlas_scene_morphology_classifier import (
    AtlasSceneMorphologyClassifier,
)
from CORE.atlas_urban_fabric_quality_report import (
    AtlasUrbanFabricQualityReport,
)


BENCHMARKS = (
    {
        "name": "galata_tower",
        "expected_morphology": "dense_urban",
        "evidence": {
            "building_density": 0.444511838,
            "road_density": 0.114657015,
            "block_compactness": 0.365980763,
            "vegetation_coverage": 0.023482719,
            "forest_coverage": 0.023108538,
            "water_coverage": 0.0,
            "railway_presence": True,
            "terrain_relief": 0.142354906,
            "landmark_density": 0.038186158,
        },
    },
    {
        "name": "sultanahmet",
        "expected_morphology": "historic_core",
        "evidence": {
            "building_density": 0.210072466,
            "road_density": 0.064296084,
            "block_compactness": 0.418280237,
            "vegetation_coverage": 0.066918922,
            "forest_coverage": 0.065478161,
            "water_coverage": 0.036633513,
            "railway_presence": True,
            "terrain_relief": 0.067454545,
            "landmark_density": 0.041698256,
        },
    },
    {
        "name": "galata_bridge",
        "expected_morphology": "river_city",
        "evidence": {
            "building_density": 0.192089236,
            "road_density": 0.055806527,
            "block_compactness": 0.361269466,
            "vegetation_coverage": 0.001586961,
            "forest_coverage": 0.0,
            "water_coverage": 0.691199040,
            "railway_presence": True,
            "terrain_relief": 0.045549172,
            "landmark_density": 0.032773781,
        },
    },
    {
        "name": "forest_candidate",
        "expected_morphology": "forest",
        "evidence": {
            "building_density": 0.000720112,
            "road_density": 0.007371863,
            "block_compactness": 0.0,
            "vegetation_coverage": 0.758394543,
            "forest_coverage": 0.758394543,
            "water_coverage": 0.004190124,
            "railway_presence": False,
            "terrain_relief": 0.098352549,
            "landmark_density": 0.0,
        },
    },
    {
        "name": "erkelenz",
        "expected_morphology": "rural",
        "evidence": {
            "building_density": 0.150841391,
            "road_density": 0.066732481,
            "block_compactness": 0.222614675,
            "vegetation_coverage": 0.232364081,
            "forest_coverage": 0.232364081,
            "water_coverage": 0.0,
            "railway_presence": False,
            "terrain_relief": 0.019106811,
            "landmark_density": 0.001941748,
        },
    },
)


def _quality_scene(
    *,
    evidence,
    morphology,
    policy,
):
    return {
        "scene_morphology_evidence": dict(
            evidence
        ),
        "effective_scene_morphology": morphology,
        "morphology_composition_policy": dict(
            policy
        ),
        "city_composition_lod": {
            "decisions": {},
        },
        "mesh_groups": {
            "roads": [],
            "buildings": [],
            "parks": [],
            "trees": [],
            "forest_canopies": [],
            "waters": [],
            "landmarks": [],
            "railways": [],
        },
    }


@pytest.mark.parametrize(
    "benchmark",
    BENCHMARKS,
    ids=[
        benchmark["name"]
        for benchmark in BENCHMARKS
    ],
)
def test_multi_morphology_acceptance_uses_same_general_architecture(
    benchmark,
):
    evidence = dict(
        benchmark["evidence"]
    )
    expected = benchmark[
        "expected_morphology"
    ]

    first_classification = (
        AtlasSceneMorphologyClassifier.resolve(
            **evidence
        )
    )
    second_classification = (
        AtlasSceneMorphologyClassifier.resolve(
            **evidence
        )
    )

    assert (
        first_classification
        == second_classification
    )
    assert (
        first_classification["morphology"]
        == expected
    )
    assert (
        first_classification["evidence"]
        == evidence
    )
    assert (
        first_classification["confidence"]
        > 0.0
    )

    first_policy = (
        AtlasMorphologyCompositionPolicy.resolve(
            morphology=expected,
            scene_evidence=evidence,
        )
    )
    second_policy = (
        AtlasMorphologyCompositionPolicy.resolve(
            morphology=expected,
            scene_evidence=evidence,
        )
    )

    assert first_policy == second_policy
    assert first_policy["morphology"] == expected
    assert (
        first_policy["profile_source"]
        == "named_profile"
    )

    scene_result = _quality_scene(
        evidence=evidence,
        morphology=expected,
        policy=first_policy,
    )
    original_scene = repr(
        scene_result
    )

    first_report = (
        AtlasUrbanFabricQualityReport.build(
            scene_result=scene_result,
        )
    )
    second_report = (
        AtlasUrbanFabricQualityReport.build(
            scene_result=scene_result,
        )
    )

    assert first_report == second_report
    assert repr(scene_result) == original_scene

    metrics = first_report["metrics"]

    for key, value in evidence.items():
        if isinstance(value, bool):
            assert metrics[key] is value
        else:
            assert metrics[key] == pytest.approx(
                value
            )

    assert (
        first_report["terrain_metrics"][
            "terrain_prominence_ratio"
        ]
        == pytest.approx(
            first_policy[
                "terrain_emphasis"
            ]
        )
    )


def test_multi_morphology_acceptance_covers_all_required_families():
    assert {
        benchmark[
            "expected_morphology"
        ]
        for benchmark in BENCHMARKS
    } == {
        "dense_urban",
        "historic_core",
        "river_city",
        "forest",
        "rural",
    }


def test_multi_morphology_policies_preserve_distinct_composition_priorities():
    policies = {
        benchmark["expected_morphology"]:
            AtlasMorphologyCompositionPolicy.resolve(
                morphology=benchmark[
                    "expected_morphology"
                ],
                scene_evidence=benchmark[
                    "evidence"
                ],
            )
        for benchmark in BENCHMARKS
    }

    assert (
        policies["dense_urban"][
            "road_emphasis"
        ]
        == pytest.approx(0.90)
    )

    assert (
        policies["historic_core"][
            "landmark_emphasis"
        ]
        == pytest.approx(1.00)
    )

    assert (
        policies["river_city"][
            "water_emphasis"
        ]
        == pytest.approx(1.00)
    )

    assert (
        policies["forest"][
            "vegetation_emphasis"
        ]
        == pytest.approx(1.00)
    )

    assert (
        policies["rural"][
            "terrain_emphasis"
        ]
        == pytest.approx(0.90)
    )
