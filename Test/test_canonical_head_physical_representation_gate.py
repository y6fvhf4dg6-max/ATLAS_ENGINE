import pytest

from CORE.atlas_canonical_head_physical_representation_gate import (
    AtlasCanonicalHeadPhysicalRepresentationGate,
)
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


def test_strong_physical_representation_is_accepted():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation()
    )

    assert result.decision == "GO"
    assert result.production_status == "ACCEPTED"
    assert result.blocked_reasons == ()
    assert result.failure_reasons == ()


def test_too_small_head_height_blocks_representation():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            target_head_height_mm=14.0,
        )
    )

    assert result.decision == "REJECT"
    assert result.production_status == "BLOCKED"
    assert "BLOCKED_PHYSICAL_IDENTITY_REPRESENTATION" in result.blocked_reasons
    assert "INSUFFICIENT_HEAD_HEIGHT" in result.failure_reasons


def test_too_small_minimum_feature_blocks_representation():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            minimum_feature_mm=0.25,
        )
    )

    assert result.decision == "REJECT"
    assert "INSUFFICIENT_PHYSICAL_FEATURE_SIZE" in result.failure_reasons


def test_weak_identity_preservation_blocks_representation():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            identity_preservation_support=0.45,
        )
    )

    assert result.decision == "REJECT"
    assert "INSUFFICIENT_IDENTITY_PRESERVATION" in result.failure_reasons


def test_limited_profile_preservation_returns_hold():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            profile_preservation_support=0.62,
        )
    )

    assert result.decision == "HOLD"
    assert result.production_status == "BLOCKED"
    assert result.failure_reasons == (
        "LIMITED_PROFILE_PRESERVATION",
    )


def test_excessive_lod_returns_hold():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            lod_level=5,
        )
    )

    assert result.decision == "HOLD"
    assert result.production_status == "BLOCKED"
    assert "LIMITED_BY_LOD" in result.failure_reasons


@pytest.mark.parametrize(
    "representation_kind",
    (
        "relief",
        "bust",
        "figurine_head",
        "story_kit_component",
    ),
)
def test_all_supported_representation_kinds_use_same_identity_gate(
    representation_kind,
):
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            representation_kind=representation_kind,
        )
    )

    assert result.decision == "GO"
    assert result.production_status == "ACCEPTED"


def test_rejects_wrong_observation_type():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadPhysicalRepresentationObservation",
    ):
        AtlasCanonicalHeadPhysicalRepresentationGate.evaluate({})


def test_result_does_not_claim_geometry_provider_or_likeness_score():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation()
    )

    assert not hasattr(result, "vertices")
    assert not hasattr(result, "faces")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "likeness_score")


def test_head_height_at_minimum_is_not_rejected():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            target_head_height_mm=18.0,
        )
    )

    assert result.decision == "GO"
    assert "INSUFFICIENT_HEAD_HEIGHT" not in result.failure_reasons


def test_minimum_feature_at_threshold_is_not_rejected():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            minimum_feature_mm=0.40,
        )
    )

    assert result.decision == "GO"
    assert "INSUFFICIENT_PHYSICAL_FEATURE_SIZE" not in result.failure_reasons


def test_identity_preservation_just_below_reject_threshold_is_rejected():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            identity_preservation_support=0.499999,
        )
    )

    assert result.decision == "REJECT"
    assert result.failure_reasons == (
        "INSUFFICIENT_IDENTITY_PRESERVATION",
    )


def test_identity_preservation_at_reject_threshold_is_hold():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            identity_preservation_support=0.50,
        )
    )

    assert result.decision == "HOLD"
    assert result.failure_reasons == (
        "LIMITED_IDENTITY_PRESERVATION",
    )


def test_all_preservation_channels_at_go_threshold_are_accepted():
    result = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            identity_preservation_support=0.70,
            silhouette_preservation_support=0.70,
            profile_preservation_support=0.70,
        )
    )

    assert result.decision == "GO"
    assert result.production_status == "ACCEPTED"


def test_lod_level_four_is_accepted_but_five_is_hold():
    accepted = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            lod_level=4,
        )
    )
    limited = AtlasCanonicalHeadPhysicalRepresentationGate.evaluate(
        _observation(
            lod_level=5,
        )
    )

    assert accepted.decision == "GO"
    assert limited.decision == "HOLD"
    assert limited.failure_reasons == (
        "LIMITED_BY_LOD",
    )
