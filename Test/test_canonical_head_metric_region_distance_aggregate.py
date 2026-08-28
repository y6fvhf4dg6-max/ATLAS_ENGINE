import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
    AtlasCanonicalHeadMetricRegionDistanceAggregate,
)


def test_aggregates_distances_for_named_regions():
    distances = np.asarray(
        [0.5, 1.0, 2.0, 4.0, 8.0],
        dtype=np.float64,
    )

    result = AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
        distances_mm=distances,
        region_sample_indices={
            "nose": (1, 2),
            "jaw_chin": (3, 4),
        },
    )

    nose = result.region("nose")
    jaw_chin = result.region("jaw_chin")

    assert nose.sample_count == 2
    assert nose.mean_distance_mm == pytest.approx(1.5)
    assert nose.max_distance_mm == pytest.approx(2.0)

    assert jaw_chin.sample_count == 2
    assert jaw_chin.mean_distance_mm == pytest.approx(6.0)
    assert jaw_chin.max_distance_mm == pytest.approx(8.0)


def test_normalizes_region_names():
    result = AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
        distances_mm=np.asarray(
            [1.0, 2.0],
            dtype=np.float64,
        ),
        region_sample_indices={
            "Jaw Chin": (0, 1),
        },
    )

    assert result.region_names == ("jaw_chin",)
    assert result.region(" jaw   chin ").sample_count == 2


def test_rejects_out_of_bounds_region_sample_indices():
    with pytest.raises(
        ValueError,
        match="region_sample_indices",
    ):
        AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
            distances_mm=np.asarray(
                [1.0, 2.0],
                dtype=np.float64,
            ),
            region_sample_indices={
                "nose": (0, 2),
            },
        )


def test_rejects_empty_regions():
    with pytest.raises(
        ValueError,
        match="region_sample_indices",
    ):
        AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
            distances_mm=np.asarray(
                [1.0, 2.0],
                dtype=np.float64,
            ),
            region_sample_indices={},
        )


def test_rejects_empty_region_sample_set():
    with pytest.raises(
        ValueError,
        match="region_sample_indices",
    ):
        AtlasCanonicalHeadMetricRegionDistanceAggregate.from_regions(
            distances_mm=np.asarray(
                [1.0, 2.0],
                dtype=np.float64,
            ),
            region_sample_indices={
                "nose": (),
            },
        )

# === PHASE 8 ITEM 10.9 REGION-WISE METRIC ERROR RED ===


def test_region_metric_evaluation_result_records_locked_item10_9_fields():
    from dataclasses import fields

    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluationResult,
    )

    field_names = {
        field.name
        for field in fields(
            AtlasCanonicalHeadMetricRegionEvaluationResult
        )
    }

    required = {
        "semantic_region",
        "aggregate",
        "region_definition_origin",
        "ground_truth_region_mapping",
        "prediction_region_mapping",
        "correspondence_evidence_class",
        "valid_sample_count",
        "coverage_ratio",
        "region_alignment_overlap",
        "expression_compatibility",
        "posture_compatibility",
        "regional_metric_admissibility",
    }

    assert required <= field_names


def test_region_metric_evaluator_accepts_locked_item10_9_inputs():
    import inspect

    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    parameters = set(
        inspect.signature(
            AtlasCanonicalHeadMetricRegionEvaluation.evaluate
        ).parameters
    )

    required = {
        "semantic_region",
        "aggregate",
        "region_definition_origin",
        "ground_truth_region_mapping",
        "prediction_region_mapping",
        "correspondence_evidence_class",
        "valid_sample_count",
        "coverage_ratio",
        "region_alignment_overlap",
        "expression_compatibility",
        "posture_compatibility",
        "regional_metric_admissibility",
    }

    assert required <= parameters


def test_region_metric_rejects_valid_sample_count_that_disagrees_with_aggregate():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadMetricDistanceAggregate,
    )
    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0, 1.5], dtype=np.float64)
    )

    with pytest.raises(
        ValueError,
        match="valid_sample_count|sample_count|aggregate",
    ):
        AtlasCanonicalHeadMetricRegionEvaluation.evaluate(
            semantic_region="nose_body",
            aggregate=aggregate,
            region_definition_origin="PROVIDER_VERIFIED",
            ground_truth_region_mapping="VERIFIED",
            prediction_region_mapping="VERIFIED",
            correspondence_evidence_class=(
                "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
            ),
            valid_sample_count=2,
            coverage_ratio=1.0,
            region_alignment_overlap="NO_OVERLAP_IDENTIFIED",
            expression_compatibility="COMPATIBLE",
            posture_compatibility="COMPATIBLE",
            regional_metric_admissibility="ADMISSIBLE",
        )


def test_region_metric_rejects_coverage_ratio_outside_unit_interval():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadMetricDistanceAggregate,
    )
    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="coverage_ratio"):
        AtlasCanonicalHeadMetricRegionEvaluation.evaluate(
            semantic_region="jaw",
            aggregate=aggregate,
            region_definition_origin="PROVIDER_VERIFIED",
            ground_truth_region_mapping="VERIFIED",
            prediction_region_mapping="VERIFIED",
            correspondence_evidence_class=(
                "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
            ),
            valid_sample_count=2,
            coverage_ratio=1.25,
            region_alignment_overlap="NO_OVERLAP_IDENTIFIED",
            expression_compatibility="COMPATIBLE",
            posture_compatibility="COMPATIBLE",
            regional_metric_admissibility="ADMISSIBLE",
        )


def test_item8_h2_anchor_supported_footprint_cannot_be_promoted_to_dense_anatomical_metric_correspondence():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadMetricDistanceAggregate,
    )
    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    with pytest.raises(
        ValueError,
        match="anchor|dense|anatomical|correspondence",
    ):
        AtlasCanonicalHeadMetricRegionEvaluation.evaluate(
            semantic_region="nose_body",
            aggregate=aggregate,
            region_definition_origin="ITEM8_H2_ANCHOR_SUPPORTED_FOOTPRINT",
            ground_truth_region_mapping="ANCHOR_SUPPORTED_ONLY",
            prediction_region_mapping="ANCHOR_SUPPORTED_ONLY",
            correspondence_evidence_class="DENSE_ANATOMICAL_CORRESPONDENCE",
            valid_sample_count=2,
            coverage_ratio=1.0,
            region_alignment_overlap="NO_OVERLAP_IDENTIFIED",
            expression_compatibility="COMPATIBLE",
            posture_compatibility="COMPATIBLE",
            regional_metric_admissibility="ADMISSIBLE",
        )

# === PHASE 8 ITEM 10.9 CLOSURE CHALLENGE CORRECTIVE RED ===


@pytest.mark.parametrize(
    ("override", "match"),
    (
        (
            {"region_definition_origin": "UNRESOLVED_BLOCKED"},
            "region_definition_origin|admiss",
        ),
        (
            {"ground_truth_region_mapping": "UNRESOLVED_BLOCKED"},
            "ground_truth_region_mapping|admiss",
        ),
        (
            {"ground_truth_region_mapping": "ANCHOR_SUPPORTED_ONLY"},
            "ground_truth_region_mapping|anchor|admiss",
        ),
        (
            {"prediction_region_mapping": "UNRESOLVED_BLOCKED"},
            "prediction_region_mapping|admiss",
        ),
        (
            {"prediction_region_mapping": "ANCHOR_SUPPORTED_ONLY"},
            "prediction_region_mapping|anchor|admiss",
        ),
        (
            {"correspondence_evidence_class": "UNRESOLVED_CORRESPONDENCE"},
            "correspondence|admiss",
        ),
        (
            {"expression_compatibility": "INCOMPATIBLE"},
            "expression|admiss",
        ),
        (
            {"expression_compatibility": "UNRESOLVED"},
            "expression|admiss",
        ),
        (
            {"posture_compatibility": "INCOMPATIBLE"},
            "posture|admiss",
        ),
        (
            {"posture_compatibility": "UNRESOLVED"},
            "posture|admiss",
        ),
    ),
)
def test_admissible_region_metric_rejects_unresolved_or_incompatible_evidence(
    override,
    match,
):
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadMetricDistanceAggregate,
    )
    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    kwargs = dict(
        semantic_region="nose_body",
        aggregate=aggregate,
        region_definition_origin="PROVIDER_VERIFIED",
        ground_truth_region_mapping="VERIFIED",
        prediction_region_mapping="VERIFIED",
        correspondence_evidence_class=(
            "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
        ),
        valid_sample_count=2,
        coverage_ratio=1.0,
        region_alignment_overlap="NO_OVERLAP_IDENTIFIED",
        expression_compatibility="COMPATIBLE",
        posture_compatibility="COMPATIBLE",
        regional_metric_admissibility="ADMISSIBLE",
    )
    kwargs.update(override)

    with pytest.raises(ValueError, match=match):
        AtlasCanonicalHeadMetricRegionEvaluation.evaluate(**kwargs)


def test_admissible_region_metric_rejects_zero_coverage_with_valid_samples():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadMetricDistanceAggregate,
    )
    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="coverage_ratio|coverage|admiss"):
        AtlasCanonicalHeadMetricRegionEvaluation.evaluate(
            semantic_region="jaw",
            aggregate=aggregate,
            region_definition_origin="PROVIDER_VERIFIED",
            ground_truth_region_mapping="VERIFIED",
            prediction_region_mapping="VERIFIED",
            correspondence_evidence_class=(
                "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
            ),
            valid_sample_count=2,
            coverage_ratio=0.0,
            region_alignment_overlap="NO_OVERLAP_IDENTIFIED",
            expression_compatibility="COMPATIBLE",
            posture_compatibility="COMPATIBLE",
            regional_metric_admissibility="ADMISSIBLE",
        )


def test_item8_h2_anchor_supported_region_cannot_claim_metric_admissibility():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadMetricDistanceAggregate,
    )
    from CORE.atlas_canonical_head_metric_region_distance_aggregate import (
        AtlasCanonicalHeadMetricRegionEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="anchor|admiss|region"):
        AtlasCanonicalHeadMetricRegionEvaluation.evaluate(
            semantic_region="nose_body",
            aggregate=aggregate,
            region_definition_origin="ITEM8_H2_ANCHOR_SUPPORTED_FOOTPRINT",
            ground_truth_region_mapping="ANCHOR_SUPPORTED_ONLY",
            prediction_region_mapping="ANCHOR_SUPPORTED_ONLY",
            correspondence_evidence_class=(
                "VERIFIED_SEMANTIC_BARYCENTRIC_CORRESPONDENCE"
            ),
            valid_sample_count=2,
            coverage_ratio=1.0,
            region_alignment_overlap="NO_OVERLAP_IDENTIFIED",
            expression_compatibility="COMPATIBLE",
            posture_compatibility="COMPATIBLE",
            regional_metric_admissibility="ADMISSIBLE",
        )
