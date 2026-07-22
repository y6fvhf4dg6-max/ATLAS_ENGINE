from __future__ import annotations

import json

import pytest

from CORE.providers.portrait.atlas_mediapipe_portrait_landmark_json_exporter import (
    AtlasMediaPipePortraitLandmarkJsonExporter,
)


def _landmarks() -> list[dict[str, float | int]]:
    return [
        {
            "id": landmark_id,
            "x": (
                0.20
                + 0.60
                * landmark_id
                / 477.0
            ),
            "y": (
                0.75
                - 0.50
                * landmark_id
                / 477.0
            ),
            "z": (
                -0.10
                + 0.20
                * landmark_id
                / 477.0
            ),
        }
        for landmark_id in range(
            478
        )
    ]


def _payload(**overrides):
    arguments = {
        "image_width": 1024,
        "image_height": 1024,
        "confidence": 1.0,
        "landmarks": _landmarks(),
        "mediapipe_version": "0.10.35",
        "model_asset": "face_landmarker.task",
        "source_image_sha256": "abc123",
        "view_type": "front",
    }
    arguments.update(
        overrides
    )

    return (
        AtlasMediaPipePortraitLandmarkJsonExporter
        .build_payload(
            **arguments
        )
    )


def test_payload_uses_expected_schema_and_provider():
    payload = _payload()

    assert payload[
        "schema_version"
    ] == (
        "atlas-mediapipe-face-landmarks-v1"
    )
    assert payload[
        "provider_id"
    ] == (
        "mediapipe-face-landmarker-tasks"
    )


def test_payload_preserves_dimensions_and_confidence():
    payload = _payload()

    assert payload[
        "image_width"
    ] == 1024
    assert payload[
        "image_height"
    ] == 1024
    assert payload[
        "confidence"
    ] == 1.0


def test_payload_contains_exactly_478_landmarks():
    payload = _payload()

    assert payload[
        "landmark_count"
    ] == 478
    assert len(
        payload[
            "landmarks"
        ]
    ) == 478


def test_payload_landmarks_are_sorted_by_id():
    landmarks = list(
        reversed(
            _landmarks()
        )
    )

    payload = _payload(
        landmarks=landmarks
    )

    assert [
        item[
            "id"
        ]
        for item in payload[
            "landmarks"
        ]
    ] == list(
        range(
            478
        )
    )


def test_payload_preserves_xyz_coordinates():
    payload = _payload()

    assert payload[
        "landmarks"
    ][
        4
    ] == pytest.approx(
        {
            "id": 4,
            "x": (
                0.20
                + 0.60
                * 4
                / 477.0
            ),
            "y": (
                0.75
                - 0.50
                * 4
                / 477.0
            ),
            "z": (
                -0.10
                + 0.20
                * 4
                / 477.0
            ),
        }
    )


def test_payload_contains_expected_metadata():
    payload = _payload()

    assert payload[
        "metadata"
    ] == {
        "mediapipe_version": "0.10.35",
        "model_asset": "face_landmarker.task",
        "source_image_sha256": "abc123",
        "synthetic": False,
        "view_type": "front",
    }


def test_payload_is_json_serializable():
    payload = _payload()

    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
    )

    assert (
        "atlas-mediapipe-face-landmarks-v1"
        in encoded
    )


def test_write_creates_deterministic_json(
    tmp_path,
):
    output_path = (
        tmp_path
        / "landmarks.json"
    )

    payload = _payload()

    (
        AtlasMediaPipePortraitLandmarkJsonExporter
        .write(
            output_path,
            payload,
        )
    )

    first_bytes = (
        output_path.read_bytes()
    )

    (
        AtlasMediaPipePortraitLandmarkJsonExporter
        .write(
            output_path,
            payload,
        )
    )

    second_bytes = (
        output_path.read_bytes()
    )

    assert first_bytes == second_bytes
    assert first_bytes.endswith(
        b"\n"
    )


def test_write_creates_parent_directory(
    tmp_path,
):
    output_path = (
        tmp_path
        / "nested"
        / "landmarks.json"
    )

    (
        AtlasMediaPipePortraitLandmarkJsonExporter
        .write(
            output_path,
            _payload(),
        )
    )

    assert output_path.is_file()


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
    ),
    [
        (
            "image_width",
            0,
        ),
        (
            "image_height",
            0,
        ),
        (
            "confidence",
            -0.01,
        ),
        (
            "confidence",
            1.01,
        ),
        (
            "landmarks",
            None,
        ),
        (
            "mediapipe_version",
            "",
        ),
        (
            "model_asset",
            "",
        ),
        (
            "source_image_sha256",
            "",
        ),
        (
            "view_type",
            "",
        ),
    ],
)
def test_payload_rejects_invalid_top_level_values(
    field_name,
    invalid_value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field_name,
    ):
        _payload(
            **{
                field_name: invalid_value,
            }
        )


def test_payload_rejects_duplicate_landmark_ids():
    landmarks = _landmarks()

    landmarks[
        100
    ][
        "id"
    ] = 99

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        _payload(
            landmarks=landmarks
        )


def test_payload_rejects_missing_landmark_id():
    landmarks = [
        item
        for item in _landmarks()
        if item[
            "id"
        ] != 197
    ]

    with pytest.raises(
        ValueError,
        match="478",
    ):
        _payload(
            landmarks=landmarks
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
def test_payload_rejects_invalid_coordinates(
    axis,
    invalid_value,
):
    landmarks = _landmarks()

    landmarks[
        4
    ][
        axis
    ] = invalid_value

    with pytest.raises(
        ValueError,
        match=axis,
    ):
        _payload(
            landmarks=landmarks
        )
