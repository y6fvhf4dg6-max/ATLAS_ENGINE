import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_distance_aggregate import (
    AtlasCanonicalHeadMetricDistanceAggregate,
)


def test_aggregates_raw_distance_metrics_in_millimetres():
    result = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray(
            [0.0, 1.0, 2.0, 3.0],
            dtype=np.float64,
        )
    )

    assert result.sample_count == 4
    assert result.mean_distance_mm == pytest.approx(1.5)
    assert result.median_distance_mm == pytest.approx(1.5)
    assert result.rmse_distance_mm == pytest.approx(
        np.sqrt(3.5)
    )
    assert result.p95_distance_mm == pytest.approx(
        np.percentile(
            np.asarray([0.0, 1.0, 2.0, 3.0]),
            95.0,
        )
    )
    assert result.max_distance_mm == pytest.approx(3.0)


def test_does_not_mutate_source_distances():
    source = np.asarray(
        [0.5, 1.5, 2.5],
        dtype=np.float64,
    )
    before = source.copy()

    AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=source
    )

    np.testing.assert_array_equal(
        source,
        before,
    )


@pytest.mark.parametrize(
    "distances",
    (
        np.asarray([]),
        np.asarray([1.0, np.nan]),
        np.asarray([1.0, np.inf]),
        np.asarray([1.0, -0.1]),
        np.asarray([[1.0, 2.0]]),
    ),
)
def test_rejects_invalid_distance_arrays(
    distances,
):
    with pytest.raises(ValueError, match="distances_mm"):
        AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
            distances_mm=distances
        )


def _item10_8_gt_observation(
    *,
    admissibility_state="ACCEPTABLE",
):
    from CORE.atlas_canonical_head_metric_ground_truth_observation import (
        AtlasCanonicalHeadMetricGroundTruthObservation,
    )

    return AtlasCanonicalHeadMetricGroundTruthObservation(
        observation_id="item10-8-fixture-observation",
        subject_id="item10-8-fixture-subject",
        source_id="item10-8-fixture-source",
        units="mm",
        ground_truth_vertices=np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        ground_truth_faces=((0, 1, 2),),
        reconstruction_vertices=np.asarray(
            [
                [0.0, 0.0, 0.1],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        reconstruction_faces=((0, 1, 2),),
        source_provenance_state="VERIFIED",
        evaluation_license_state="UNRESOLVED",
        evaluation_use_only=True,
        acquisition_modality="MULTIVIEW_IMAGE_CAPTURE",
        acquisition_system="UNRESOLVED",
        acquisition_manufacturer="UNRESOLVED",
        reconstruction_modality="IMAGE_BASED_MULTIVIEW_RECONSTRUCTION",
        reconstruction_software="RealityCapture",
        reconstruction_software_version="1.4.2.117426",
        ground_truth_surface_origin="RECONSTRUCTED_SENSOR_DERIVED_SURFACE",
        ground_truth_strength_state="DERIVED_SENSOR",
        subject_match_state="VERIFIED",
        capture_session_relation="UNRESOLVED",
        capture_expression="NEUTRAL",
        capture_pose="WALKING",
        capture_date="UNRESOLVED",
        physical_resolution_state="UNRESOLVED",
        physical_resolution_reference="UNRESOLVED",
        calibration_state="UNRESOLVED",
        calibration_reference="UNRESOLVED",
        known_reference_dimension_mm=None,
        reference_uncertainty_mm=None,
        calibration_date="UNRESOLVED",
        reconstruction_scale_factor=1.0,
        scale_transform_provenance="UNRESOLVED",
        scale_source="UNRESOLVED",
        scale_uncertainty_mm=None,
        scale_uncertainty_propagation="UNRESOLVED",
        source_coordinate_frame="UNRESOLVED",
        target_coordinate_frame="UNRESOLVED",
        source_handedness="UNRESOLVED",
        target_handedness="UNRESOLVED",
        source_axis_definitions=(
            "UNRESOLVED_X",
            "UNRESOLVED_Y",
            "UNRESOLVED_Z",
        ),
        target_axis_definitions=(
            "UNRESOLVED_X",
            "UNRESOLVED_Y",
            "UNRESOLVED_Z",
        ),
        source_coordinate_origin="UNRESOLVED",
        target_coordinate_origin="UNRESOLVED",
        source_orientation="UNRESOLVED",
        target_orientation="UNRESOLVED",
        canonical_pose="UNRESOLVED",
        coordinate_transform_provenance="UNRESOLVED",
        transform_order=(
            "AXIS_PERMUTATION",
            "REFLECTION",
            "CANONICAL_POSE",
        ),
        axis_permutation=(0, 1, 2),
        reflection_state="UNRESOLVED",
        reflection_applied=None,
        canonical_pose_transform=np.eye(4, dtype=np.float64),
        round_trip_invertibility_state="UNRESOLVED",
        source_provenance_reference="item10-8-test-evidence",
        license_reference="UNRESOLVED",
        license_restrictions="UNRESOLVED",
        ground_truth_admissibility_state=admissibility_state,
    )


# === PHASE 8 ITEM 10.8 GLOBAL METRIC ERROR RED ===


def test_global_metric_evaluation_records_admissible_metric_result():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0, 1.5, 2.0], dtype=np.float64)
    )

    result = AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
        aggregate=aggregate,
        ground_truth_observation=_item10_8_gt_observation(),
        alignment_admissibility="ADMISSIBLE",
        alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
        correspondence_evidence_class=(
            "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
        ),
        correspondence_direction="SOURCE_TO_TARGET",
        bidirectional_evaluation_state="NOT_PERFORMED",
        regional_blocker_state="PRESENT",
    )

    assert result.aggregate is aggregate
    assert result.global_metric_result_state == "ADMISSIBLE"
    assert result.alignment_bias_leakage_risk == "NO_OVERLAP_IDENTIFIED"
    assert result.regional_blocker_state == "PRESENT"


def test_global_metric_result_rejects_unacceptable_ground_truth():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([1.0, 2.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="ground_truth|admiss"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(admissibility_state="BLOCKED"),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
        )


def test_global_metric_result_rejects_inadmissible_alignment():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([1.0, 2.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="alignment|admiss"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="INADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
        )


def test_global_metric_result_rejects_unresolved_correspondence():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([1.0, 2.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="correspondence"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class="UNRESOLVED_CORRESPONDENCE",
            correspondence_direction="UNRESOLVED",
            bidirectional_evaluation_state="UNRESOLVED",
            regional_blocker_state="NONE",
        )


def test_overlap_risk_remains_explicit_without_automatically_invalidating_result():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    result = AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
        aggregate=aggregate,
        ground_truth_observation=_item10_8_gt_observation(),
        alignment_admissibility="ADMISSIBLE",
        alignment_bias_leakage_risk="OVERLAP_PRESENT",
        correspondence_evidence_class=(
            "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
        ),
        correspondence_direction="SOURCE_TO_TARGET",
        bidirectional_evaluation_state="NOT_PERFORMED",
        regional_blocker_state="NONE",
    )

    assert result.global_metric_result_state == "ADMISSIBLE"
    assert result.alignment_bias_leakage_risk == "OVERLAP_PRESENT"


def test_global_metric_evaluation_does_not_clear_regional_blockers():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.2, 0.3, 0.4], dtype=np.float64)
    )

    result = AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
        aggregate=aggregate,
        ground_truth_observation=_item10_8_gt_observation(),
        alignment_admissibility="ADMISSIBLE",
        alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
        correspondence_evidence_class=(
            "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
        ),
        correspondence_direction="SOURCE_TO_TARGET",
        bidirectional_evaluation_state="NOT_PERFORMED",
        regional_blocker_state="PRESENT",
    )

    assert result.global_metric_result_state == "ADMISSIBLE"
    assert result.regional_blocker_state == "PRESENT"


def test_bidirectional_metric_state_requires_bidirectional_direction():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([1.0, 2.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="bidirectional|direction"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="VERIFIED",
            regional_blocker_state="NONE",
        )


def test_numeric_aggregate_alone_does_not_claim_metric_admissibility():
    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([1.0, 2.0], dtype=np.float64)
    )

    assert not hasattr(aggregate, "global_metric_result_state")
    assert not hasattr(aggregate, "ground_truth_admissibility_state")
    assert not hasattr(aggregate, "alignment_admissibility")

# === PHASE 8 ITEM 10.8 GT EVIDENCE-BINDING CORRECTIVE RED ===


def test_global_metric_evaluation_requires_metric_ground_truth_observation_object():
    import inspect

    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    signature = inspect.signature(
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate
    )

    assert "ground_truth_observation" in signature.parameters
    assert "ground_truth_admissibility_state" not in signature.parameters


def test_global_metric_evaluation_rejects_bare_ground_truth_admissibility_token():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([1.0, 2.0], dtype=np.float64)
    )

    with pytest.raises(TypeError):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation="ACCEPTABLE",
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
        )


def test_global_metric_result_records_bound_ground_truth_observation_identity():
    from dataclasses import fields

    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluationResult,
    )

    field_names = tuple(
        field.name
        for field in fields(
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
        )
    )

    assert "ground_truth_observation_id" in field_names
    assert "ground_truth_source_id" in field_names
    assert "ground_truth_admissibility_state" in field_names

# === PHASE 8 ITEM 10.8 FORGED GT INSTANCE CORRECTIVE RED V2 ===


def test_global_metric_evaluation_rejects_gt_instance_that_bypassed_contract_initialization():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )
    from CORE.atlas_canonical_head_metric_ground_truth_observation import (
        AtlasCanonicalHeadMetricGroundTruthObservation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0, 1.5], dtype=np.float64)
    )

    forged = object.__new__(
        AtlasCanonicalHeadMetricGroundTruthObservation
    )
    object.__setattr__(
        forged,
        "observation_id",
        "forged-observation",
    )
    object.__setattr__(
        forged,
        "source_id",
        "forged-source",
    )
    object.__setattr__(
        forged,
        "ground_truth_admissibility_state",
        "ACCEPTABLE",
    )

    with pytest.raises(
        (TypeError, ValueError, AttributeError)
    ):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=forged,
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
        )

# === PHASE 8 ITEM 10.8 LOCKED-SCOPE CORRECTIVE RED V3 ===


def test_global_metric_result_supports_locked_directional_and_coverage_evidence_fields():
    from dataclasses import fields

    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluationResult,
    )

    field_names = {
        field.name
        for field in fields(
            AtlasCanonicalHeadGlobalMetricErrorEvaluationResult
        )
    }

    required = {
        "source_to_target_aggregate",
        "target_to_source_aggregate",
        "symmetric_bidirectional_aggregate",
        "valid_correspondence_count",
        "evaluation_coverage_denominator",
        "missing_surface_fraction",
        "normal_orientation_angular_discrepancy_deg",
    }

    assert required <= field_names


def test_global_metric_evaluator_accepts_locked_coverage_evidence_inputs():
    import inspect

    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    parameters = set(
        inspect.signature(
            AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate
        ).parameters
    )

    required = {
        "source_to_target_aggregate",
        "target_to_source_aggregate",
        "symmetric_bidirectional_aggregate",
        "valid_correspondence_count",
        "evaluation_coverage_denominator",
        "missing_surface_fraction",
        "normal_orientation_angular_discrepancy_deg",
    }

    assert required <= parameters


def test_verified_bidirectional_metric_requires_both_directional_aggregates():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="direction|bidirectional"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="BIDIRECTIONAL",
            bidirectional_evaluation_state="VERIFIED",
            regional_blocker_state="NONE",
            source_to_target_aggregate=aggregate,
            target_to_source_aggregate=None,
            symmetric_bidirectional_aggregate=aggregate,
            valid_correspondence_count=2,
            evaluation_coverage_denominator=2,
            missing_surface_fraction=0.0,
            normal_orientation_angular_discrepancy_deg=None,
        )


def test_symmetric_metric_cannot_be_reported_without_verified_bidirectional_evidence():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="symmetric|bidirectional|direction"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
            source_to_target_aggregate=aggregate,
            target_to_source_aggregate=None,
            symmetric_bidirectional_aggregate=aggregate,
            valid_correspondence_count=2,
            evaluation_coverage_denominator=2,
            missing_surface_fraction=0.0,
            normal_orientation_angular_discrepancy_deg=None,
        )

# === PHASE 8 ITEM 10.8 COUNT-AGGREGATE CORRECTIVE RED V4 ===


def test_global_metric_result_rejects_zero_valid_correspondence_count():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0, 1.5], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="valid_correspondence_count|correspondence"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
            source_to_target_aggregate=aggregate,
            valid_correspondence_count=0,
            evaluation_coverage_denominator=3,
            missing_surface_fraction=1.0,
            normal_orientation_angular_discrepancy_deg=None,
        )


def test_global_metric_result_rejects_valid_count_that_disagrees_with_primary_aggregate():
    from CORE.atlas_canonical_head_metric_distance_aggregate import (
        AtlasCanonicalHeadGlobalMetricErrorEvaluation,
    )

    aggregate = AtlasCanonicalHeadMetricDistanceAggregate.from_distances(
        distances_mm=np.asarray([0.5, 1.0, 1.5], dtype=np.float64)
    )

    with pytest.raises(ValueError, match="valid_correspondence_count|sample_count|aggregate"):
        AtlasCanonicalHeadGlobalMetricErrorEvaluation.evaluate(
            aggregate=aggregate,
            ground_truth_observation=_item10_8_gt_observation(),
            alignment_admissibility="ADMISSIBLE",
            alignment_bias_leakage_risk="NO_OVERLAP_IDENTIFIED",
            correspondence_evidence_class=(
                "GEOMETRIC_CLOSEST_POINT_CORRESPONDENCE"
            ),
            correspondence_direction="SOURCE_TO_TARGET",
            bidirectional_evaluation_state="NOT_PERFORMED",
            regional_blocker_state="NONE",
            source_to_target_aggregate=aggregate,
            valid_correspondence_count=2,
            evaluation_coverage_denominator=4,
            missing_surface_fraction=0.5,
            normal_orientation_angular_discrepancy_deg=None,
        )
