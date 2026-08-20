import pytest

from CORE.atlas_portrait_input_evidence import (
    AtlasPortraitInputEvidence,
)
from CORE.atlas_portrait_input_evidence_set import (
    AtlasPortraitInputEvidenceSet,
)


def _item(
    evidence_id,
    view_type,
    *,
    media_kind="image",
):
    return AtlasPortraitInputEvidence(
        evidence_id=evidence_id,
        media_kind=media_kind,
        view_type=view_type,
        width=1600,
        height=2000,
        metadata={
            "source": "fixture",
        },
    )


def test_classifies_preferred_front_three_quarter_profile_set():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item("front", "front"),
            _item("three-quarter", "three_quarter_left"),
            _item("profile", "profile_left"),
        )
    )

    assert evidence.coverage_class == (
        "high_confidence_multiview"
    )
    assert evidence.production_evidence_eligible is True
    assert evidence.blocked_reason is None


def test_accepts_opposite_three_quarter_and_profile_sides():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item("front", "front"),
            _item(
                "three-quarter",
                "three_quarter_right",
            ),
            _item("profile", "profile_right"),
        )
    )

    assert evidence.coverage_class == (
        "high_confidence_multiview"
    )


def test_classifies_front_plus_three_quarter_as_partial_multiview():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item("front", "front"),
            _item(
                "three-quarter",
                "three_quarter_left",
            ),
        )
    )

    assert evidence.coverage_class == (
        "multiview_partial"
    )
    assert evidence.production_evidence_eligible is True
    assert evidence.blocked_reason is None


def test_classifies_single_front_as_fallback():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item("front", "front"),
        )
    )

    assert evidence.coverage_class == (
        "single_view_fallback"
    )
    assert evidence.production_evidence_eligible is True
    assert evidence.blocked_reason is None


@pytest.mark.parametrize(
    "items",
    [
        (
            _item("unknown", "unknown"),
        ),
        (
            _item("profile", "profile_left"),
        ),
        (
            _item(
                "three-quarter",
                "three_quarter_left",
            ),
        ),
    ],
)
def test_blocks_insufficient_identity_view_coverage(items):
    evidence = AtlasPortraitInputEvidenceSet(
        items
    )

    assert evidence.coverage_class == "insufficient"
    assert evidence.production_evidence_eligible is False
    assert evidence.blocked_reason == (
        "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE"
    )


def test_video_evidence_does_not_automatically_claim_multiview_coverage():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item(
                "video",
                "unknown",
                media_kind="video",
            ),
        )
    )

    assert evidence.coverage_class == "insufficient"
    assert evidence.production_evidence_eligible is False


def test_rejects_duplicate_evidence_ids():
    with pytest.raises(
        ValueError,
        match="evidence_id",
    ):
        AtlasPortraitInputEvidenceSet(
            (
                _item("same", "front"),
                _item(
                    "same",
                    "three_quarter_left",
                ),
            )
        )


def test_rejects_empty_evidence_set():
    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        AtlasPortraitInputEvidenceSet(
            ()
        )


def test_evidence_set_is_immutable_snapshot():
    source = [
        _item("front", "front"),
    ]

    evidence = AtlasPortraitInputEvidenceSet(
        source
    )

    source.append(
        _item(
            "profile",
            "profile_left",
        )
    )

    assert len(evidence.items) == 1
    assert isinstance(
        evidence.items,
        tuple,
    )


def test_contract_does_not_claim_identity_confidence_or_geometry():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item("front", "front"),
        )
    )

    assert not hasattr(
        evidence,
        "identity_confidence",
    )
    assert not hasattr(
        evidence,
        "head_mesh",
    )
    assert not hasattr(
        evidence,
        "vertices",
    )
