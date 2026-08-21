from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_benchmark_measurement_observation import (
    AtlasCanonicalHeadBenchmarkMeasurementObservation,
)


def _measurement(**overrides):
    values = {
        "measurement_id": "flame-subject-01",
        "candidate_id": "flame-2023-open",
        "subject_id": "subject-01",
        "view_count": 3,
        "landmarks_per_view": 105,
        "mean_reprojection_iod_nme": 0.027984,
        "mean_reprojection_bbox_nme": 0.007818,
        "cross_view_identity_shape_nme": 0.057514,
        "focal_identifiable": False,
        "ground_truth_3d_available": False,
        "volumetric_identity_proven": False,
        "processing_time_seconds": 1.407287,
    }
    values.update(overrides)

    return AtlasCanonicalHeadBenchmarkMeasurementObservation(
        **values
    )


def test_preserves_real_raw_benchmark_measurements():
    measurement = _measurement()

    assert measurement.measurement_id == "flame-subject-01"
    assert measurement.candidate_id == "flame-2023-open"
    assert measurement.subject_id == "subject-01"
    assert measurement.view_count == 3
    assert measurement.landmarks_per_view == 105
    assert measurement.mean_reprojection_iod_nme == pytest.approx(
        0.027984
    )
    assert measurement.mean_reprojection_bbox_nme == pytest.approx(
        0.007818
    )
    assert measurement.cross_view_identity_shape_nme == pytest.approx(
        0.057514
    )
    assert measurement.focal_identifiable is False
    assert measurement.ground_truth_3d_available is False
    assert measurement.volumetric_identity_proven is False


@pytest.mark.parametrize(
    "field_name",
    (
        "measurement_id",
        "candidate_id",
        "subject_id",
    ),
)
def test_identifiers_must_be_non_blank(field_name):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _measurement(**{field_name: "   "})


@pytest.mark.parametrize(
    "field_name",
    (
        "view_count",
        "landmarks_per_view",
    ),
)
@pytest.mark.parametrize(
    "value",
    (0, -1),
)
def test_counts_must_be_positive(field_name, value):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _measurement(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    (
        "mean_reprojection_iod_nme",
        "mean_reprojection_bbox_nme",
        "cross_view_identity_shape_nme",
        "processing_time_seconds",
    ),
)
@pytest.mark.parametrize(
    "value",
    (-0.01, float("nan"), float("inf")),
)
def test_numeric_measurements_must_be_finite_and_nonnegative(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _measurement(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    (
        "focal_identifiable",
        "ground_truth_3d_available",
        "volumetric_identity_proven",
    ),
)
def test_evidence_flags_must_be_boolean(field_name):
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _measurement(**{field_name: 1})


def test_volumetric_identity_cannot_be_proven_without_3d_ground_truth():
    with pytest.raises(
        ValueError,
        match="ground_truth_3d_available",
    ):
        _measurement(
            ground_truth_3d_available=False,
            volumetric_identity_proven=True,
        )


def test_measurement_is_immutable():
    measurement = _measurement()

    with pytest.raises(FrozenInstanceError):
        measurement.mean_reprojection_iod_nme = 0.0


def test_raw_measurement_does_not_claim_support_or_gate_decision():
    measurement = _measurement()

    assert not hasattr(
        measurement,
        "identity_preservation_support",
    )
    assert not hasattr(
        measurement,
        "multi_view_consistency",
    )
    assert not hasattr(
        measurement,
        "pose_separation_support",
    )
    assert not hasattr(
        measurement,
        "decision",
    )
    assert not hasattr(
        measurement,
        "phase_9_authorized",
    )
