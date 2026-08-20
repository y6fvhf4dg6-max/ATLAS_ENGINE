from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_portrait_input_evidence import (
    AtlasPortraitInputEvidence,
)


def _evidence(**overrides):
    values = {
        "evidence_id": "front-photo-01",
        "media_kind": "image",
        "view_type": "front",
        "width": 1600,
        "height": 2000,
        "metadata": {
            "source": "customer_upload",
        },
    }
    values.update(overrides)
    return AtlasPortraitInputEvidence(**values)


def test_normalizes_canonical_input_evidence():
    evidence = _evidence(
        evidence_id="  Front Photo 01  ",
        media_kind=" IMAGE ",
        view_type=" Front ",
    )

    assert evidence.evidence_id == "Front Photo 01"
    assert evidence.media_kind == "image"
    assert evidence.view_type == "front"
    assert evidence.width == 1600
    assert evidence.height == 2000
    assert evidence.metadata == {
        "source": "customer_upload",
    }


def test_supports_phase8_canonical_view_types():
    for view_type in (
        "front",
        "three_quarter_left",
        "three_quarter_right",
        "profile_left",
        "profile_right",
        "unknown",
    ):
        assert _evidence(view_type=view_type).view_type == view_type


def test_supports_image_and_video_evidence():
    assert _evidence(media_kind="image").media_kind == "image"
    assert _evidence(media_kind="video").media_kind == "video"


def test_evidence_is_immutable_snapshot():
    metadata = {
        "source": "customer_upload",
    }
    evidence = _evidence(metadata=metadata)

    metadata["source"] = "changed"

    assert evidence.metadata == {
        "source": "customer_upload",
    }

    with pytest.raises(TypeError):
        evidence.metadata["source"] = "changed"

    with pytest.raises(FrozenInstanceError):
        evidence.view_type = "profile_left"


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"evidence_id": "   "}, "evidence_id"),
        ({"media_kind": "mesh"}, "media_kind"),
        ({"view_type": "rear"}, "view_type"),
        ({"width": 0}, "width"),
        ({"height": 0}, "height"),
        ({"metadata": []}, "metadata"),
    ],
)
def test_rejects_invalid_input_evidence(overrides, message):
    with pytest.raises((TypeError, ValueError), match=message):
        _evidence(**overrides)


def test_contract_does_not_claim_landmarks_or_canonical_geometry():
    evidence = _evidence()

    assert not hasattr(evidence, "landmarks")
    assert not hasattr(evidence, "vertices")
    assert not hasattr(evidence, "faces")
    assert not hasattr(evidence, "head_mesh")
    assert not hasattr(evidence, "identity_confidence")
