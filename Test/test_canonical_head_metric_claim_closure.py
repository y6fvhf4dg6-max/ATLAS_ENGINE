import pytest


# === PHASE 8 ITEM 10.15 METRIC CLAIM CLOSURE RED ===


def _claim(**overrides):
    from CORE.atlas_canonical_head_metric_claim_closure import (
        AtlasCanonicalHeadMetricClaimClosure,
    )

    values = {
        "claim_id": "global-face-surface-mm",
        "claim_scope": "GLOBAL",
        "ground_truth_admissibility": "SUPPORTED",
        "unit_certainty": "SUPPORTED",
        "scale_traceability": "SUPPORTED",
        "coordinate_system_certainty": "SUPPORTED",
        "alignment_admissibility": "SUPPORTED",
        "correspondence_admissibility": "SUPPORTED",
        "uncertainty": "PARTIAL",
        "coverage": "PARTIAL",
        "leakage": "SUPPORTED",
        "provenance_reference": "item10 closure evidence",
    }
    values.update(overrides)

    return AtlasCanonicalHeadMetricClaimClosure(**values)


def test_records_exact_locked_item10_15_prerequisites():
    closure = _claim()

    assert closure.claim_id == "global-face-surface-mm"
    assert closure.claim_scope == "GLOBAL"
    assert closure.ground_truth_admissibility == "SUPPORTED"
    assert closure.unit_certainty == "SUPPORTED"
    assert closure.scale_traceability == "SUPPORTED"
    assert closure.coordinate_system_certainty == "SUPPORTED"
    assert closure.alignment_admissibility == "SUPPORTED"
    assert closure.correspondence_admissibility == "SUPPORTED"
    assert closure.uncertainty == "PARTIAL"
    assert closure.coverage == "PARTIAL"
    assert closure.leakage == "SUPPORTED"


def test_derives_partial_when_no_blocker_exists_but_prerequisite_is_partial():
    closure = _claim(
        uncertainty="PARTIAL",
        coverage="SUPPORTED",
    )

    assert closure.evidence_state == "PARTIAL"


def test_derives_missing_when_no_blocker_exists_but_prerequisite_is_missing():
    closure = _claim(
        uncertainty="SUPPORTED",
        coverage="MISSING",
    )

    assert closure.evidence_state == "MISSING"


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("ground_truth_admissibility", "BLOCKED"),
        ("unit_certainty", "BLOCKED"),
        ("scale_traceability", "BLOCKED"),
        ("coordinate_system_certainty", "BLOCKED"),
        ("alignment_admissibility", "BLOCKED"),
        ("correspondence_admissibility", "BLOCKED"),
        ("uncertainty", "BLOCKED"),
        ("coverage", "BLOCKED"),
        ("leakage", "BLOCKED"),
    ),
)
def test_any_blocked_prerequisite_blocks_claim(field_name, value):
    closure = _claim(**{field_name: value})

    assert closure.evidence_state == "BLOCKED"


def test_all_supported_prerequisites_support_claim():
    closure = _claim(
        uncertainty="SUPPORTED",
        coverage="SUPPORTED",
    )

    assert closure.evidence_state == "SUPPORTED"


def test_blocked_takes_precedence_over_missing_and_partial():
    closure = _claim(
        ground_truth_admissibility="BLOCKED",
        uncertainty="MISSING",
        coverage="PARTIAL",
    )

    assert closure.evidence_state == "BLOCKED"


def test_missing_takes_precedence_over_partial():
    closure = _claim(
        uncertainty="MISSING",
        coverage="PARTIAL",
    )

    assert closure.evidence_state == "MISSING"


@pytest.mark.parametrize(
    "field_name",
    (
        "ground_truth_admissibility",
        "unit_certainty",
        "scale_traceability",
        "coordinate_system_certainty",
        "alignment_admissibility",
        "correspondence_admissibility",
        "uncertainty",
        "coverage",
        "leakage",
    ),
)
def test_rejects_unknown_prerequisite_state(field_name):
    with pytest.raises(ValueError, match=field_name):
        _claim(**{field_name: "MAYBE"})


def test_unresolved_units_must_be_represented_as_blocked_or_missing_not_supported():
    closure = _claim(
        unit_certainty="BLOCKED",
    )

    assert closure.evidence_state == "BLOCKED"


def test_unqualified_ground_truth_must_block_corresponding_metric_claim():
    closure = _claim(
        ground_truth_admissibility="BLOCKED",
    )

    assert closure.evidence_state == "BLOCKED"


def test_unverified_correspondence_must_block_corresponding_metric_claim():
    closure = _claim(
        correspondence_admissibility="BLOCKED",
    )

    assert closure.evidence_state == "BLOCKED"


def test_inadmissible_alignment_must_block_corresponding_metric_claim():
    closure = _claim(
        alignment_admissibility="BLOCKED",
    )

    assert closure.evidence_state == "BLOCKED"


def test_regional_claim_cannot_hide_partial_or_missing_regional_prerequisite():
    closure = _claim(
        claim_id="nose-region-mm",
        claim_scope="REGIONAL",
        coverage="PARTIAL",
    )

    assert closure.evidence_state == "PARTIAL"


def test_requires_nonblank_claim_id_and_provenance():
    with pytest.raises(ValueError, match="claim_id"):
        _claim(claim_id="   ")

    with pytest.raises(ValueError, match="provenance_reference"):
        _claim(provenance_reference="   ")


def test_rejects_unknown_claim_scope():
    with pytest.raises(ValueError, match="claim_scope"):
        _claim(claim_scope="EVERYTHING")


def test_contract_does_not_emit_global_score_phase_decision_or_phase9_authority():
    closure = _claim()

    assert not hasattr(closure, "support_score")
    assert not hasattr(closure, "normalized_score")
    assert not hasattr(closure, "decision")
    assert not hasattr(closure, "phase8_go")
    assert not hasattr(closure, "phase_9_authorized")


# === ITEM 10.15 CORRECTIVE RED V1 — AUTHORITY HARD BLOCKERS ===


@pytest.mark.parametrize(
    ("field_name", "state"),
    (
        ("ground_truth_admissibility", "PARTIAL"),
        ("ground_truth_admissibility", "MISSING"),
        ("unit_certainty", "PARTIAL"),
        ("unit_certainty", "MISSING"),
        ("alignment_admissibility", "PARTIAL"),
        ("alignment_admissibility", "MISSING"),
        ("correspondence_admissibility", "PARTIAL"),
        ("correspondence_admissibility", "MISSING"),
    ),
)
def test_unresolved_hard_prerequisite_blocks_metric_claim(field_name, state):
    closure = _claim(**{field_name: state})

    assert closure.evidence_state == "BLOCKED"
