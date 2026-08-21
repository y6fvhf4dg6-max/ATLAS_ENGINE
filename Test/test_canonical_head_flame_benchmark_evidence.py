import pytest

from CORE.atlas_canonical_head_benchmark_measurement_observation import (
    AtlasCanonicalHeadBenchmarkMeasurementObservation,
)
from CORE.atlas_canonical_head_flame_benchmark_evidence import (
    AtlasCanonicalHeadFlameBenchmarkEvidence,
)


def test_exposes_two_real_flame_2023_open_measurements():
    measurements = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .measurements()
    )

    assert len(measurements) == 2

    assert all(
        isinstance(
            item,
            AtlasCanonicalHeadBenchmarkMeasurementObservation,
        )
        for item in measurements
    )

    assert tuple(
        item.subject_id
        for item in measurements
    ) == (
        "subject_01",
        "subject_02",
    )


def test_preserves_verified_subject_01_measurement():
    measurement = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .measurement_for_subject(
            "subject_01"
        )
    )

    assert measurement.candidate_id == "flame-2023-open"
    assert measurement.view_count == 3
    assert measurement.landmarks_per_view == 105

    assert measurement.mean_reprojection_iod_nme == pytest.approx(
        0.027984
    )
    assert measurement.mean_reprojection_bbox_nme == pytest.approx(
        0.007818
    )
    assert measurement.cross_view_identity_shape_nme == pytest.approx(
        0.059630
    )

    assert measurement.focal_identifiable is False
    assert measurement.ground_truth_3d_available is False
    assert measurement.volumetric_identity_proven is False
    assert measurement.processing_time_seconds == pytest.approx(
        1.407287
    )


def test_preserves_verified_subject_02_measurement():
    measurement = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .measurement_for_subject(
            "subject_02"
        )
    )

    assert measurement.candidate_id == "flame-2023-open"
    assert measurement.view_count == 3
    assert measurement.landmarks_per_view == 105

    assert measurement.mean_reprojection_iod_nme == pytest.approx(
        0.023456
    )
    assert measurement.mean_reprojection_bbox_nme == pytest.approx(
        0.007082
    )
    assert measurement.cross_view_identity_shape_nme == pytest.approx(
        0.064978
    )

    assert measurement.focal_identifiable is False
    assert measurement.ground_truth_3d_available is False
    assert measurement.volumetric_identity_proven is False
    assert measurement.processing_time_seconds == pytest.approx(
        1.457528
    )


def test_exposes_verified_aggregate_raw_measurements():
    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .mean_reprojection_iod_nme()
        == pytest.approx(
            0.025720
        )
    )

    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .mean_cross_view_identity_shape_nme()
        == pytest.approx(
            0.062304
        )
    )


def test_records_selected_identity_capacity():
    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .IDENTITY_MODEL_CAPACITY
        == 300
    )
    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .ACTIVE_IDENTITY_COMPONENT_COUNT
        == 90
    )


def test_records_current_evidence_limitations():
    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .all_focal_identifiable()
        is False
    )
    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .any_volumetric_identity_proven()
        is False
    )


def test_unknown_subject_is_rejected():
    with pytest.raises(
        KeyError,
        match="subject_03",
    ):
        (
            AtlasCanonicalHeadFlameBenchmarkEvidence
            .measurement_for_subject(
                "subject_03"
            )
        )


def test_catalog_does_not_expose_support_or_phase_9_decision():
    assert not hasattr(
        AtlasCanonicalHeadFlameBenchmarkEvidence,
        "candidate_observation",
    )
    assert not hasattr(
        AtlasCanonicalHeadFlameBenchmarkEvidence,
        "identity_preservation_support",
    )
    assert not hasattr(
        AtlasCanonicalHeadFlameBenchmarkEvidence,
        "decision",
    )
    assert not hasattr(
        AtlasCanonicalHeadFlameBenchmarkEvidence,
        "phase_9_authorized",
    )


def test_exposes_conservative_phase_8_10_evidence_coverage():
    coverage = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .coverage()
    )

    assert coverage.candidate_id == "flame-2023-open"

    assert coverage.identity_preservation_support == "PARTIAL"
    assert coverage.multi_view_consistency == "MEASURED"

    assert coverage.silhouette_profile_support == "MISSING"
    assert coverage.head_ratio_support == "MISSING"
    assert coverage.jaw_chin_support == "MISSING"
    assert coverage.nose_projection_support == "MISSING"
    assert coverage.orbital_cheek_volume_support == "MISSING"
    assert coverage.expression_separation_support == "MISSING"

    assert coverage.pose_separation_support == "PARTIAL"

    assert coverage.topology_suitability == "DIRECT"
    assert coverage.physical_suitability == "MISSING"
    assert coverage.apple_silicon_runtime_support == "DIRECT"
    assert coverage.reproducibility_support == "DIRECT"


def test_flame_coverage_does_not_fabricate_candidate_support():
    coverage = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .coverage()
    )

    assert not hasattr(coverage, "decision")
    assert not hasattr(coverage, "phase_9_authorized")
    assert not hasattr(coverage, "support_score")


def test_exposes_conservative_phase_8_10_evidence_coverage():
    coverage = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .coverage()
    )

    assert coverage.candidate_id == "flame-2023-open"

    assert coverage.identity_preservation_support == "PARTIAL"
    assert coverage.multi_view_consistency == "MEASURED"

    assert coverage.silhouette_profile_support == "MISSING"
    assert coverage.head_ratio_support == "MISSING"
    assert coverage.jaw_chin_support == "MISSING"
    assert coverage.nose_projection_support == "MISSING"
    assert coverage.orbital_cheek_volume_support == "MISSING"
    assert coverage.expression_separation_support == "MISSING"

    assert coverage.pose_separation_support == "PARTIAL"

    assert coverage.topology_suitability == "DIRECT"
    assert coverage.physical_suitability == "MISSING"
    assert coverage.apple_silicon_runtime_support == "DIRECT"
    assert coverage.reproducibility_support == "DIRECT"


def test_flame_coverage_does_not_fabricate_candidate_support():
    coverage = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .coverage()
    )

    assert not hasattr(coverage, "decision")
    assert not hasattr(coverage, "phase_9_authorized")
    assert not hasattr(coverage, "support_score")


# === PHASE 8.10 HELD-OUT BENCHMARK C RAW EVIDENCE ===

from CORE.atlas_canonical_head_held_out_view_observation import (
    AtlasCanonicalHeadHeldOutViewObservation,
)


def test_exposes_six_verified_held_out_view_observations():
    observations = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .held_out_observations()
    )

    assert len(observations) == 6

    assert all(
        isinstance(
            item,
            AtlasCanonicalHeadHeldOutViewObservation,
        )
        for item in observations
    )

    assert tuple(
        (
            item.subject_id,
            item.training_view_ids,
            item.held_out_view_id,
        )
        for item in observations
    ) == (
        ("subject_01", ("side_a", "side_b"), "front"),
        ("subject_01", ("front", "side_b"), "side_a"),
        ("subject_01", ("front", "side_a"), "side_b"),
        ("subject_02", ("side_a", "side_b"), "front"),
        ("subject_02", ("front", "side_b"), "side_a"),
        ("subject_02", ("front", "side_a"), "side_b"),
    )


@pytest.mark.parametrize(
    (
        "subject_id",
        "held_out_view_id",
        "expected_iod_nme",
        "expected_bbox_nme",
        "expected_processing_time",
    ),
    (
        ("subject_01", "front", 0.025737053, 0.009386448, 10.257207),
        ("subject_01", "side_a", 0.042736096, 0.010860442, 10.775558),
        ("subject_01", "side_b", 0.038976068, 0.010278185, 10.701019),
        ("subject_02", "front", 0.038987713, 0.014025643, 16.549599),
        ("subject_02", "side_a", 0.037416831, 0.011151774, 13.301181),
        ("subject_02", "side_b", 0.031452767, 0.008749089, 11.974395),
    ),
)
def test_preserves_verified_held_out_raw_measurements(
    subject_id,
    held_out_view_id,
    expected_iod_nme,
    expected_bbox_nme,
    expected_processing_time,
):
    observation = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .held_out_observation(
            subject_id=subject_id,
            held_out_view_id=held_out_view_id,
        )
    )

    assert observation.candidate_id == "flame-2023-open"
    assert observation.shared_identity_component_count == 90
    assert observation.identity_locked is True
    assert observation.held_out_pose_camera_only is True
    assert observation.expression_fixed_neutral is True
    assert observation.projection_model == "weak_perspective"
    assert observation.optimizer_success is True

    assert observation.held_out_reprojection_iod_nme == pytest.approx(
        expected_iod_nme
    )
    assert observation.held_out_reprojection_bbox_nme == pytest.approx(
        expected_bbox_nme
    )
    assert observation.processing_time_seconds == pytest.approx(
        expected_processing_time
    )


def test_exposes_held_out_observations_by_subject():
    subject_01 = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .held_out_observations_for_subject(
            "subject_01"
        )
    )
    subject_02 = (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .held_out_observations_for_subject(
            "subject_02"
        )
    )

    assert tuple(
        item.held_out_view_id
        for item in subject_01
    ) == ("front", "side_a", "side_b")

    assert tuple(
        item.held_out_view_id
        for item in subject_02
    ) == ("front", "side_a", "side_b")


def test_exposes_verified_aggregate_held_out_metrics():
    expected_iod = (
        0.025737053
        + 0.042736096
        + 0.038976068
        + 0.038987713
        + 0.037416831
        + 0.031452767
    ) / 6.0

    expected_bbox = (
        0.009386448
        + 0.010860442
        + 0.010278185
        + 0.014025643
        + 0.011151774
        + 0.008749089
    ) / 6.0

    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .mean_held_out_reprojection_iod_nme()
        == pytest.approx(expected_iod)
    )

    assert (
        AtlasCanonicalHeadFlameBenchmarkEvidence
        .mean_held_out_reprojection_bbox_nme()
        == pytest.approx(expected_bbox)
    )


def test_unknown_held_out_observation_is_rejected():
    with pytest.raises(KeyError):
        (
            AtlasCanonicalHeadFlameBenchmarkEvidence
            .held_out_observation(
                subject_id="subject_03",
                held_out_view_id="front",
            )
        )
