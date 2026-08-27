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
        "acquisition_modality": "MULTIVIEW_IMAGE_CAPTURE",
        "acquisition_system": "UNRESOLVED",
        "acquisition_manufacturer": "UNRESOLVED",
        "reconstruction_modality": "IMAGE_BASED_MULTIVIEW_RECONSTRUCTION",
        "reconstruction_software": "RealityCapture",
        "reconstruction_software_version": "1.4.2.117426",
        "ground_truth_surface_origin": "RECONSTRUCTED_SENSOR_DERIVED_SURFACE",
        "ground_truth_strength_state": "DERIVED_SENSOR",
        "subject_match_state": "VERIFIED",
        "capture_session_relation": "UNRESOLVED",
        "capture_expression": "NEUTRAL",
        "capture_pose": "WALKING",
        "capture_date": "UNRESOLVED",
        "physical_resolution_state": "UNRESOLVED",
        "physical_resolution_reference": "UNRESOLVED",
        "calibration_state": "UNRESOLVED",
        "source_provenance_reference": "HSRD-100/HSR0015-Body-035",
        "license_reference": "UNRESOLVED",
        "license_restrictions": "UNRESOLVED",
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

def test_accepts_complete_source_qualification_metadata():
    observation = _observation()

    assert observation.acquisition_modality == "MULTIVIEW_IMAGE_CAPTURE"
    assert observation.acquisition_system == "UNRESOLVED"
    assert observation.acquisition_manufacturer == "UNRESOLVED"
    assert (
        observation.reconstruction_modality
        == "IMAGE_BASED_MULTIVIEW_RECONSTRUCTION"
    )
    assert observation.reconstruction_software == "RealityCapture"
    assert observation.reconstruction_software_version == "1.4.2.117426"
    assert (
        observation.ground_truth_surface_origin
        == "RECONSTRUCTED_SENSOR_DERIVED_SURFACE"
    )
    assert observation.ground_truth_strength_state == "DERIVED_SENSOR"
    assert observation.subject_match_state == "VERIFIED"
    assert observation.capture_session_relation == "UNRESOLVED"
    assert observation.capture_expression == "NEUTRAL"
    assert observation.capture_pose == "WALKING"
    assert observation.capture_date == "UNRESOLVED"
    assert observation.physical_resolution_state == "UNRESOLVED"
    assert observation.physical_resolution_reference == "UNRESOLVED"
    assert observation.calibration_state == "UNRESOLVED"
    assert (
        observation.source_provenance_reference
        == "HSRD-100/HSR0015-Body-035"
    )
    assert observation.license_reference == "UNRESOLVED"
    assert observation.license_restrictions == "UNRESOLVED"
    assert observation.ground_truth_admissibility_state == "BLOCKED"


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("acquisition_modality", "MAYBE"),
        ("reconstruction_modality", "MAYBE"),
        ("ground_truth_surface_origin", "MAYBE"),
        ("ground_truth_strength_state", "MAYBE"),
        ("subject_match_state", "MAYBE"),
        ("capture_session_relation", "MAYBE"),
        ("physical_resolution_state", "MAYBE"),
        ("calibration_state", "MAYBE"),
        ("ground_truth_admissibility_state", "MAYBE"),
    ),
)
def test_rejects_unknown_complete_source_qualification_states(
    field_name,
    value,
):
    with pytest.raises(ValueError, match=field_name):
        _observation(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    (
        "acquisition_system",
        "acquisition_manufacturer",
        "reconstruction_software",
        "reconstruction_software_version",
        "capture_expression",
        "capture_pose",
        "capture_date",
        "physical_resolution_reference",
        "source_provenance_reference",
        "license_reference",
        "license_restrictions",
    ),
)
def test_rejects_blank_complete_source_qualification_text(field_name):
    with pytest.raises(ValueError, match=field_name):
        _observation(**{field_name: "   "})


def test_allows_explicit_unresolved_complete_source_qualification():
    observation = _observation(
        acquisition_modality="UNRESOLVED",
        acquisition_system="UNRESOLVED",
        acquisition_manufacturer="UNRESOLVED",
        reconstruction_modality="UNRESOLVED",
        reconstruction_software="UNRESOLVED",
        reconstruction_software_version="UNRESOLVED",
        ground_truth_surface_origin="UNRESOLVED",
        ground_truth_strength_state="UNRESOLVED",
        subject_match_state="UNRESOLVED",
        capture_session_relation="UNRESOLVED",
        capture_expression="UNRESOLVED",
        capture_pose="UNRESOLVED",
        capture_date="UNRESOLVED",
        physical_resolution_state="UNRESOLVED",
        physical_resolution_reference="UNRESOLVED",
        calibration_state="UNRESOLVED",
        source_provenance_reference="UNRESOLVED",
        license_reference="UNRESOLVED",
        license_restrictions="UNRESOLVED",
        ground_truth_admissibility_state="UNRESOLVED",
    )

    assert observation.acquisition_modality == "UNRESOLVED"
    assert observation.reconstruction_modality == "UNRESOLVED"
    assert observation.ground_truth_surface_origin == "UNRESOLVED"
    assert observation.ground_truth_strength_state == "UNRESOLVED"
    assert observation.subject_match_state == "UNRESOLVED"
    assert observation.capture_session_relation == "UNRESOLVED"
    assert observation.physical_resolution_state == "UNRESOLVED"
    assert observation.calibration_state == "UNRESOLVED"
    assert observation.ground_truth_admissibility_state == "UNRESOLVED"


@pytest.mark.parametrize(
    "surface_origin",
    (
        "RAW_SENSOR_DERIVED_SURFACE",
        "REGISTERED_SENSOR_DERIVED_SURFACE",
        "RECONSTRUCTED_SENSOR_DERIVED_SURFACE",
        "MODEL_FITTED_TO_SCAN_GEOMETRY",
        "GENERATED_OR_INFERRED_GEOMETRY",
        "UNRESOLVED",
    ),
)
def test_accepts_explicit_ground_truth_surface_origin_classes(surface_origin):
    observation = _observation(
        ground_truth_surface_origin=surface_origin,
    )

    assert observation.ground_truth_surface_origin == surface_origin
