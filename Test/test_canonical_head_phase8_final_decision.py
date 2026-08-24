from CORE.atlas_canonical_head_phase8_final_decision import (
    AtlasCanonicalHeadPhase8FinalDecision,
)


def test_current_phase8_decision_is_hold_and_blocked():
    result = AtlasCanonicalHeadPhase8FinalDecision.evaluate_current()

    assert result["decision"] == "HOLD"
    assert result["status"] == "BLOCKED"
    assert result["selected_architecture_kind"] is None
    assert result["phase_9_authorized"] is False


def test_hold_preserves_real_blocking_reasons():
    result = AtlasCanonicalHeadPhase8FinalDecision.evaluate_current()

    assert "INCOMPLETE_FINAL_SCORING_EVIDENCE" in result["blocked_reasons"]
    assert "PRNET_POLICY_BLOCKED" in result["blocked_reasons"]
    assert "HYBRID_DSINE_LICENSE_BLOCKED" in result["blocked_reasons"]


def test_does_not_fabricate_candidate_scores_or_go():
    result = AtlasCanonicalHeadPhase8FinalDecision.evaluate_current()

    assert "candidate_scores" not in result
    assert "support_score" not in result
    assert result["decision"] != "GO"
