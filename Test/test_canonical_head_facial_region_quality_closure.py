from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_facial_region_quality_closure import (
    AtlasCanonicalHeadFacialRegionQualityClosure,
)


def test_defines_exact_item9_decisions():
    assert AtlasCanonicalHeadFacialRegionQualityClosure.DECISIONS == (
        "pass",
        "bounded_pass",
        "hold",
        "revision_required",
    )


def test_defines_exact_superseding_sources():
    assert AtlasCanonicalHeadFacialRegionQualityClosure.SUPERSEDING_SOURCES == (
        "item_10_metric_ground_truth",
        "item_11_physical_representation",
        "item_14_three_class_architecture_comparison",
        "item_15_phase8_final_decision",
        "explicit_plan_revision",
    )


def test_accepts_bounded_pass_item9_closure():
    closure = AtlasCanonicalHeadFacialRegionQualityClosure(
        decision="BOUNDED_PASS",
        evidence_date="2026-08-27",
        retained_limitations=(
            "nose_body degrades in 3/3 held-out observation-space views",
            "jaw/chin front-versus-profile trade-off remains",
            "orbital customer-visible likeness risk remains unresolved",
            "cheek/midface customer-visible likeness risk remains unresolved",
            "forehead/cranial quality remains blocked",
            "regional metric surface result remains blocked",
            "customer-visible risk remains potential, not verified",
        ),
        bounded_interpretation=(
            "Item 9 facial-region quality has been sufficiently characterized "
            "to close as BOUNDED_PASS without claiming unqualified facial "
            "geometry correctness or commercial likeness acceptance."
        ),
        reopen_on_new_evidence=True,
        superseding_sources=(
            "item_10_metric_ground_truth",
            "item_11_physical_representation",
            "item_14_three_class_architecture_comparison",
            "item_15_phase8_final_decision",
            "explicit_plan_revision",
        ),
        historical_record_policy=(
            "The 2026-08-27 Item 9 closure remains immutable historical evidence; "
            "later stronger evidence may reopen or supersede conclusions but must "
            "not silently rewrite the historical state."
        ),
        prohibited_claims=(
            "Item 9 BOUNDED_PASS proves metric anatomical correctness",
            "Item 9 BOUNDED_PASS proves commercial likeness acceptance",
            "Item 9 BOUNDED_PASS is Phase 8 GO LOCK",
            "Item 9 BOUNDED_PASS authorizes Phase 9",
        ),
    )

    assert closure.decision == "bounded_pass"
    assert closure.reopen_on_new_evidence is True
    assert closure.superseding_sources == (
        "item_10_metric_ground_truth",
        "item_11_physical_representation",
        "item_14_three_class_architecture_comparison",
        "item_15_phase8_final_decision",
        "explicit_plan_revision",
    )


def test_rejects_unknown_decision():
    with pytest.raises(ValueError, match="decision"):
        AtlasCanonicalHeadFacialRegionQualityClosure(
            decision="go",
            evidence_date="2026-08-27",
            retained_limitations=("limitation",),
            bounded_interpretation="bounded",
            reopen_on_new_evidence=True,
            superseding_sources=("item_10_metric_ground_truth",),
            historical_record_policy="preserve history",
            prohibited_claims=("unsupported claim",),
        )


def test_rejects_unknown_superseding_source():
    with pytest.raises(ValueError, match="superseding_sources"):
        AtlasCanonicalHeadFacialRegionQualityClosure(
            decision="bounded_pass",
            evidence_date="2026-08-27",
            retained_limitations=("limitation",),
            bounded_interpretation="bounded",
            reopen_on_new_evidence=True,
            superseding_sources=("item_12_runtime_reproducibility",),
            historical_record_policy="preserve history",
            prohibited_claims=("unsupported claim",),
        )


def test_reopen_boundary_is_explicit_and_true():
    closure = AtlasCanonicalHeadFacialRegionQualityClosure(
        decision="bounded_pass",
        evidence_date="2026-08-27",
        retained_limitations=("limitation",),
        bounded_interpretation="bounded",
        reopen_on_new_evidence=True,
        superseding_sources=("item_10_metric_ground_truth",),
        historical_record_policy="preserve historical closure",
        prohibited_claims=("unsupported claim",),
    )

    assert closure.reopen_on_new_evidence is True


def test_historical_record_policy_must_be_present():
    with pytest.raises(ValueError, match="historical_record_policy"):
        AtlasCanonicalHeadFacialRegionQualityClosure(
            decision="bounded_pass",
            evidence_date="2026-08-27",
            retained_limitations=("limitation",),
            bounded_interpretation="bounded",
            reopen_on_new_evidence=True,
            superseding_sources=("item_10_metric_ground_truth",),
            historical_record_policy="",
            prohibited_claims=("unsupported claim",),
        )


def test_retained_limitations_must_not_be_empty():
    with pytest.raises(ValueError, match="retained_limitations"):
        AtlasCanonicalHeadFacialRegionQualityClosure(
            decision="bounded_pass",
            evidence_date="2026-08-27",
            retained_limitations=(),
            bounded_interpretation="bounded",
            reopen_on_new_evidence=True,
            superseding_sources=("item_10_metric_ground_truth",),
            historical_record_policy="preserve history",
            prohibited_claims=("unsupported claim",),
        )


def test_prohibited_claims_must_not_be_empty():
    with pytest.raises(ValueError, match="prohibited_claims"):
        AtlasCanonicalHeadFacialRegionQualityClosure(
            decision="bounded_pass",
            evidence_date="2026-08-27",
            retained_limitations=("limitation",),
            bounded_interpretation="bounded",
            reopen_on_new_evidence=True,
            superseding_sources=("item_10_metric_ground_truth",),
            historical_record_policy="preserve history",
            prohibited_claims=(),
        )


def test_contract_is_immutable():
    closure = AtlasCanonicalHeadFacialRegionQualityClosure(
        decision="bounded_pass",
        evidence_date="2026-08-27",
        retained_limitations=("limitation",),
        bounded_interpretation="bounded",
        reopen_on_new_evidence=True,
        superseding_sources=("item_10_metric_ground_truth",),
        historical_record_policy="preserve history",
        prohibited_claims=("unsupported claim",),
    )

    with pytest.raises(FrozenInstanceError):
        closure.decision = "pass"


def test_contract_does_not_create_phase8_or_phase9_authority():
    closure = AtlasCanonicalHeadFacialRegionQualityClosure(
        decision="bounded_pass",
        evidence_date="2026-08-27",
        retained_limitations=("limitation",),
        bounded_interpretation="bounded",
        reopen_on_new_evidence=True,
        superseding_sources=("item_10_metric_ground_truth",),
        historical_record_policy="preserve history",
        prohibited_claims=("unsupported claim",),
    )

    assert not hasattr(closure, "phase8_go")
    assert not hasattr(closure, "phase8_locked")
    assert not hasattr(closure, "phase_9_authorized")
    assert not hasattr(closure, "commercial_acceptance")
    assert not hasattr(closure, "metric_anatomical_accuracy")
    assert not hasattr(closure, "acceptance_threshold")
