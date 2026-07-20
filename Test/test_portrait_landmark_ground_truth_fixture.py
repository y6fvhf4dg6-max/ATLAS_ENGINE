import json

import pytest

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from Test.fixtures.portrait.portrait_landmark_ground_truth_fixture import (
    load_portrait_landmark_ground_truth,
)


def _valid_payload() -> dict:
    return {
        "type": "portrait_landmark_ground_truth",
        "fixture_name": "portrait_fixture_v1",
        "image": {
            "path": "portrait.png",
            "sha256": "abc123",
            "width": 101,
            "height": 201,
        },
        "view_type": "front",
        "coordinate_system": {
            "normalized_range": "0.0..1.0",
            "pixel_origin": "top-left",
            "pixel_mapping": "normalized * (dimension - 1)",
        },
        "landmarks": {
            "left_eye_outer": [0.25, 0.40],
            "nose_tip": [0.50, 0.60],
            "right_eye_outer": [0.75, 0.40],
        },
        "pixel_landmarks": {
            "left_eye_outer": [25.0, 80.0],
            "nose_tip": [50.0, 120.0],
            "right_eye_outer": [75.0, 80.0],
        },
        "metadata": {
            "synthetic": False,
            "manual_ground_truth": True,
            "landmark_count": 3,
        },
    }


def _write_payload(
    tmp_path,
    payload: dict,
):
    path = tmp_path / "ground_truth.json"
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return path


def test_loader_returns_landmark_result(
    tmp_path,
):
    path = _write_payload(
        tmp_path,
        _valid_payload(),
    )

    result = load_portrait_landmark_ground_truth(
        path,
    )

    assert isinstance(
        result,
        AtlasPortraitLandmarkResult,
    )


def test_loader_preserves_image_dimensions(
    tmp_path,
):
    path = _write_payload(
        tmp_path,
        _valid_payload(),
    )

    result = load_portrait_landmark_ground_truth(
        path,
    )

    assert result.image_width == 101
    assert result.image_height == 201


def test_loader_preserves_normalized_landmarks(
    tmp_path,
):
    path = _write_payload(
        tmp_path,
        _valid_payload(),
    )

    result = load_portrait_landmark_ground_truth(
        path,
    )

    assert result.landmarks == {
        "left_eye_outer": (
            0.25,
            0.40,
        ),
        "nose_tip": (
            0.50,
            0.60,
        ),
        "right_eye_outer": (
            0.75,
            0.40,
        ),
    }


def test_loader_uses_manual_ground_truth_provider_id(
    tmp_path,
):
    path = _write_payload(
        tmp_path,
        _valid_payload(),
    )

    result = load_portrait_landmark_ground_truth(
        path,
    )

    assert result.provider_id == ("manual-ground-truth-fixture")
    assert result.confidence == 1.0


def test_loader_builds_expected_metadata(
    tmp_path,
):
    path = _write_payload(
        tmp_path,
        _valid_payload(),
    )

    result = load_portrait_landmark_ground_truth(
        path,
    )

    assert result.metadata == {
        "fixture_name": "portrait_fixture_v1",
        "view_type": "front",
        "synthetic": False,
        "manual_ground_truth": True,
        "image_path": "portrait.png",
        "image_sha256": "abc123",
    }


def test_loader_rejects_wrong_document_type(
    tmp_path,
):
    payload = _valid_payload()
    payload["type"] = "wrong_type"

    path = _write_payload(
        tmp_path,
        payload,
    )

    with pytest.raises(
        ValueError,
        match="document type",
    ):
        load_portrait_landmark_ground_truth(
            path,
        )


def test_loader_rejects_missing_landmarks(
    tmp_path,
):
    payload = _valid_payload()
    del payload["landmarks"]

    path = _write_payload(
        tmp_path,
        payload,
    )

    with pytest.raises(
        ValueError,
        match="landmarks",
    ):
        load_portrait_landmark_ground_truth(
            path,
        )


def test_loader_rejects_pixel_landmark_name_mismatch(
    tmp_path,
):
    payload = _valid_payload()
    del payload["pixel_landmarks"]["nose_tip"]

    path = _write_payload(
        tmp_path,
        payload,
    )

    with pytest.raises(
        ValueError,
        match="landmark names",
    ):
        load_portrait_landmark_ground_truth(
            path,
        )


def test_loader_rejects_inconsistent_pixel_mapping(
    tmp_path,
):
    payload = _valid_payload()
    payload["pixel_landmarks"]["nose_tip"] = [
        51.0,
        120.0,
    ]

    path = _write_payload(
        tmp_path,
        payload,
    )

    with pytest.raises(
        ValueError,
        match="pixel coordinate",
    ):
        load_portrait_landmark_ground_truth(
            path,
        )


def test_loader_rejects_invalid_json(
    tmp_path,
):
    path = tmp_path / "invalid.json"
    path.write_text(
        "{not-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="valid JSON",
    ):
        load_portrait_landmark_ground_truth(
            path,
        )
