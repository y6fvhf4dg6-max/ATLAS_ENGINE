from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from CORE.providers.portrait.atlas_mediapipe_portrait_landmark_cli import (
    AtlasMediaPipePortraitLandmarkCli,
)


class _FakeLandmark:
    def __init__(
        self,
        *,
        x: float,
        y: float,
        z: float,
    ) -> None:
        self.x = x
        self.y = y
        self.z = z


def _fake_landmarks():
    return [
        _FakeLandmark(
            x=(
                0.20
                + 0.60
                * landmark_id
                / 477.0
            ),
            y=(
                0.75
                - 0.50
                * landmark_id
                / 477.0
            ),
            z=(
                -0.10
                + 0.20
                * landmark_id
                / 477.0
            ),
        )
        for landmark_id in range(
            478
        )
    ]


def test_parser_accepts_required_arguments():
    arguments = (
        AtlasMediaPipePortraitLandmarkCli
        .build_parser()
        .parse_args(
            [
                "--image",
                "portrait.png",
                "--model",
                "face_landmarker.task",
                "--output",
                "landmarks.json",
            ]
        )
    )

    assert arguments.image == Path(
        "portrait.png"
    )
    assert arguments.model == Path(
        "face_landmarker.task"
    )
    assert arguments.output == Path(
        "landmarks.json"
    )
    assert arguments.view_type == "front"


def test_parser_accepts_view_type_override():
    arguments = (
        AtlasMediaPipePortraitLandmarkCli
        .build_parser()
        .parse_args(
            [
                "--image",
                "portrait.png",
                "--model",
                "face_landmarker.task",
                "--output",
                "landmarks.json",
                "--view-type",
                "three-quarter",
            ]
        )
    )

    assert arguments.view_type == (
        "three-quarter"
    )


def test_sha256_file_returns_expected_digest(
    tmp_path,
):
    path = tmp_path / "image.bin"
    path.write_bytes(
        b"atlas-portrait"
    )

    expected = hashlib.sha256(
        b"atlas-portrait"
    ).hexdigest()

    assert (
        AtlasMediaPipePortraitLandmarkCli
        .sha256_file(
            path
        )
        == expected
    )


def test_convert_landmarks_returns_478_records():
    records = (
        AtlasMediaPipePortraitLandmarkCli
        .convert_landmarks(
            _fake_landmarks()
        )
    )

    assert len(
        records
    ) == 478
    assert records[
        0
    ][
        "id"
    ] == 0
    assert records[
        477
    ][
        "id"
    ] == 477


def test_convert_landmarks_preserves_xyz():
    source = _fake_landmarks()

    records = (
        AtlasMediaPipePortraitLandmarkCli
        .convert_landmarks(
            source
        )
    )

    assert records[
        4
    ] == pytest.approx(
        {
            "id": 4,
            "x": source[
                4
            ].x,
            "y": source[
                4
            ].y,
            "z": source[
                4
            ].z,
        }
    )


def test_convert_landmarks_rejects_wrong_count():
    with pytest.raises(
        ValueError,
        match="478",
    ):
        (
            AtlasMediaPipePortraitLandmarkCli
            .convert_landmarks(
                _fake_landmarks()[
                    :-1
                ]
            )
        )


@pytest.mark.parametrize(
    "missing_path_name",
    [
        "image",
        "model",
    ],
)
def test_export_rejects_missing_input_files(
    tmp_path,
    missing_path_name,
):
    image_path = (
        tmp_path
        / "portrait.png"
    )
    model_path = (
        tmp_path
        / "face_landmarker.task"
    )
    output_path = (
        tmp_path
        / "landmarks.json"
    )

    image_path.write_bytes(
        b"image"
    )
    model_path.write_bytes(
        b"model"
    )

    if missing_path_name == "image":
        image_path.unlink()
    else:
        model_path.unlink()

    with pytest.raises(
        FileNotFoundError,
        match=missing_path_name,
    ):
        AtlasMediaPipePortraitLandmarkCli.export(
            image_path=image_path,
            model_path=model_path,
            output_path=output_path,
            view_type="front",
            mediapipe_module=SimpleNamespace(),
        )


def test_export_rejects_no_detected_face(
    tmp_path,
):
    image_path = (
        tmp_path
        / "portrait.png"
    )
    model_path = (
        tmp_path
        / "face_landmarker.task"
    )

    image_path.write_bytes(
        b"image"
    )
    model_path.write_bytes(
        b"model"
    )

    fake_module = _fake_mediapipe_module(
        face_landmarks=[],
    )

    with pytest.raises(
        ValueError,
        match="exactly one face",
    ):
        AtlasMediaPipePortraitLandmarkCli.export(
            image_path=image_path,
            model_path=model_path,
            output_path=(
                tmp_path
                / "landmarks.json"
            ),
            view_type="front",
            mediapipe_module=fake_module,
        )


def test_export_rejects_multiple_detected_faces(
    tmp_path,
):
    image_path = (
        tmp_path
        / "portrait.png"
    )
    model_path = (
        tmp_path
        / "face_landmarker.task"
    )

    image_path.write_bytes(
        b"image"
    )
    model_path.write_bytes(
        b"model"
    )

    fake_module = _fake_mediapipe_module(
        face_landmarks=[
            _fake_landmarks(),
            _fake_landmarks(),
        ],
    )

    with pytest.raises(
        ValueError,
        match="exactly one face",
    ):
        AtlasMediaPipePortraitLandmarkCli.export(
            image_path=image_path,
            model_path=model_path,
            output_path=(
                tmp_path
                / "landmarks.json"
            ),
            view_type="front",
            mediapipe_module=fake_module,
        )


def test_export_writes_loader_compatible_json(
    tmp_path,
):
    image_path = (
        tmp_path
        / "portrait.png"
    )
    model_path = (
        tmp_path
        / "face_landmarker.task"
    )
    output_path = (
        tmp_path
        / "landmarks.json"
    )

    image_bytes = (
        b"deterministic-portrait"
    )

    image_path.write_bytes(
        image_bytes
    )
    model_path.write_bytes(
        b"model"
    )

    fake_module = _fake_mediapipe_module(
        face_landmarks=[
            _fake_landmarks(),
        ],
    )

    returned_path = (
        AtlasMediaPipePortraitLandmarkCli
        .export(
            image_path=image_path,
            model_path=model_path,
            output_path=output_path,
            view_type="front",
            mediapipe_module=fake_module,
        )
    )

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8",
        )
    )

    assert returned_path == output_path
    assert payload[
        "schema_version"
    ] == (
        "atlas-mediapipe-face-landmarks-v1"
    )
    assert payload[
        "landmark_count"
    ] == 478
    assert payload[
        "metadata"
    ][
        "mediapipe_version"
    ] == "0.10.35-test"
    assert payload[
        "metadata"
    ][
        "model_asset"
    ] == "face_landmarker.task"
    assert payload[
        "metadata"
    ][
        "source_image_sha256"
    ] == hashlib.sha256(
        image_bytes
    ).hexdigest()


def _fake_mediapipe_module(
    *,
    face_landmarks,
):
    class FakeImage:
        @staticmethod
        def create_from_file(
            path,
        ):
            return SimpleNamespace(
                path=path,
                width=1024,
                height=1024,
            )

    class FakeLandmarker:
        def __enter__(
            self,
        ):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def detect(
            self,
            image,
        ):
            return SimpleNamespace(
                face_landmarks=face_landmarks,
            )

        @classmethod
        def create_from_options(
            cls,
            options,
        ):
            return cls()

    class FakeOptions:
        def __init__(
            self,
            **kwargs,
        ):
            self.arguments = kwargs

    class FakeBaseOptions:
        def __init__(
            self,
            **kwargs,
        ):
            self.arguments = kwargs

    return SimpleNamespace(
        __version__="0.10.35-test",
        Image=FakeImage,
        tasks=SimpleNamespace(
            BaseOptions=FakeBaseOptions,
            vision=SimpleNamespace(
                FaceLandmarker=FakeLandmarker,
                FaceLandmarkerOptions=(
                    FakeOptions
                ),
                RunningMode=SimpleNamespace(
                    IMAGE="IMAGE",
                ),
            ),
        ),
    )
