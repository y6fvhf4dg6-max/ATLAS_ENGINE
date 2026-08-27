from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_semantic_region_mapping_evidence import (
    AtlasCanonicalHeadSemanticRegionMappingEvidence,
)


def test_contract_defines_exact_item9_2_required_regions():
    assert AtlasCanonicalHeadSemanticRegionMappingEvidence.REQUIRED_REGIONS == (
        "jaw",
        "chin",
        "nose_bridge",
        "nose_body",
        "nose_base_tip",
        "left_orbital",
        "right_orbital",
        "left_cheek",
        "right_cheek",
        "upper_lip",
        "lower_lip",
        "perioral",
        "forehead",
        "cranial_head_envelope",
    )


def test_contract_defines_exact_mapping_states():
    assert AtlasCanonicalHeadSemanticRegionMappingEvidence.MAPPING_STATES == (
        "provider_verified",
        "independently_verified_atlas_derived",
        "anchor_supported_only",
        "unresolved_blocked",
    )


def test_contract_defines_exact_evidence_origin_states():
    assert AtlasCanonicalHeadSemanticRegionMappingEvidence.EVIDENCE_ORIGINS == (
        "directly_observed",
        "multiview_constrained",
        "model_prior_inferred",
        "generated_completion",
        "unresolved",
    )


def test_accepts_provider_verified_mapping_with_bounded_claim():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="left_orbital",
        mapping_state="provider_verified",
        mapping_name="synthetic provider mapping fixture",
        mapping_scope="synthetic_test_only",
        evidence_origin="DIRECTLY_OBSERVED",
        source_reference="synthetic-test-only",
        permitted_claim="provider-verified mapping state contract fixture",
        prohibited_claims=(
            "dense anatomical ground truth",
            "metric 3d ground truth",
        ),
    )

    assert evidence.region_name == "left_orbital"
    assert evidence.mapping_state == "provider_verified"
    assert evidence.mapping_name == "synthetic provider mapping fixture"
    assert evidence.mapping_scope == "synthetic_test_only"
    assert evidence.evidence_origin == "directly_observed"
    assert evidence.source_reference == "synthetic-test-only"
    assert evidence.permitted_claim == (
        "provider-verified mapping state contract fixture"
    )
    assert evidence.prohibited_claims == (
        "dense anatomical ground truth",
        "metric 3d ground truth",
    )


def test_accepts_independently_verified_atlas_derived_mapping():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="nose_body",
        mapping_state="independently_verified_atlas_derived",
        mapping_name=(
            "ATLAS-derived barycentric-anchor-supported "
            "FLAME topology footprint"
        ),
        mapping_scope="barycentric_anchor_supported_topology_footprint",
        evidence_origin="MODEL_PRIOR_INFERRED",
        source_reference=(
            "ITEM8_H2_EXACT_BARYCENTRIC_ANCHOR_TOPOLOGY_FOOTPRINT.json"
        ),
        permitted_claim=(
            "separately verified anchor-supported canonical topology footprint"
        ),
        prohibited_claims=(
            "provider-authored finer region",
            "dense anatomical region",
            "anatomical ground truth",
        ),
    )

    assert evidence.mapping_state == "independently_verified_atlas_derived"


def test_accepts_anchor_supported_only_state_without_promoting_to_verified_region():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="nose_base_tip",
        mapping_state="anchor_supported_only",
        mapping_name="bounded observation-to-surface anchor support",
        mapping_scope="anchor_supported_correspondence_only",
        evidence_origin="DIRECTLY_OBSERVED",
        source_reference="persistent evidence reference",
        permitted_claim="anchor-supported correspondence evidence only",
        prohibited_claims=(
            "verified dense region mapping",
            "provider-authored region",
            "anatomical ground truth",
        ),
    )

    assert evidence.mapping_state == "anchor_supported_only"


def test_accepts_unresolved_blocked_state():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="left_cheek",
        mapping_state="unresolved_blocked",
        mapping_name="unresolved",
        mapping_scope="unresolved",
        evidence_origin="UNRESOLVED",
        source_reference="no verified mapping source",
        permitted_claim="mapping unresolved",
        prohibited_claims=(
            "regional surface accuracy",
            "anatomical ground truth",
        ),
    )

    assert evidence.mapping_state == "unresolved_blocked"


def test_normalizes_region_and_mapping_state():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="  Nose Body  ",
        mapping_state="  Independently Verified Atlas Derived  ",
        mapping_name="mapping",
        mapping_scope="bounded_scope",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="source",
        permitted_claim="bounded claim",
        prohibited_claims=("unsupported claim",),
    )

    assert evidence.region_name == "nose_body"
    assert evidence.mapping_state == "independently_verified_atlas_derived"


@pytest.mark.parametrize(
    "region_name",
    (
        "",
        "nose",
        "left_eye",
        "right_eye",
        "unknown_region",
    ),
)
def test_rejects_non_item9_2_region(region_name):
    with pytest.raises(
        ValueError,
        match="region_name",
    ):
        AtlasCanonicalHeadSemanticRegionMappingEvidence(
            region_name=region_name,
            mapping_state="unresolved_blocked",
            mapping_name="mapping",
            mapping_scope="unresolved",
            evidence_origin="UNRESOLVED",
            source_reference="source",
            permitted_claim="bounded claim",
            prohibited_claims=("unsupported claim",),
        )


def test_rejects_unknown_mapping_state():
    with pytest.raises(
        ValueError,
        match="mapping_state",
    ):
        AtlasCanonicalHeadSemanticRegionMappingEvidence(
            region_name="jaw",
            mapping_state="verified",
            mapping_name="mapping",
            mapping_scope="unresolved",
            evidence_origin="UNRESOLVED",
            source_reference="source",
            permitted_claim="bounded claim",
            prohibited_claims=("unsupported claim",),
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "mapping_name",
        "mapping_scope",
        "source_reference",
        "permitted_claim",
    ),
)
def test_rejects_blank_required_text_fields(field_name):
    kwargs = {
        "region_name": "jaw",
        "mapping_state": "unresolved_blocked",
        "mapping_name": "mapping",
        "mapping_scope": "unresolved",
        "evidence_origin": "UNRESOLVED",
        "source_reference": "source",
        "permitted_claim": "bounded claim",
        "prohibited_claims": ("unsupported claim",),
    }
    kwargs[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasCanonicalHeadSemanticRegionMappingEvidence(**kwargs)


def test_rejects_empty_prohibited_claims():
    with pytest.raises(
        ValueError,
        match="prohibited_claims",
    ):
        AtlasCanonicalHeadSemanticRegionMappingEvidence(
            region_name="jaw",
            mapping_state="unresolved_blocked",
            mapping_name="mapping",
            mapping_scope="unresolved",
            evidence_origin="UNRESOLVED",
            source_reference="source",
            permitted_claim="bounded claim",
            prohibited_claims=(),
        )


def test_contract_is_immutable():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="jaw",
        mapping_state="unresolved_blocked",
        mapping_name="mapping",
        mapping_scope="bounded_scope",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="source",
        permitted_claim="bounded claim",
        prohibited_claims=("unsupported claim",),
    )

    with pytest.raises(FrozenInstanceError):
        evidence.mapping_state = "provider_verified"


def test_contract_does_not_claim_geometry_accuracy_or_phase_decision():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="jaw",
        mapping_state="unresolved_blocked",
        mapping_name="mapping",
        mapping_scope="bounded_scope",
        evidence_origin="MULTIVIEW_CONSTRAINED",
        source_reference="source",
        permitted_claim="bounded claim",
        prohibited_claims=("unsupported claim",),
    )

    assert not hasattr(evidence, "vertices")
    assert not hasattr(evidence, "surface_error")
    assert not hasattr(evidence, "metric_accuracy_mm")
    assert not hasattr(evidence, "likeness_score")
    assert not hasattr(evidence, "support_score")
    assert not hasattr(evidence, "threshold")
    assert not hasattr(evidence, "decision")
    assert not hasattr(evidence, "phase_9_authorized")


def test_rejects_unknown_evidence_origin():
    with pytest.raises(
        ValueError,
        match="evidence_origin",
    ):
        AtlasCanonicalHeadSemanticRegionMappingEvidence(
            region_name="jaw",
            mapping_state="unresolved_blocked",
            mapping_name="mapping",
            mapping_scope="unresolved",
            evidence_origin="observed",
            source_reference="source",
            permitted_claim="bounded claim",
            prohibited_claims=("unsupported claim",),
        )


def test_normalizes_evidence_origin():
    evidence = AtlasCanonicalHeadSemanticRegionMappingEvidence(
        region_name="jaw",
        mapping_state="unresolved_blocked",
        mapping_name="mapping",
        mapping_scope="unresolved",
        evidence_origin="  Model Prior Inferred  ",
        source_reference="source",
        permitted_claim="bounded claim",
        prohibited_claims=("unsupported claim",),
    )

    assert evidence.evidence_origin == "model_prior_inferred"
