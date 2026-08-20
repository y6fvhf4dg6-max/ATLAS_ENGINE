import pytest

from CORE.atlas_portrait_input_evidence import (
    AtlasPortraitInputEvidence,
)
from CORE.atlas_portrait_input_evidence_set import (
    AtlasPortraitInputEvidenceSet,
)
from CORE.atlas_portrait_input_quality_observation import (
    AtlasPortraitInputQualityObservation,
)
from CORE.atlas_portrait_input_usability_gate import (
    AtlasPortraitInputUsabilityGate,
)


def _item(
    evidence_id,
    view_type,
):
    return AtlasPortraitInputEvidence(
        evidence_id=evidence_id,
        media_kind="image",
        view_type=view_type,
        width=1600,
        height=2000,
        metadata={"source": "fixture"},
    )


def _quality(
    evidence_id,
    **overrides,
):
    values = {
        "face_detected": True,
        "face_coverage_ratio": 0.42,
        "occlusion_ratio": 0.08,
        "blur_score": 0.91,
        "perspective_distortion_score": 0.12,
    }
    values.update(overrides)

    return AtlasPortraitInputQualityObservation(
        evidence_id=evidence_id,
        **values,
    )


def _preferred_set():
    return AtlasPortraitInputEvidenceSet(
        (
            _item("front", "front"),
            _item("three-quarter", "three_quarter_left"),
            _item("profile", "profile_left"),
        )
    )


def test_accepts_usable_preferred_multiview_evidence():
    result = AtlasPortraitInputUsabilityGate.evaluate(
        _preferred_set(),
        (
            _quality("front"),
            _quality("three-quarter"),
            _quality("profile"),
        ),
    )

    assert result.usable is True
    assert result.status == "ACCEPTED"
    assert result.blocked_reasons == ()


def test_blocks_when_view_coverage_is_insufficient():
    evidence = AtlasPortraitInputEvidenceSet(
        (
            _item("profile", "profile_left"),
        )
    )

    result = AtlasPortraitInputUsabilityGate.evaluate(
        evidence,
        (
            _quality("profile"),
        ),
    )

    assert result.usable is False
    assert (
        "BLOCKED_INSUFFICIENT_IDENTITY_EVIDENCE"
        in result.blocked_reasons
    )


@pytest.mark.parametrize(
    "quality, reason",
    [
        (
            {"face_detected": False},
            "BLOCKED_FACE_NOT_DETECTED",
        ),
        (
            {"face_coverage_ratio": 0.10},
            "BLOCKED_INSUFFICIENT_FACE_COVERAGE",
        ),
        (
            {"occlusion_ratio": 0.60},
            "BLOCKED_EXCESSIVE_OCCLUSION",
        ),
        (
            {"blur_score": 0.20},
            "BLOCKED_EXCESSIVE_BLUR",
        ),
        (
            {
                "perspective_distortion_score": 0.80,
            },
            "BLOCKED_EXCESSIVE_PERSPECTIVE_DISTORTION",
        ),
    ],
)
def test_blocks_unusable_quality_conditions(
    quality,
    reason,
):
    result = AtlasPortraitInputUsabilityGate.evaluate(
        AtlasPortraitInputEvidenceSet(
            (
                _item("front", "front"),
            )
        ),
        (
            _quality(
                "front",
                **quality,
            ),
        ),
    )

    assert result.usable is False
    assert reason in result.blocked_reasons


def test_requires_one_quality_observation_per_evidence_item():
    with pytest.raises(
        ValueError,
        match="quality observation",
    ):
        AtlasPortraitInputUsabilityGate.evaluate(
            _preferred_set(),
            (
                _quality("front"),
                _quality("three-quarter"),
            ),
        )


def test_rejects_unknown_quality_observation_evidence_id():
    with pytest.raises(
        ValueError,
        match="evidence_id",
    ):
        AtlasPortraitInputUsabilityGate.evaluate(
            _preferred_set(),
            (
                _quality("front"),
                _quality("three-quarter"),
                _quality("unknown"),
            ),
        )


def test_result_does_not_claim_identity_confidence():
    result = AtlasPortraitInputUsabilityGate.evaluate(
        AtlasPortraitInputEvidenceSet(
            (
                _item("front", "front"),
            )
        ),
        (
            _quality("front"),
        ),
    )

    assert not hasattr(
        result,
        "identity_confidence",
    )
    assert not hasattr(
        result,
        "head_mesh",
    )
