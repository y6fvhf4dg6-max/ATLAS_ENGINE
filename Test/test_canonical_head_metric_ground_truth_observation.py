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
        "evaluation_license_state": "UNRESOLVED",
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
        "calibration_reference": "UNRESOLVED",
        "known_reference_dimension_mm": None,
        "reference_uncertainty_mm": None,
        "calibration_date": "UNRESOLVED",
        "reconstruction_scale_factor": 1.0,
        "scale_transform_provenance": "UNRESOLVED",
        "scale_source": "UNRESOLVED",
        "scale_uncertainty_mm": None,
        "scale_uncertainty_propagation": "UNRESOLVED",
        "source_coordinate_frame": "UNRESOLVED",
        "target_coordinate_frame": "UNRESOLVED",
        "source_handedness": "UNRESOLVED",
        "target_handedness": "UNRESOLVED",
        "source_axis_definitions": (
            "UNRESOLVED_X",
            "UNRESOLVED_Y",
            "UNRESOLVED_Z",
        ),
        "target_axis_definitions": (
            "UNRESOLVED_X",
            "UNRESOLVED_Y",
            "UNRESOLVED_Z",
        ),
        "source_coordinate_origin": "UNRESOLVED",
        "target_coordinate_origin": "UNRESOLVED",
        "source_orientation": "UNRESOLVED",
        "target_orientation": "UNRESOLVED",
        "canonical_pose": "UNRESOLVED",
        "coordinate_transform_provenance": "UNRESOLVED",
        "transform_order": (
            "AXIS_PERMUTATION",
            "REFLECTION",
            "CANONICAL_POSE",
        ),
        "axis_permutation": (0, 1, 2),
        "reflection_state": "UNRESOLVED",
        "reflection_applied": None,
        "canonical_pose_transform": np.eye(4, dtype=np.float64),
        "round_trip_invertibility_state": "UNRESOLVED",
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
    assert observation.evaluation_license_state == "UNRESOLVED"
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
        license_reference="provider-license-reference",
        license_restrictions="evaluation use permitted",
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
        source_provenance_state="UNRESOLVED",
        evaluation_license_state="UNRESOLVED",
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
    ("surface_origin", "strength_state"),
    (
        ("RAW_SENSOR_DERIVED_SURFACE", "RAW_SENSOR"),
        ("REGISTERED_SENSOR_DERIVED_SURFACE", "REGISTERED_SENSOR"),
        ("RECONSTRUCTED_SENSOR_DERIVED_SURFACE", "DERIVED_SENSOR"),
        ("MODEL_FITTED_TO_SCAN_GEOMETRY", "MODEL_FITTED"),
        ("GENERATED_OR_INFERRED_GEOMETRY", "GENERATED_OR_INFERRED"),
        ("UNRESOLVED", "UNRESOLVED"),
    ),
)
def test_accepts_explicit_ground_truth_surface_origin_classes(
    surface_origin,
    strength_state,
):
    observation = _observation(
        ground_truth_surface_origin=surface_origin,
        ground_truth_strength_state=strength_state,
    )

    assert observation.ground_truth_surface_origin == surface_origin
    assert observation.ground_truth_strength_state == strength_state

# === ITEM 10.1 CROSS-FIELD QUALIFICATION INVARIANTS ===


@pytest.mark.parametrize(
    ("surface_origin", "strength_state"),
    (
        ("GENERATED_OR_INFERRED_GEOMETRY", "RAW_SENSOR"),
        ("MODEL_FITTED_TO_SCAN_GEOMETRY", "REGISTERED_SENSOR"),
        ("RAW_SENSOR_DERIVED_SURFACE", "GENERATED_OR_INFERRED"),
    ),
)
def test_rejects_incompatible_surface_origin_and_ground_truth_strength(
    surface_origin,
    strength_state,
):
    with pytest.raises(
        ValueError,
        match="ground_truth_surface_origin|ground_truth_strength_state",
    ):
        _observation(
            ground_truth_surface_origin=surface_origin,
            ground_truth_strength_state=strength_state,
        )


def test_verified_physical_resolution_requires_resolved_reference():
    with pytest.raises(
        ValueError,
        match="physical_resolution",
    ):
        _observation(
            physical_resolution_state="VERIFIED",
            physical_resolution_reference="UNRESOLVED",
        )


def test_verified_source_provenance_requires_resolved_reference():
    with pytest.raises(
        ValueError,
        match="source_provenance",
    ):
        _observation(
            source_provenance_state="VERIFIED",
            source_provenance_reference="UNRESOLVED",
        )


@pytest.mark.parametrize(
    ("license_reference", "license_restrictions"),
    (
        ("UNRESOLVED", "evaluation only"),
        ("provider-license-page", "UNRESOLVED"),
        ("UNRESOLVED", "UNRESOLVED"),
    ),
)
def test_acceptable_evaluation_license_requires_resolved_license_evidence(
    license_reference,
    license_restrictions,
):
    with pytest.raises(
        ValueError,
        match="license",
    ):
        _observation(
            evaluation_license_state="ACCEPTABLE",
            license_reference=license_reference,
            license_restrictions=license_restrictions,
        )

# === PHASE 8 ITEM 10.3 SCALE CALIBRATION ===


def test_accepts_explicit_scale_calibration_metadata():
    observation = _observation(
        calibration_reference="provider-calibration-record",
        known_reference_dimension_mm=100.0,
        reference_uncertainty_mm=0.25,
        calibration_date="2026-08-25",
        reconstruction_scale_factor=1.0,
        scale_transform_provenance="provider-declared-metric-coordinate-system",
        scale_source="DECLARED",
        scale_uncertainty_mm=0.25,
        scale_uncertainty_propagation="REFERENCE_UNCERTAINTY_CARRIED_FORWARD",
    )

    assert observation.calibration_reference == "provider-calibration-record"
    assert observation.known_reference_dimension_mm == pytest.approx(100.0)
    assert observation.reference_uncertainty_mm == pytest.approx(0.25)
    assert observation.calibration_date == "2026-08-25"
    assert observation.reconstruction_scale_factor == pytest.approx(1.0)
    assert observation.scale_transform_provenance == (
        "provider-declared-metric-coordinate-system"
    )
    assert observation.scale_source == "DECLARED"
    assert observation.scale_uncertainty_mm == pytest.approx(0.25)
    assert observation.scale_uncertainty_propagation == (
        "REFERENCE_UNCERTAINTY_CARRIED_FORWARD"
    )


@pytest.mark.parametrize(
    "scale_source",
    (
        "MEASURED",
        "DECLARED",
        "OPTIMIZED",
        "INFERRED",
        "UNRESOLVED",
    ),
)
def test_accepts_explicit_scale_source_states(scale_source):
    observation = _observation(
        calibration_reference="UNRESOLVED",
        known_reference_dimension_mm=None,
        reference_uncertainty_mm=None,
        calibration_date="UNRESOLVED",
        reconstruction_scale_factor=1.0,
        scale_transform_provenance="UNRESOLVED",
        scale_source=scale_source,
        scale_uncertainty_mm=None,
        scale_uncertainty_propagation="UNRESOLVED",
    )

    assert observation.scale_source == scale_source


def test_verified_calibration_requires_resolved_reference_and_date():
    with pytest.raises(
        ValueError,
        match="calibration",
    ):
        _observation(
            calibration_state="VERIFIED",
            calibration_reference="UNRESOLVED",
            known_reference_dimension_mm=100.0,
            reference_uncertainty_mm=0.25,
            calibration_date="UNRESOLVED",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="verified-transform",
            scale_source="MEASURED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="verified-propagation",
        )


def test_measured_scale_requires_known_reference_dimension():
    with pytest.raises(
        ValueError,
        match="known_reference_dimension",
    ):
        _observation(
            calibration_reference="physical-reference-a",
            known_reference_dimension_mm=None,
            reference_uncertainty_mm=0.25,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="measured-reference-scale",
            scale_source="MEASURED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="verified-propagation",
        )


def test_inferred_scale_cannot_establish_verified_calibration():
    with pytest.raises(
        ValueError,
        match="scale_source|calibration",
    ):
        _observation(
            calibration_state="VERIFIED",
            calibration_reference="physical-reference-a",
            known_reference_dimension_mm=100.0,
            reference_uncertainty_mm=0.25,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="typical-head-size-assumption",
            scale_source="INFERRED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="verified-propagation",
        )


def test_optimized_scale_cannot_be_relabelled_as_verified_physical_calibration():
    with pytest.raises(
        ValueError,
        match="scale_source|calibration",
    ):
        _observation(
            calibration_state="VERIFIED",
            calibration_reference="physical-reference-a",
            known_reference_dimension_mm=100.0,
            reference_uncertainty_mm=0.25,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.03,
            scale_transform_provenance="similarity-alignment-optimized-scale",
            scale_source="OPTIMIZED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="verified-propagation",
        )


def test_scale_uncertainty_requires_traceable_propagation():
    with pytest.raises(
        ValueError,
        match="scale_uncertainty_propagation",
    ):
        _observation(
            calibration_reference="physical-reference-a",
            known_reference_dimension_mm=100.0,
            reference_uncertainty_mm=0.25,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="measured-reference-scale",
            scale_source="MEASURED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="UNRESOLVED",
        )

# === PHASE 8 ITEM 10.3 CLOSURE CHALLENGE CORRECTIVE RED ===


def test_verified_calibration_requires_resolved_scale_transform_provenance():
    with pytest.raises(
        ValueError,
        match="scale_transform_provenance|calibration",
    ):
        _observation(
            calibration_state="VERIFIED",
            calibration_reference="physical-reference-a",
            known_reference_dimension_mm=100.0,
            reference_uncertainty_mm=0.25,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="UNRESOLVED",
            scale_source="MEASURED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="verified-propagation",
        )


def test_verified_calibration_requires_resolved_scale_source():
    with pytest.raises(
        ValueError,
        match="scale_source|calibration",
    ):
        _observation(
            calibration_state="VERIFIED",
            calibration_reference="physical-reference-a",
            known_reference_dimension_mm=100.0,
            reference_uncertainty_mm=0.25,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="physical-reference-scale-transform",
            scale_source="UNRESOLVED",
            scale_uncertainty_mm=0.25,
            scale_uncertainty_propagation="verified-propagation",
        )

# === PHASE 8 ITEM 10.3 DECLARED SCALE CALIBRATION FIREWALL ===


def test_declared_scale_cannot_establish_verified_physical_calibration():
    with pytest.raises(
        ValueError,
        match="scale_source|calibration",
    ):
        _observation(
            calibration_state="VERIFIED",
            calibration_reference="provider-declared-coordinate-units",
            known_reference_dimension_mm=None,
            reference_uncertainty_mm=None,
            calibration_date="2026-08-25",
            reconstruction_scale_factor=1.0,
            scale_transform_provenance="provider-declared-metric-scale",
            scale_source="DECLARED",
            scale_uncertainty_mm=None,
            scale_uncertainty_propagation="UNRESOLVED",
        )

# === PHASE 8 ITEM 10.4 COORDINATE-SYSTEM CONTRACT ===


def _coordinate_contract(**overrides):
    values = {
        "source_coordinate_frame": "HSRD_NATIVE_FRAME",
        "target_coordinate_frame": "ATLAS_METRIC_EVALUATION_FRAME",
        "source_handedness": "RIGHT_HANDED",
        "target_handedness": "RIGHT_HANDED",
        "source_axis_definitions": ("RIGHT", "UP", "FORWARD"),
        "target_axis_definitions": ("RIGHT", "UP", "FORWARD"),
        "source_coordinate_origin": "SOURCE_DEFINED",
        "target_coordinate_origin": "EVALUATION_DEFINED",
        "source_orientation": "SOURCE_NATIVE",
        "target_orientation": "CANONICAL_HEAD",
        "canonical_pose": "CANONICAL_HEAD",
        "coordinate_transform_provenance": "explicit-test-coordinate-contract",
        "transform_order": (
            "AXIS_PERMUTATION",
            "REFLECTION",
            "CANONICAL_POSE",
        ),
        "axis_permutation": (0, 1, 2),
        "reflection_state": "NOT_APPLIED",
        "reflection_applied": False,
        "canonical_pose_transform": np.eye(4, dtype=np.float64),
        "round_trip_invertibility_state": "VERIFIED",
    }
    values.update(overrides)
    return values


def test_accepts_explicit_coordinate_system_contract():
    values = _coordinate_contract()
    observation = _observation(**values)

    assert observation.source_coordinate_frame == "HSRD_NATIVE_FRAME"
    assert (
        observation.target_coordinate_frame
        == "ATLAS_METRIC_EVALUATION_FRAME"
    )
    assert observation.source_handedness == "RIGHT_HANDED"
    assert observation.target_handedness == "RIGHT_HANDED"
    assert observation.source_axis_definitions == (
        "RIGHT",
        "UP",
        "FORWARD",
    )
    assert observation.target_axis_definitions == (
        "RIGHT",
        "UP",
        "FORWARD",
    )
    assert observation.axis_permutation == (0, 1, 2)
    assert observation.reflection_state == "NOT_APPLIED"
    assert observation.reflection_applied is False
    assert observation.round_trip_invertibility_state == "VERIFIED"
    np.testing.assert_allclose(
        observation.canonical_pose_transform,
        np.eye(4),
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "source_coordinate_frame",
        "target_coordinate_frame",
        "source_coordinate_origin",
        "target_coordinate_origin",
        "source_orientation",
        "target_orientation",
        "canonical_pose",
        "coordinate_transform_provenance",
    ),
)
def test_coordinate_contract_requires_nonblank_text_fields(field_name):
    values = _coordinate_contract(**{field_name: "   "})

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _observation(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "source_handedness",
        "target_handedness",
    ),
)
def test_coordinate_contract_rejects_unknown_handedness(field_name):
    values = _coordinate_contract(**{field_name: "MAYBE_HANDED"})

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _observation(**values)


def test_axis_permutation_must_be_an_exact_permutation():
    values = _coordinate_contract(
        axis_permutation=(0, 0, 2),
    )

    with pytest.raises(
        ValueError,
        match="axis_permutation",
    ):
        _observation(**values)


def test_reflection_state_and_applied_flag_must_agree():
    values = _coordinate_contract(
        reflection_state="APPLIED",
        reflection_applied=False,
    )

    with pytest.raises(
        ValueError,
        match="reflection",
    ):
        _observation(**values)


def test_unresolved_reflection_cannot_claim_boolean_application_state():
    values = _coordinate_contract(
        reflection_state="UNRESOLVED",
        reflection_applied=False,
    )

    with pytest.raises(
        ValueError,
        match="reflection",
    ):
        _observation(**values)


def test_canonical_pose_transform_must_be_finite_four_by_four():
    values = _coordinate_contract(
        canonical_pose_transform=np.eye(3),
    )

    with pytest.raises(
        ValueError,
        match="canonical_pose_transform",
    ):
        _observation(**values)


def test_verified_round_trip_requires_invertible_canonical_pose_transform():
    transform = np.eye(4, dtype=np.float64)
    transform[2, 2] = 0.0

    values = _coordinate_contract(
        canonical_pose_transform=transform,
        round_trip_invertibility_state="VERIFIED",
    )

    with pytest.raises(
        ValueError,
        match="invertib|round_trip",
    ):
        _observation(**values)


def test_transform_order_must_explicitly_account_for_axis_and_reflection_steps():
    values = _coordinate_contract(
        transform_order=("CANONICAL_POSE",),
    )

    with pytest.raises(
        ValueError,
        match="transform_order",
    ):
        _observation(**values)
