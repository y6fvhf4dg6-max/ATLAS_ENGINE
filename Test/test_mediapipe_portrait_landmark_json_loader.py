from __future__ import annotations

import json
from pathlib import Path

import pytest

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)
from CORE.providers.portrait.atlas_mediapipe_portrait_landmark_json_loader import (
    AtlasMediaPipePortraitLandmarkJsonLoader,
)


def _payload() -> dict:
    landmarks = []

    for landmark_id in range(
        478,
    ):
        landmarks.append(
            {
                "id": landmark_id,
                "x": (
                    0.20
                    + 0.60
                    * float(
                        landmark_id
                    )
                    / 477.0
                ),
                "y": (
                    0.75
                    - 0.50
                    * float(
                        landmark_id
                    )
                    / 477.0
                ),
                "z": (
                    -0.10
                    + 0.20
                    * float(
                        landmark_id
                    )
                    / 477.0
                ),
            }
        )

    return {
        "schema_version": (
            "atlas-mediapipe-face-landmarks-v1"
        ),
        "provider_id": (
            "mediapipe-face-landmarker-tasks"
        ),
        "image_width": 1024,
        "image_height": 1024,
        "confidence": 1.0,
        "landmark_count": 478,
        "landmarks": landmarks,
        "metadata": {
            "mediapipe_version": "0.10.35",
            "model_asset": "face_landmarker.task",
            "source_image_sha256": "abc123",
            "view_type": "front",
            "synthetic": False,
        },
    }


def _write_payload(
    tmp_path: Path,
    *,
    payload: dict | None = None,
) -> Path:
    if payload is None:
        payload = _payload()

    path = (
        tmp_path
        / "mediapipe_landmarks.json"
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return path


def test_loader_returns_landmark_result(
    tmp_path,
):
    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
        )
    )

    assert isinstance(
        result,
        AtlasPortraitLandmarkResult,
    )


def test_loader_preserves_image_dimensions_and_confidence(
    tmp_path,
):
    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
        )
    )

    assert result.image_width == 1024
    assert result.image_height == 1024
    assert result.confidence == pytest.approx(
        1.0,
    )


def test_loader_uses_expected_provider_id(
    tmp_path,
):
    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
        )
    )

    assert result.provider_id == (
        "mediapipe-face-landmarker-tasks"
    )


def test_loader_maps_exact_required_landmark_names(
    tmp_path,
):
    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
        )
    )

    assert tuple(
        sorted(
            result.landmarks,
        )
    ) == (
        AtlasFlameMediaPipeLandmarkCorrespondence
        .landmark_names()
    )

    assert len(
        result.landmarks,
    ) == 17


def test_loader_maps_media_pipe_ids_to_named_coordinates(
    tmp_path,
):
    payload = _payload()

    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
            payload=payload,
        )
    )

    mapping = (
        AtlasFlameMediaPipeLandmarkCorrespondence
        .mapping()
    )

    for name, landmark_id in mapping.items():
        source = payload[
            "landmarks"
        ][
            landmark_id
        ]

        assert result.landmarks[
            name
        ] == pytest.approx(
            (
                source["x"],
                source["y"],
            ),
            rel=0.0,
            abs=1.0e-12,
        )


def test_loader_preserves_deterministic_metadata(
    tmp_path,
):
    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
        )
    )

    assert result.metadata == {
        "correspondence_version": (
            "flame-mediapipe-ground-truth-v1"
        ),
        "fixture_name": None,
        "image_sha256": "abc123",
        "landmark_count": 478,
        "mediapipe_version": "0.10.35",
        "model_asset": "face_landmarker.task",
        "schema_version": (
            "atlas-mediapipe-face-landmarks-v1"
        ),
        "synthetic": False,
        "view_type": "front",
    }


def test_loader_accepts_string_path(
    tmp_path,
):
    path = _write_payload(
        tmp_path,
    )

    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        str(
            path,
        )
    )

    assert result.image_width == 1024


def test_loader_rejects_missing_file(
    tmp_path,
):
    with pytest.raises(
        FileNotFoundError,
    ):
        AtlasMediaPipePortraitLandmarkJsonLoader.load(
            tmp_path
            / "missing.json"
        )


def test_loader_rejects_invalid_json(
    tmp_path,
):
    path = (
        tmp_path
        / "invalid.json"
    )
    path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="JSON",
    ):
        AtlasMediaPipePortraitLandmarkJsonLoader.load(
            path
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    [
        (
            "schema_version",
            "wrong-schema",
        ),
        (
            "provider_id",
            "wrong-provider",
        ),
        (
            "image_width",
            0,
        ),
        (
            "image_height",
            12.5,
        ),
        (
            "confidence",
            1.1,
        ),
        (
            "landmark_count",
            477,
        ),
        (
            "landmarks",
            None,
        ),
        (
            "metadata",
            None,
        ),
    ],
)
def test_loader_rejects_invalid_top_level_fields(
    tmp_path,
    field_name,
    invalid_value,
):
    payload = _payload()
    payload[
        field_name
    ] = invalid_value

    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field_name,
    ):
        AtlasMediaPipePortraitLandmarkJsonLoader.load(
            _write_payload(
                tmp_path,
                payload=payload,
            )
        )


def test_loader_rejects_duplicate_landmark_ids(
    tmp_path,
):
    payload = _payload()

    payload[
        "landmarks"
    ][
        100
    ][
        "id"
    ] = 99

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        AtlasMediaPipePortraitLandmarkJsonLoader.load(
            _write_payload(
                tmp_path,
                payload=payload,
            )
        )


def test_loader_rejects_missing_required_media_pipe_id(
    tmp_path,
):
    payload = _payload()

    payload[
        "landmarks"
    ] = [
        item
        for item in payload[
            "landmarks"
        ]
        if item["id"] != 197
    ]
    payload[
        "landmark_count"
    ] = 477

    with pytest.raises(
        ValueError,
        match="197",
    ):
        AtlasMediaPipePortraitLandmarkJsonLoader.load(
            _write_payload(
                tmp_path,
                payload=payload,
            )
        )


@pytest.mark.parametrize(
    (
        "axis",
        "invalid_value",
    ),
    [
        (
            "x",
            -0.01,
        ),
        (
            "x",
            1.01,
        ),
        (
            "y",
            -0.01,
        ),
        (
            "y",
            1.01,
        ),
        (
            "z",
            float(
                "nan"
            ),
        ),
    ],
)
def test_loader_rejects_invalid_landmark_coordinates(
    tmp_path,
    axis,
    invalid_value,
):
    payload = _payload()

    payload[
        "landmarks"
    ][
        4
    ][
        axis
    ] = invalid_value

    with pytest.raises(
        ValueError,
        match=axis,
    ):
        AtlasMediaPipePortraitLandmarkJsonLoader.load(
            _write_payload(
                tmp_path,
                payload=payload,
            )
        )


def test_loader_does_not_depend_on_mediapipe_package(
    tmp_path,
):
    result = AtlasMediaPipePortraitLandmarkJsonLoader.load(
        _write_payload(
            tmp_path,
        )
    )

    assert result.metadata[
        "mediapipe_version"
    ] == "0.10.35"
