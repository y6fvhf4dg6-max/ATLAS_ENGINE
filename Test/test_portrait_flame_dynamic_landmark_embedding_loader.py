from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest

from CORE.providers.portrait.atlas_portrait_flame_dynamic_landmark_embedding_loader import (
    AtlasPortraitFlameDynamicLandmarkEmbedding,
    AtlasPortraitFlameDynamicLandmarkEmbeddingLoader,
)


def _valid_payload() -> dict[str, np.ndarray]:
    return {
        "lmk_face_idx": np.array(
            [
                [10, 11, 12],
                [20, 21, 22],
            ],
            dtype=np.uint32,
        ),
        "lmk_b_coords": np.array(
            [
                [
                    [1.0, 0.0, 0.0],
                    [0.2, 0.3, 0.5],
                    [0.0, 0.0, 1.0],
                ],
                [
                    [0.4, 0.4, 0.2],
                    [0.1, 0.2, 0.7],
                    [0.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float64,
        ),
    }


def _write_payload(
    path: Path,
    payload: object,
) -> None:
    np.save(
        path,
        payload,
        allow_pickle=True,
    )


def _load(
    tmp_path: Path,
    *,
    payload: object | None = None,
    triangle_count: int = 100,
) -> AtlasPortraitFlameDynamicLandmarkEmbedding:
    path = tmp_path / "dynamic_embedding.npy"

    _write_payload(
        path,
        _valid_payload() if payload is None else payload,
    )

    return AtlasPortraitFlameDynamicLandmarkEmbeddingLoader.load(
        path,
        triangle_count=triangle_count,
    )


def test_loader_returns_dynamic_embedding(
    tmp_path: Path,
):
    result = _load(
        tmp_path
    )

    assert isinstance(
        result,
        AtlasPortraitFlameDynamicLandmarkEmbedding,
    )


def test_loader_preserves_face_indices(
    tmp_path: Path,
):
    result = _load(
        tmp_path
    )

    np.testing.assert_array_equal(
        result.landmark_face_indices,
        np.array(
            [
                [10, 11, 12],
                [20, 21, 22],
            ],
            dtype=np.int64,
        ),
    )


def test_loader_preserves_barycentric_coordinates(
    tmp_path: Path,
):
    result = _load(
        tmp_path
    )

    np.testing.assert_allclose(
        result.landmark_barycentric_coordinates,
        _valid_payload()[
            "lmk_b_coords"
        ],
    )


def test_embedding_reports_dimensions(
    tmp_path: Path,
):
    result = _load(
        tmp_path
    )

    assert result.yaw_bin_count == 2
    assert result.contour_landmark_count == 3


def test_embedding_arrays_are_read_only(
    tmp_path: Path,
):
    result = _load(
        tmp_path
    )

    assert (
        result.landmark_face_indices.flags.writeable
        is False
    )
    assert (
        result
        .landmark_barycentric_coordinates
        .flags
        .writeable
        is False
    )


def test_embedding_is_frozen(
    tmp_path: Path,
):
    result = _load(
        tmp_path
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.landmark_face_indices = np.zeros(
            (
                2,
                3,
            ),
            dtype=np.int64,
        )


def test_loader_copies_payload_arrays(
    tmp_path: Path,
):
    payload = _valid_payload()

    result = _load(
        tmp_path,
        payload=payload,
    )

    payload[
        "lmk_face_idx"
    ][
        0,
        0,
    ] = 99

    payload[
        "lmk_b_coords"
    ][
        0,
        0,
        0,
    ] = 0.5

    assert result.landmark_face_indices[
        0,
        0,
    ] == 10

    assert result.landmark_barycentric_coordinates[
        0,
        0,
        0,
    ] == pytest.approx(
        1.0
    )


def test_embedding_serialization_is_deterministic(
    tmp_path: Path,
):
    first = _load(
        tmp_path
    )
    second = _load(
        tmp_path
    )

    assert first.to_dict() == second.to_dict()


def test_loader_accepts_path_string(
    tmp_path: Path,
):
    path = tmp_path / "dynamic_embedding.npy"

    _write_payload(
        path,
        _valid_payload(),
    )

    result = AtlasPortraitFlameDynamicLandmarkEmbeddingLoader.load(
        str(
            path
        ),
        triangle_count=100,
    )

    assert result.yaw_bin_count == 2


def test_loader_rejects_missing_file(
    tmp_path: Path,
):
    with pytest.raises(
        FileNotFoundError,
        match="dynamic landmark embedding",
    ):
        AtlasPortraitFlameDynamicLandmarkEmbeddingLoader.load(
            tmp_path / "missing.npy",
            triangle_count=100,
        )


@pytest.mark.parametrize(
    "payload",
    [
        np.zeros(
            (
                2,
                3,
            ),
            dtype=np.float64,
        ),
        [
            1,
            2,
            3,
        ],
        "invalid",
    ],
)
def test_loader_rejects_non_mapping_payload(
    tmp_path: Path,
    payload,
):
    with pytest.raises(
        TypeError,
        match="mapping",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


@pytest.mark.parametrize(
    "missing_key",
    [
        "lmk_face_idx",
        "lmk_b_coords",
    ],
)
def test_loader_rejects_missing_required_key(
    tmp_path: Path,
    missing_key: str,
):
    payload = _valid_payload()
    del payload[
        missing_key
    ]

    with pytest.raises(
        KeyError,
        match=missing_key,
    ):
        _load(
            tmp_path,
            payload=payload,
        )


@pytest.mark.parametrize(
    "face_indices",
    [
        np.zeros(
            (
                2,
                3,
                1,
            ),
            dtype=np.int64,
        ),
        np.zeros(
            6,
            dtype=np.int64,
        ),
        np.zeros(
            (
                0,
                3,
            ),
            dtype=np.int64,
        ),
        np.zeros(
            (
                2,
                0,
            ),
            dtype=np.int64,
        ),
    ],
)
def test_loader_rejects_invalid_face_index_shape(
    tmp_path: Path,
    face_indices: np.ndarray,
):
    payload = _valid_payload()
    payload[
        "lmk_face_idx"
    ] = face_indices

    with pytest.raises(
        ValueError,
        match="lmk_face_idx",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


def test_loader_rejects_noninteger_face_indices(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_face_idx"
    ] = np.array(
        [
            [10.0, 11.5, 12.0],
            [20.0, 21.0, 22.0],
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="lmk_face_idx",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


def test_loader_rejects_negative_face_indices(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_face_idx"
    ][
        0,
        0,
    ] = np.iinfo(
        np.uint32
    ).max

    payload[
        "lmk_face_idx"
    ] = payload[
        "lmk_face_idx"
    ].astype(
        np.int64
    )

    payload[
        "lmk_face_idx"
    ][
        0,
        0,
    ] = -1

    with pytest.raises(
        ValueError,
        match="lmk_face_idx",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


def test_loader_rejects_face_indices_outside_triangle_count(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_face_idx"
    ][
        1,
        2,
    ] = 100

    with pytest.raises(
        ValueError,
        match="triangle_count",
    ):
        _load(
            tmp_path,
            payload=payload,
            triangle_count=100,
        )


@pytest.mark.parametrize(
    "coordinates",
    [
        np.zeros(
            (
                2,
                3,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                2,
                3,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                3,
                3,
                3,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_loader_rejects_invalid_barycentric_shape(
    tmp_path: Path,
    coordinates: np.ndarray,
):
    payload = _valid_payload()
    payload[
        "lmk_b_coords"
    ] = coordinates

    with pytest.raises(
        ValueError,
        match="lmk_b_coords",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


def test_loader_rejects_nonfinite_barycentric_coordinates(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_b_coords"
    ][
        0,
        0,
        0,
    ] = np.nan

    with pytest.raises(
        ValueError,
        match="lmk_b_coords",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


def test_loader_rejects_materially_negative_barycentric_coordinates(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_b_coords"
    ][
        0,
        0,
    ] = np.array(
        [
            -0.01,
            0.51,
            0.50,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="lmk_b_coords",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


def test_loader_clamps_tiny_negative_barycentric_noise(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_b_coords"
    ][
        0,
        0,
    ] = np.array(
        [
            -1.0e-13,
            0.4,
            0.6000000000001,
        ],
        dtype=np.float64,
    )

    result = _load(
        tmp_path,
        payload=payload,
    )

    np.testing.assert_allclose(
        result.landmark_barycentric_coordinates[
            0,
            0,
        ],
        np.array(
            [
                0.0,
                0.4,
                0.6,
            ],
            dtype=np.float64,
        ),
        atol=1.0e-12,
    )


def test_loader_rejects_barycentric_sum_error(
    tmp_path: Path,
):
    payload = _valid_payload()
    payload[
        "lmk_b_coords"
    ][
        0,
        0,
    ] = np.array(
        [
            0.2,
            0.2,
            0.2,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="sum",
    ):
        _load(
            tmp_path,
            payload=payload,
        )


@pytest.mark.parametrize(
    "triangle_count",
    [
        0,
        -1,
        100.5,
        True,
    ],
)
def test_loader_rejects_invalid_triangle_count(
    tmp_path: Path,
    triangle_count,
):
    path = tmp_path / "dynamic_embedding.npy"

    _write_payload(
        path,
        _valid_payload(),
    )

    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="triangle_count",
    ):
        AtlasPortraitFlameDynamicLandmarkEmbeddingLoader.load(
            path,
            triangle_count=triangle_count,
        )
