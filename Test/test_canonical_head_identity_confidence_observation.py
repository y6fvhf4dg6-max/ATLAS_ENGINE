from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_identity_confidence_observation import (
    AtlasCanonicalHeadIdentityConfidenceObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "identity-evidence-001",
        "view_coverage_support": 0.90,
        "multi_view_consistency": 0.85,
        "silhouette_support": 0.80,
        "profile_support": 0.75,
        "identity_shape_support": 0.88,
        "landmark_support": 0.92,
        "asymmetry_support": 0.70,
    }
    values.update(overrides)
    return AtlasCanonicalHeadIdentityConfidenceObservation(**values)


def test_normalizes_observation_id():
    observation = _observation(
        observation_id="  Identity Evidence 001  "
    )

    assert observation.observation_id == "Identity Evidence 001"


@pytest.mark.parametrize(
    "field_name",
    (
        "view_coverage_support",
        "multi_view_consistency",
        "silhouette_support",
        "profile_support",
        "identity_shape_support",
        "landmark_support",
        "asymmetry_support",
    ),
)
@pytest.mark.parametrize(
    "value",
    (-0.01, 1.01),
)
def test_identity_support_channels_must_be_unit_interval(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _observation(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    (
        "view_coverage_support",
        "multi_view_consistency",
        "silhouette_support",
        "profile_support",
        "identity_shape_support",
        "landmark_support",
        "asymmetry_support",
    ),
)
def test_identity_support_channels_must_be_finite(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _observation(**{field_name: float("nan")})


def test_blank_observation_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="observation_id",
    ):
        _observation(observation_id="   ")


def test_observation_is_immutable():
    observation = _observation()

    with pytest.raises(FrozenInstanceError):
        observation.profile_support = 1.0


def test_landmark_support_is_not_identity_confidence():
    observation = _observation(
        landmark_support=1.0,
        identity_shape_support=0.25,
    )

    assert observation.landmark_support == 1.0
    assert observation.identity_shape_support == 0.25
    assert not hasattr(observation, "identity_confidence")


def test_contract_does_not_claim_gate_decision_geometry_or_provider():
    observation = _observation()

    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "production_status")
    assert not hasattr(observation, "vertices")
    assert not hasattr(observation, "faces")
    assert not hasattr(observation, "provider_id")
    assert not hasattr(observation, "likeness_score")
