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
