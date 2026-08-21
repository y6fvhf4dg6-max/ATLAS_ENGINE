import pytest

from CORE.atlas_canonical_head_identity_confidence_gate import (
    AtlasCanonicalHeadIdentityConfidenceGate,
)
from CORE.atlas_canonical_head_identity_confidence_observation import (
    AtlasCanonicalHeadIdentityConfidenceObservation,
)


def _observation(**overrides):
    values = {
        "observation_id": "identity-evidence-001",
        "view_coverage_support": 0.90,
        "multi_view_consistency": 0.86,
        "silhouette_support": 0.84,
        "profile_support": 0.80,
        "identity_shape_support": 0.88,
        "landmark_support": 0.92,
        "asymmetry_support": 0.72,
    }
    values.update(overrides)
    return AtlasCanonicalHeadIdentityConfidenceObservation(**values)


def test_strong_identity_evidence_returns_go():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation()
    )

    assert result.decision == "GO"
    assert result.production_status == "ACCEPTED"
    assert result.confidence_class == "STRONG"
    assert result.blocked_reasons == ()


def test_limited_identity_evidence_returns_hold_and_blocks_production():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            profile_support=0.58,
        )
    )

    assert result.decision == "HOLD"
    assert result.production_status == "BLOCKED"
    assert result.confidence_class == "LIMITED"
    assert result.blocked_reasons == (
        "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE",
    )


def test_weak_identity_shape_support_returns_reject():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            identity_shape_support=0.30,
        )
    )

    assert result.decision == "REJECT"
    assert result.production_status == "BLOCKED"
    assert result.confidence_class == "INSUFFICIENT"
    assert result.blocked_reasons == (
        "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE",
    )


def test_high_landmark_support_cannot_override_weak_identity_shape():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            landmark_support=1.0,
            identity_shape_support=0.30,
        )
    )

    assert result.decision == "REJECT"
    assert result.production_status == "BLOCKED"


def test_low_multi_view_consistency_cannot_return_go():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            multi_view_consistency=0.50,
        )
    )

    assert result.decision == "HOLD"
    assert result.production_status == "BLOCKED"


def test_severely_inconsistent_multiview_returns_reject():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            multi_view_consistency=0.20,
        )
    )

    assert result.decision == "REJECT"
    assert result.production_status == "BLOCKED"


def test_missing_profile_strength_cannot_be_hidden_by_other_high_channels():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            view_coverage_support=1.0,
            multi_view_consistency=1.0,
            silhouette_support=1.0,
            profile_support=0.40,
            identity_shape_support=1.0,
            landmark_support=1.0,
            asymmetry_support=1.0,
        )
    )

    assert result.decision != "GO"
    assert result.production_status == "BLOCKED"


def test_asymmetry_support_may_be_limited_without_rejecting_identity():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            asymmetry_support=0.35,
        )
    )

    assert result.decision == "HOLD"
    assert result.production_status == "BLOCKED"


def test_rejects_wrong_observation_type():
    with pytest.raises(
        TypeError,
        match="AtlasCanonicalHeadIdentityConfidenceObservation",
    ):
        AtlasCanonicalHeadIdentityConfidenceGate.evaluate({})


def test_result_does_not_claim_geometry_provider_or_likeness_score():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation()
    )

    assert not hasattr(result, "vertices")
    assert not hasattr(result, "faces")
    assert not hasattr(result, "provider_id")
    assert not hasattr(result, "likeness_score")
    assert not hasattr(result, "identity_shape")


def test_hold_reports_specific_limited_identity_channel():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            profile_support=0.58,
        )
    )

    assert result.failure_reasons == (
        "LIMITED_PROFILE_SUPPORT",
    )


def test_reject_reports_specific_insufficient_identity_channel():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            identity_shape_support=0.30,
        )
    )

    assert result.failure_reasons == (
        "INSUFFICIENT_IDENTITY_SHAPE_SUPPORT",
    )


def test_multiple_failure_reasons_are_deterministic():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            multi_view_consistency=0.50,
            profile_support=0.58,
            asymmetry_support=0.40,
        )
    )

    assert result.failure_reasons == (
        "LIMITED_MULTI_VIEW_CONSISTENCY",
        "LIMITED_PROFILE_SUPPORT",
        "LIMITED_ASYMMETRY_SUPPORT",
    )


def test_go_has_no_failure_reasons():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation()
    )

    assert result.failure_reasons == ()


def test_landmark_support_alone_does_not_create_identity_failure_reason():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            landmark_support=0.05,
        )
    )

    assert result.decision == "GO"
    assert result.failure_reasons == ()


def test_critical_channel_just_below_reject_threshold_is_rejected():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            profile_support=0.349999,
        )
    )

    assert result.decision == "REJECT"
    assert result.confidence_class == "INSUFFICIENT"
    assert result.failure_reasons == (
        "INSUFFICIENT_PROFILE_SUPPORT",
    )


def test_critical_channel_at_reject_threshold_is_hold_not_reject():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            profile_support=0.35,
        )
    )

    assert result.decision == "HOLD"
    assert result.confidence_class == "LIMITED"
    assert result.failure_reasons == (
        "LIMITED_PROFILE_SUPPORT",
    )


def test_all_decision_channels_at_go_threshold_are_accepted():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            view_coverage_support=0.70,
            multi_view_consistency=0.70,
            silhouette_support=0.70,
            profile_support=0.70,
            identity_shape_support=0.70,
            asymmetry_support=0.70,
        )
    )

    assert result.decision == "GO"
    assert result.production_status == "ACCEPTED"
    assert result.confidence_class == "STRONG"
    assert result.failure_reasons == ()


def test_severely_weak_asymmetry_alone_remains_hold_not_reject():
    result = AtlasCanonicalHeadIdentityConfidenceGate.evaluate(
        _observation(
            asymmetry_support=0.0,
        )
    )

    assert result.decision == "HOLD"
    assert result.production_status == "BLOCKED"
    assert result.confidence_class == "LIMITED"
    assert result.failure_reasons == (
        "LIMITED_ASYMMETRY_SUPPORT",
    )
