import pytest

from CORE.atlas_building_height_product_normalizer import (
    AtlasBuildingHeightProductNormalizer,
)


def test_preserves_readable_generic_building_height():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=12.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=2.0,
        semantic_importance=0.40,
        is_semantic_landmark=False,
    )

    assert result.source_height_m == pytest.approx(12.0)
    assert result.normalized_height_m == pytest.approx(12.0)
    assert result.normalized_height_mm == pytest.approx(
        12.0 * 1000.0 / 5500.0
    )
    assert result.changed is False
    assert result.reason == "source_height_preserved"


def test_raises_generic_building_to_physical_minimum_readable_height():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=6.0,
        block_median_height_m=8.0,
        scale_ratio=10000.0,
        minimum_readable_height_mm=2.0,
        semantic_importance=0.20,
        is_semantic_landmark=False,
    )

    assert result.source_height_m == pytest.approx(6.0)
    assert result.normalized_height_mm == pytest.approx(2.0)
    assert result.normalized_height_m == pytest.approx(20.0)
    assert result.changed is True
    assert result.reason == "physical_minimum"


def test_caps_excessive_generic_background_outlier_against_block_context():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=40.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.20,
        is_semantic_landmark=False,
        maximum_block_height_ratio=2.0,
    )

    assert result.source_height_m == pytest.approx(40.0)
    assert result.normalized_height_m == pytest.approx(20.0)
    assert result.is_statistical_outlier is True
    assert result.changed is True
    assert result.reason == "block_height_outlier"


def test_does_not_flatten_normal_block_height_variation():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=16.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.20,
        is_semantic_landmark=False,
        maximum_block_height_ratio=2.0,
    )

    assert result.normalized_height_m == pytest.approx(16.0)
    assert result.is_statistical_outlier is False
    assert result.changed is False


def test_semantic_landmark_retains_its_own_height_policy():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=48.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=2.0,
        semantic_importance=1.0,
        is_semantic_landmark=True,
        maximum_block_height_ratio=2.0,
    )

    assert result.normalized_height_m == pytest.approx(48.0)
    assert result.changed is False
    assert result.reason == "semantic_landmark_preserved"
    assert result.is_semantic_landmark is True


def test_source_truth_is_never_overwritten_by_normalization():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=40.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.25,
        is_semantic_landmark=False,
        maximum_block_height_ratio=2.0,
    )

    assert result.source_height_m == pytest.approx(40.0)
    assert result.normalized_height_m == pytest.approx(20.0)


@pytest.mark.parametrize(
    "kwargs",
    (
        {
            "source_height_m": 0.0,
            "block_median_height_m": 10.0,
            "scale_ratio": 5500.0,
            "minimum_readable_height_mm": 2.0,
            "semantic_importance": 0.5,
            "is_semantic_landmark": False,
        },
        {
            "source_height_m": 10.0,
            "block_median_height_m": 10.0,
            "scale_ratio": 0.0,
            "minimum_readable_height_mm": 2.0,
            "semantic_importance": 0.5,
            "is_semantic_landmark": False,
        },
        {
            "source_height_m": 10.0,
            "block_median_height_m": 10.0,
            "scale_ratio": 5500.0,
            "minimum_readable_height_mm": 0.0,
            "semantic_importance": 0.5,
            "is_semantic_landmark": False,
        },
        {
            "source_height_m": 10.0,
            "block_median_height_m": 10.0,
            "scale_ratio": 5500.0,
            "minimum_readable_height_mm": 2.0,
            "semantic_importance": 1.5,
            "is_semantic_landmark": False,
        },
    ),
)
def test_rejects_invalid_height_normalization_inputs(kwargs):
    with pytest.raises((TypeError, ValueError)):
        AtlasBuildingHeightProductNormalizer.resolve(
            **kwargs
        )


def test_near_landmark_allows_more_generic_height_variation():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=24.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.70,
        is_semantic_landmark=False,
        landmark_distance_m=15.0,
        landmark_context_distance_m=50.0,
        maximum_block_height_ratio=2.0,
    )

    assert result.normalized_height_m == pytest.approx(24.0)
    assert result.changed is False
    assert result.reason == "landmark_context_preserved"
    assert result.near_landmark is True


def test_distant_low_importance_generic_outlier_is_normalized():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=24.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.20,
        is_semantic_landmark=False,
        landmark_distance_m=120.0,
        landmark_context_distance_m=50.0,
        maximum_block_height_ratio=2.0,
    )

    assert result.normalized_height_m == pytest.approx(20.0)
    assert result.changed is True
    assert result.reason == "block_height_outlier"
    assert result.near_landmark is False


def test_high_semantic_importance_preserves_moderate_generic_outlier():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=22.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.85,
        is_semantic_landmark=False,
        landmark_distance_m=None,
        maximum_block_height_ratio=2.0,
    )

    assert result.normalized_height_m == pytest.approx(22.0)
    assert result.changed is False
    assert result.reason == "semantic_importance_preserved"


def test_extreme_generic_outlier_is_still_capped_near_landmark():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=50.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.70,
        is_semantic_landmark=False,
        landmark_distance_m=10.0,
        landmark_context_distance_m=50.0,
        maximum_block_height_ratio=2.0,
    )

    assert result.normalized_height_m < 50.0
    assert result.is_statistical_outlier is True
    assert result.changed is True


def test_result_records_landmark_context():
    result = AtlasBuildingHeightProductNormalizer.resolve(
        source_height_m=12.0,
        block_median_height_m=10.0,
        scale_ratio=5500.0,
        minimum_readable_height_mm=1.0,
        semantic_importance=0.4,
        is_semantic_landmark=False,
        landmark_distance_m=25.0,
        landmark_context_distance_m=50.0,
    )

    assert result.landmark_distance_m == pytest.approx(25.0)
    assert result.landmark_context_distance_m == pytest.approx(50.0)
    assert result.near_landmark is True
