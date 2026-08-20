from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_portrait_input_quality_observation import (
    AtlasPortraitInputQualityObservation,
)


def _observation(**overrides):
    values = {
        "evidence_id": "front-photo-01",
        "face_detected": True,
        "face_coverage_ratio": 0.42,
        "occlusion_ratio": 0.08,
        "blur_score": 0.91,
        "perspective_distortion_score": 0.12,
    }
    values.update(overrides)
    return AtlasPortraitInputQualityObservation(**values)


def test_preserves_normalized_quality_observation():
    observation = _observation(
        evidence_id="  front-photo-01  ",
    )

    assert observation.evidence_id == "front-photo-01"
    assert observation.face_detected is True
    assert observation.face_coverage_ratio == pytest.approx(0.42)
    assert observation.occlusion_ratio == pytest.approx(0.08)
    assert observation.blur_score == pytest.approx(0.91)
    assert observation.perspective_distortion_score == pytest.approx(0.12)


def test_quality_observation_is_immutable():
    observation = _observation()

    with pytest.raises(FrozenInstanceError):
        observation.blur_score = 0.5


@pytest.mark.parametrize(
    "field",
    (
        "face_coverage_ratio",
        "occlusion_ratio",
        "blur_score",
        "perspective_distortion_score",
    ),
)
@pytest.mark.parametrize(
    "value",
    (-0.01, 1.01, float("nan"), float("inf")),
)
def test_rejects_invalid_normalized_quality_metrics(field, value):
    with pytest.raises(ValueError, match=field):
        _observation(**{field: value})


def test_requires_boolean_face_detected():
    with pytest.raises(TypeError, match="face_detected"):
        _observation(face_detected=1)


def test_rejects_blank_evidence_id():
    with pytest.raises(ValueError, match="evidence_id"):
        _observation(evidence_id="   ")


def test_contract_does_not_claim_identity_confidence_or_geometry():
    observation = _observation()

    assert not hasattr(observation, "identity_confidence")
    assert not hasattr(observation, "vertices")
    assert not hasattr(observation, "head_mesh")
    assert not hasattr(observation, "production_eligible")
