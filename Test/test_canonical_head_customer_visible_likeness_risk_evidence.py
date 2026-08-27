from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_customer_visible_likeness_risk_evidence import (
    AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence,
)


def test_defines_exact_item9_14_regions():
    assert AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence.REGIONS == (
        "nose",
        "jaw_chin",
        "orbital_region",
        "cheek_midface",
        "head_silhouette_profile",
    )


def test_defines_exact_risk_statuses():
    assert AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence.RISK_STATUSES == (
        "bounded_potential_likeness_risk",
        "bounded_mixed_likeness_risk",
        "unresolved_likeness_risk",
    )


def test_defines_exact_verification_states():
    assert AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence.VERIFICATION_STATES == (
        "potential_not_verified_customer_visible",
        "not_verified_customer_visible",
    )


def test_defines_exact_evidence_origins():
    assert AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


@pytest.mark.parametrize(
    ("region", "risk_status"),
    (
        ("nose", "bounded_potential_likeness_risk"),
        ("jaw_chin", "bounded_mixed_likeness_risk"),
        ("orbital_region", "unresolved_likeness_risk"),
        ("cheek_midface", "unresolved_likeness_risk"),
        ("head_silhouette_profile", "bounded_mixed_likeness_risk"),
    ),
)
def test_accepts_exact_item9_14_region_risk_pairs(region, risk_status):
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region=region,
        risk_status=risk_status,
        verification_state="POTENTIAL_NOT_VERIFIED_CUSTOMER_VISIBLE",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="persisted Item 8/9 evidence",
        semantic_scope="Item 9.14 bounded likeness-risk audit",
        permitted_claim="potential customer-visible risk remains bounded",
        prohibited_claims=(
            "verified customer-visible identity degradation",
            "commercial likeness failure proven",
            "unsupported phase decision",
        ),
        bounded_interpretation="risk remains bounded to verified evidence",
    )

    assert evidence.region == region
    assert evidence.risk_status == risk_status
    assert evidence.verification_state == "potential_not_verified_customer_visible"
    assert evidence.evidence_origin == "multiview_constrained"


def test_nose_retains_potential_likeness_risk_without_customer_visible_failure_claim():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="nose",
        risk_status="bounded_potential_likeness_risk",
        verification_state="potential_not_verified_customer_visible",
        evidence_origin="multiview_constrained",
        source_reference=(
            "Item 9.4 nose evidence + Item 8 H1/H2/H4 evidence"
        ),
        semantic_scope=(
            "nose_body repeated held-out observation-space degradation and "
            "bounded canonical model-space geometry change"
        ),
        permitted_claim=(
            "nose_body remains the clearest retained potential likeness-risk signal"
        ),
        prohibited_claims=(
            "customer-visible nose degradation is verified",
            "FLAME nose geometry is commercially unacceptable",
            "metric anatomical nose failure is proven",
        ),
        bounded_interpretation=(
            "nose_body degrades in 3/3 held-out observation-space views, "
            "but customer-visible identity degradation remains unverified"
        ),
    )

    assert evidence.risk_status == "bounded_potential_likeness_risk"


def test_jaw_chin_is_mixed_due_to_side_improvement_and_front_tradeoff():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="jaw_chin",
        risk_status="bounded_mixed_likeness_risk",
        verification_state="potential_not_verified_customer_visible",
        evidence_origin="multiview_constrained",
        source_reference="Item 9.3 jaw/chin quality evidence",
        semantic_scope="jaw/chin silhouette and profile behavior",
        permitted_claim=(
            "jaw/chin likeness risk is mixed because side-profile evidence "
            "improves while front-view trade-off remains"
        ),
        prohibited_claims=(
            "jaw/chin likeness is commercially accepted",
            "jaw/chin likeness is commercially rejected",
            "2d contour improvement proves 3d anatomical correctness",
        ),
        bounded_interpretation=(
            "side-profile contour improvement does not remove front-view "
            "or anatomical uncertainty"
        ),
    )

    assert evidence.risk_status == "bounded_mixed_likeness_risk"


def test_orbital_customer_visible_risk_remains_unresolved():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="orbital_region",
        risk_status="unresolved_likeness_risk",
        verification_state="not_verified_customer_visible",
        evidence_origin="unresolved",
        source_reference="Item 9.5 orbital quality evidence",
        semantic_scope="orbital/eye-socket customer-visible identity risk",
        permitted_claim="orbital customer-visible likeness risk remains unresolved",
        prohibited_claims=(
            "eye-region landmarks prove orbital likeness",
            "orbital customer-visible failure is verified",
            "orbital anatomy is metric validated",
        ),
        bounded_interpretation=(
            "eye-region evidence is view-dependent and cannot be promoted "
            "to orbital anatomical surface evidence"
        ),
    )

    assert evidence.risk_status == "unresolved_likeness_risk"


def test_cheek_midface_customer_visible_risk_remains_unresolved():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="cheek_midface",
        risk_status="unresolved_likeness_risk",
        verification_state="not_verified_customer_visible",
        evidence_origin="unresolved",
        source_reference="Item 9.6 cheek/midface quality evidence",
        semantic_scope="cheek/midface customer-visible identity risk",
        permitted_claim="cheek/midface likeness risk remains unresolved",
        prohibited_claims=(
            "cheek/midface likeness is verified",
            "cheek/midface failure is verified",
            "model-prior cheek geometry is subject-observed likeness evidence",
        ),
        bounded_interpretation=(
            "subject-specific cheek/midface mapping and validated quality "
            "evidence remain unavailable"
        ),
    )

    assert evidence.risk_status == "unresolved_likeness_risk"


def test_head_silhouette_profile_is_mixed_not_commercially_accepted():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="head_silhouette_profile",
        risk_status="bounded_mixed_likeness_risk",
        verification_state="potential_not_verified_customer_visible",
        evidence_origin="multiview_constrained",
        source_reference="personal multiview silhouette/profile evidence",
        semantic_scope="identity-bearing head silhouette/profile behavior",
        permitted_claim=(
            "side-profile evidence improves while front-view trade-off remains"
        ),
        prohibited_claims=(
            "silhouette/profile commercial likeness acceptance",
            "silhouette improvement proves identity preservation",
            "front-view trade-off proves customer-visible failure",
        ),
        bounded_interpretation=(
            "silhouette/profile is identity-bearing but current evidence "
            "does not establish customer-visible acceptance or rejection"
        ),
    )

    assert evidence.risk_status == "bounded_mixed_likeness_risk"


def test_pre_phase8_portrait_visual_rejection_is_not_current_canonical_candidate_rejection():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="nose",
        risk_status="bounded_potential_likeness_risk",
        verification_state="potential_not_verified_customer_visible",
        evidence_origin="multiview_constrained",
        source_reference=(
            "current Phase 8 evidence; pre-Phase-8 portrait diagnostics excluded "
            "from current canonical candidate rejection"
        ),
        semantic_scope="current canonical-head likeness-risk boundary",
        permitted_claim=(
            "historical portrait visual rejection remains diagnostic history only"
        ),
        prohibited_claims=(
            "pre-Phase-8 portrait rejection proves current canonical candidate rejection",
            "historical visual inspection is current customer-visible validation",
        ),
        bounded_interpretation=(
            "historical portrait pipeline and current canonical-head candidate "
            "must remain separate evidence paths"
        ),
    )

    assert (
        "pre-Phase-8 portrait rejection proves current canonical candidate rejection"
        in evidence.prohibited_claims
    )


def test_rejects_unknown_region():
    with pytest.raises(ValueError, match="region"):
        AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
            region="mouth",
            risk_status="unresolved_likeness_risk",
            verification_state="not_verified_customer_visible",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_risk_status():
    with pytest.raises(ValueError, match="risk_status"):
        AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
            region="nose",
            risk_status="pass",
            verification_state="not_verified_customer_visible",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_verification_state():
    with pytest.raises(ValueError, match="verification_state"):
        AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
            region="nose",
            risk_status="bounded_potential_likeness_risk",
            verification_state="verified_failure",
            evidence_origin="unresolved",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_rejects_unknown_evidence_origin():
    with pytest.raises(ValueError, match="evidence_origin"):
        AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
            region="nose",
            risk_status="bounded_potential_likeness_risk",
            verification_state="not_verified_customer_visible",
            evidence_origin="observed",
            source_reference="source",
            semantic_scope="scope",
            permitted_claim="bounded",
            prohibited_claims=("unsupported claim",),
            bounded_interpretation="bounded",
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="nose",
        risk_status="bounded_potential_likeness_risk",
        verification_state="potential_not_verified_customer_visible",
        evidence_origin="multiview_constrained",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.risk_status = "unresolved_likeness_risk"


def test_contract_does_not_add_customer_visible_score_threshold_or_phase_decision():
    evidence = AtlasCanonicalHeadCustomerVisibleLikenessRiskEvidence(
        region="nose",
        risk_status="bounded_potential_likeness_risk",
        verification_state="potential_not_verified_customer_visible",
        evidence_origin="multiview_constrained",
        source_reference="source",
        semantic_scope="scope",
        permitted_claim="bounded",
        prohibited_claims=("unsupported claim",),
        bounded_interpretation="bounded",
    )

    assert not hasattr(evidence, "customer_visible_score")
    assert not hasattr(evidence, "likeness_score")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "commercial_acceptance")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")
