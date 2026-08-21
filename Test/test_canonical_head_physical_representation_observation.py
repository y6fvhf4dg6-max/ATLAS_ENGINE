from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_physical_representation_observation import (
    AtlasCanonicalHeadPhysicalRepresentationObservation,
)


def _observation(**overrides):
    values = {
        "representation_id": "physical-head-001",
        "representation_kind": "relief",
        "target_head_height_mm": 42.0,
        "minimum_feature_mm": 0.8,
        "lod_level": 2,
        "identity_preservation_support": 0.88,
        "silhouette_preservation_support": 0.84,
        "profile_preservation_support": 0.78,
    }
    values.update(overrides)
    return AtlasCanonicalHeadPhysicalRepresentationObservation(**values)


def test_normalizes_representation_id_and_kind():
    observation = _observation(
        representation_id="  Head Output 001  ",
        representation_kind="  RELIEF  ",
    )

    assert observation.representation_id == "Head Output 001"
    assert observation.representation_kind == "relief"


@pytest.mark.parametrize(
    "representation_kind",
    (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_supported_representation_kinds_are_accepted(
    representation_kind,
):
    observation = _observation(
        representation_kind=representation_kind,
    )

    assert observation.representation_kind == representation_kind


def test_unknown_representation_kind_is_rejected():
    with pytest.raises(
        ValueError,
        match="representation_kind",
    ):
        _observation(
            representation_kind="generic_mesh",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "identity_preservation_support",
        "silhouette_preservation_support",
        "profile_preservation_support",
    ),
)
@pytest.mark.parametrize(
    "value",
    (-0.01, 1.01),
)
def test_preservation_support_channels_must_be_unit_interval(
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
        "target_head_height_mm",
        "minimum_feature_mm",
    ),
)
@pytest.mark.parametrize(
    "value",
    (0.0, -0.01),
)
def test_physical_dimensions_must_be_positive(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _observation(**{field_name: value})


def test_lod_level_must_be_nonnegative_integer():
    with pytest.raises(
        ValueError,
        match="lod_level",
    ):
        _observation(lod_level=-1)

    with pytest.raises(
        TypeError,
        match="lod_level",
    ):
        _observation(lod_level=1.5)


def test_observation_is_immutable():
    observation = _observation()

    with pytest.raises(FrozenInstanceError):
        observation.target_head_height_mm = 50.0


def test_observation_does_not_claim_gate_decision_or_geometry():
    observation = _observation()

    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "production_status")
    assert not hasattr(observation, "vertices")
    assert not hasattr(observation, "faces")
    assert not hasattr(observation, "provider_id")
    assert not hasattr(observation, "likeness_score")
