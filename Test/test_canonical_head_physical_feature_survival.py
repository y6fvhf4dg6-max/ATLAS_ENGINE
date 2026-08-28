from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_physical_feature_survival import (
    AtlasCanonicalHeadPhysicalFeatureSurvival,
)


def _survival(**overrides):
    values = {
        "representation_id": "person-a-relief-v1",
        "representation_kind": "relief",
        "feature_name": "nose_edge_profile",
        "measurement_mm": 0.62,
        "minimum_required_mm": 0.40,
        "measurement_state": "OBSERVED",
        "measurement_provenance": "synthetic physical fixture",
    }
    values.update(overrides)
    return AtlasCanonicalHeadPhysicalFeatureSurvival(**values)


@pytest.mark.parametrize(
    "representation_kind",
    (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_accepts_required_representation_kinds(representation_kind):
    survival = _survival(representation_kind=representation_kind)

    assert survival.representation_kind == representation_kind


@pytest.mark.parametrize(
    "feature_name",
    (
        "nose_edge_profile",
        "nose_base",
        "upper_lip_boundary",
        "lower_lip_boundary",
        "left_eyelid_orbital_boundary",
        "right_eyelid_orbital_boundary",
        "jaw_edge",
        "chin",
        "left_ear_structure",
        "right_ear_structure",
    ),
)
def test_accepts_required_identity_bearing_features(feature_name):
    survival = _survival(feature_name=feature_name)

    assert survival.feature_name == feature_name


def test_rejects_unknown_feature():
    with pytest.raises(ValueError, match="feature_name"):
        _survival(feature_name="generic_face_detail")


def test_observed_feature_survives_at_or_above_minimum():
    survival = _survival(
        measurement_mm=0.40,
        minimum_required_mm=0.40,
        measurement_state="OBSERVED",
    )

    assert survival.survival_state == "SURVIVES"


def test_observed_feature_is_below_minimum_when_too_small():
    survival = _survival(
        measurement_mm=0.39,
        minimum_required_mm=0.40,
        measurement_state="OBSERVED",
    )

    assert survival.survival_state == "BELOW_MINIMUM"


@pytest.mark.parametrize(
    ("measurement_state", "expected_survival_state"),
    (
        ("UNRESOLVED", "UNRESOLVED"),
        ("NOT_APPLICABLE", "NOT_APPLICABLE"),
    ),
)
def test_non_observed_measurement_states_do_not_fabricate_mm(
    measurement_state,
    expected_survival_state,
):
    survival = _survival(
        measurement_mm=None,
        measurement_state=measurement_state,
    )

    assert survival.measurement_mm is None
    assert survival.survival_state == expected_survival_state


@pytest.mark.parametrize(
    "measurement_state",
    (
        "UNRESOLVED",
        "NOT_APPLICABLE",
    ),
)
def test_non_observed_state_rejects_numeric_measurement(measurement_state):
    with pytest.raises(ValueError, match="measurement_mm"):
        _survival(
            measurement_mm=0.50,
            measurement_state=measurement_state,
        )


def test_observed_state_requires_measurement():
    with pytest.raises(ValueError, match="measurement_mm"):
        _survival(
            measurement_mm=None,
            measurement_state="OBSERVED",
        )


@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -0.01,
        float("nan"),
        float("inf"),
    ),
)
def test_observed_measurement_must_be_positive_finite(value):
    with pytest.raises(ValueError, match="measurement_mm"):
        _survival(
            measurement_mm=value,
            measurement_state="OBSERVED",
        )


@pytest.mark.parametrize(
    "value",
    (
        0.0,
        -0.01,
        float("nan"),
        float("inf"),
    ),
)
def test_minimum_required_mm_must_be_positive_finite(value):
    with pytest.raises(ValueError, match="minimum_required_mm"):
        _survival(minimum_required_mm=value)


def test_measurement_state_is_normalized():
    survival = _survival(
        measurement_mm=None,
        measurement_state="  not applicable  ",
    )

    assert survival.measurement_state == "NOT_APPLICABLE"
    assert survival.survival_state == "NOT_APPLICABLE"


def test_rejects_unknown_measurement_state():
    with pytest.raises(ValueError, match="measurement_state"):
        _survival(measurement_state="ESTIMATED")


def test_requires_measurement_provenance():
    with pytest.raises(ValueError, match="measurement_provenance"):
        _survival(measurement_provenance="   ")


def test_requires_representation_id():
    with pytest.raises(ValueError, match="representation_id"):
        _survival(representation_id="   ")


def test_record_is_immutable():
    survival = _survival()

    with pytest.raises(FrozenInstanceError):
        survival.measurement_mm = 0.50


def test_contract_does_not_claim_identity_or_production_decision():
    survival = _survival()

    assert not hasattr(survival, "likeness_score")
    assert not hasattr(survival, "identity_preservation_support")
    assert not hasattr(survival, "support_score")
    assert not hasattr(survival, "decision")
    assert not hasattr(survival, "production_status")
    assert not hasattr(survival, "phase_9_authorized")
