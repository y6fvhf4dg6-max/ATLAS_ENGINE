import pytest

from CORE.atlas_canonical_head_evaluation_space_claim_boundary import (
    AtlasCanonicalHeadEvaluationSpaceClaimBoundary,
)


def test_exposes_four_explicit_evaluation_spaces():
    boundary = AtlasCanonicalHeadEvaluationSpaceClaimBoundary

    assert boundary.EVALUATION_SPACES == (
        "2d_observation",
        "canonical_model",
        "metric_3d_ground_truth",
        "physical_output",
    )


@pytest.mark.parametrize(
    ("evidence_kind", "claim_kind"),
    (
        ("landmark_fit", "surface_accuracy"),
        ("2d_reprojection", "metric_3d_accuracy"),
        (
            "canonical_model_displacement",
            "anatomical_millimetres",
        ),
        ("printability", "identity_preservation"),
        (
            "aggregate_improvement",
            "uniform_regional_improvement",
        ),
    ),
)
def test_blocks_forbidden_cross_space_claim_promotions(
    evidence_kind,
    claim_kind,
):
    result = AtlasCanonicalHeadEvaluationSpaceClaimBoundary.evaluate(
        evidence_kind=evidence_kind,
        claim_kind=claim_kind,
    )

    assert result.allowed is False
    assert result.status == "BLOCKED"
    assert result.failure_reason == "UNSUPPORTED_CLAIM_PROMOTION"


@pytest.mark.parametrize(
    ("evidence_kind", "claim_kind"),
    (
        ("landmark_fit", "landmark_fit"),
        ("2d_reprojection", "2d_reprojection"),
        (
            "canonical_model_displacement",
            "canonical_model_displacement",
        ),
        ("printability", "printability"),
        ("aggregate_improvement", "aggregate_improvement"),
    ),
)
def test_preserves_same_scope_claims_without_promoting_them(
    evidence_kind,
    claim_kind,
):
    result = AtlasCanonicalHeadEvaluationSpaceClaimBoundary.evaluate(
        evidence_kind=evidence_kind,
        claim_kind=claim_kind,
    )

    assert result.allowed is True
    assert result.status == "ALLOWED"
    assert result.failure_reason is None


def test_rejects_unknown_evidence_kind():
    with pytest.raises(
        ValueError,
        match="evidence_kind",
    ):
        AtlasCanonicalHeadEvaluationSpaceClaimBoundary.evaluate(
            evidence_kind="unknown",
            claim_kind="surface_accuracy",
        )


def test_rejects_unknown_claim_kind():
    with pytest.raises(
        ValueError,
        match="claim_kind",
    ):
        AtlasCanonicalHeadEvaluationSpaceClaimBoundary.evaluate(
            evidence_kind="landmark_fit",
            claim_kind="unknown",
        )


def test_boundary_does_not_emit_score_threshold_or_phase_decision():
    result = AtlasCanonicalHeadEvaluationSpaceClaimBoundary.evaluate(
        evidence_kind="2d_reprojection",
        claim_kind="metric_3d_accuracy",
    )

    assert not hasattr(result, "support_score")
    assert not hasattr(result, "threshold")
    assert not hasattr(result, "decision")
    assert not hasattr(result, "phase_9_authorized")
