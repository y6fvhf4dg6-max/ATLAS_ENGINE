import numpy as np
import pytest

from CORE.atlas_canonical_head_metric_ground_truth_observation import (
    AtlasCanonicalHeadMetricGroundTruthObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "metric-gt-01",
        "subject_id": "subject-01",
        "source_id": "benchmark-source-a",
        "units": "mm",
        "ground_truth_vertices": np.asarray(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        "ground_truth_faces": (
            (0, 1, 2),
        ),
        "reconstruction_vertices": np.asarray(
            [
                [0.0, 0.0, 0.1],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        "reconstruction_faces": (
            (0, 1, 2),
        ),
        "source_provenance_state": "VERIFIED",
        "evaluation_license_state": "ACCEPTABLE",
        "evaluation_use_only": True,
        "acquisition_modality": "IMAGE_BASED_MULTIVIEW_RECONSTRUCTION",
        "acquisition_system": "RealityCapture 1.4.2.117426",
        "acquisition_manufacturer": "UNRESOLVED",
        "ground_truth_surface_origin": "RECONSTRUCTED_SENSOR_DERIVED_SURFACE",
        "capture_expression": "NEUTRAL",
        "capture_pose": "WALKING",
        "capture_session_state": "UNRESOLVED",
        "calibration_state": "UNRESOLVED",
        "ground_truth_admissibility_state": "BLOCKED",
    }
    values.update(overrides)
    return AtlasCanonicalHeadMetricGroundTruthObservation(**values)


def test_accepts_metric_ground_truth_observation():
    observation = _observation()

    assert observation.observation_id == "metric-gt-01"
    assert observation.subject_id == "subject-01"
    assert observation.source_id == "benchmark-source-a"
    assert observation.units == "mm"
    assert observation.source_provenance_state == "VERIFIED"
    assert observation.evaluation_license_state == "ACCEPTABLE"
    assert observation.evaluation_use_only is True


def test_requires_millimetre_units():
    with pytest.raises(ValueError, match="units"):
        _observation(units="px")


def test_rejects_nonfinite_ground_truth_vertices():
    vertices = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [np.nan, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    with pytest.raises(ValueError, match="ground_truth_vertices"):
        _observation(ground_truth_vertices=vertices)


def test_rejects_nonfinite_reconstruction_vertices():
    vertices = np.asarray(
        [
            [0.0, 0.0, 0.0],
            [1.0, np.inf, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )

    with pytest.raises(ValueError, match="reconstruction_vertices"):
        _observation(reconstruction_vertices=vertices)


def test_requires_boolean_evaluation_use_only():
    with pytest.raises(TypeError, match="evaluation_use_only"):
        _observation(evaluation_use_only="yes")


def test_normalizes_metric_ground_truth_policy_states():
    observation = _observation(
        source_provenance_state=" verified ",
        evaluation_license_state=" acceptable ",
    )

    assert observation.source_provenance_state == "VERIFIED"
    assert observation.evaluation_license_state == "ACCEPTABLE"


def test_rejects_unknown_source_provenance_state():
    with pytest.raises(ValueError, match="source_provenance_state"):
        _observation(source_provenance_state="MAYBE")


def test_rejects_unknown_evaluation_license_state():
    with pytest.raises(ValueError, match="evaluation_license_state"):
        _observation(evaluation_license_state="MAYBE")

def test_accepts_source_qualification_metadata():
    observation = _observation()

    assert observation.acquisition_modality == "IMAGE_BASED_MULTIVIEW_RECONSTRUCTION"
    assert observation.acquisition_system == "RealityCapture 1.4.2.117426"
    assert observation.acquisition_manufacturer == "UNRESOLVED"
    assert observation.ground_truth_surface_origin == "RECONSTRUCTED_SENSOR_DERIVED_SURFACE"
    assert observation.capture_expression == "NEUTRAL"
    assert observation.capture_pose == "WALKING"
    assert observation.capture_session_state == "UNRESOLVED"
    assert observation.calibration_state == "UNRESOLVED"
    assert observation.ground_truth_admissibility_state == "BLOCKED"


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("acquisition_modality", "MAYBE"),
        ("ground_truth_surface_origin", "MAYBE"),
        ("capture_session_state", "MAYBE"),
        ("calibration_state", "MAYBE"),
        ("ground_truth_admissibility_state", "MAYBE"),
    ),
)
def test_rejects_unknown_source_qualification_states(field_name, value):
    with pytest.raises(ValueError, match=field_name):
        _observation(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    (
        "acquisition_system",
        "acquisition_manufacturer",
        "capture_expression",
        "capture_pose",
    ),
)
def test_rejects_blank_source_qualification_text(field_name):
    with pytest.raises(ValueError, match=field_name):
        _observation(**{field_name: "   "})


def test_allows_explicit_unresolved_source_qualification():
    observation = _observation(
        acquisition_modality="UNRESOLVED",
        acquisition_system="UNRESOLVED",
        acquisition_manufacturer="UNRESOLVED",
        ground_truth_surface_origin="UNRESOLVED",
        capture_expression="UNRESOLVED",
        capture_pose="UNRESOLVED",
        capture_session_state="UNRESOLVED",
        calibration_state="UNRESOLVED",
        ground_truth_admissibility_state="UNRESOLVED",
    )

    assert observation.acquisition_modality == "UNRESOLVED"
    assert observation.acquisition_system == "UNRESOLVED"
    assert observation.acquisition_manufacturer == "UNRESOLVED"
    assert observation.ground_truth_surface_origin == "UNRESOLVED"
    assert observation.capture_expression == "UNRESOLVED"
    assert observation.capture_pose == "UNRESOLVED"
    assert observation.capture_session_state == "UNRESOLVED"
    assert observation.calibration_state == "UNRESOLVED"
    assert observation.ground_truth_admissibility_state == "UNRESOLVED"
