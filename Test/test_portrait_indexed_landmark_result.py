from __future__ import annotations

import math

import numpy as np
import pytest

from CORE.atlas_portrait_indexed_landmark_result import (
    AtlasPortraitIndexedLandmarkResult,
)


def _landmark_ids() -> tuple[int, ...]:
    return (
        4,
        33,
        133,
        263,
    )


def _landmarks_3d() -> np.ndarray:
    return np.array(
        [
            [0.50, 0.40, -0.10],
            [0.30, 0.35, -0.05],
            [0.40, 0.35, -0.04],
            [0.70, 0.35, -0.05],
        ],
        dtype=np.float64,
    )


def _make_result(
    **overrides,
) -> AtlasPortraitIndexedLandmarkResult:
    arguments = {
        "image_width": 1024,
        "image_height": 768,
        "landmark_ids": _landmark_ids(),
        "landmarks_3d": _landmarks_3d(),
        "confidence": 0.98,
        "provider_id": (
            "mediapipe-face-landmarker-tasks"
        ),
        "metadata": {
            "schema_version": (
                "atlas-mediapipe-face-landmarks-v1"
            ),
            "synthetic": False,
        },
    }
    arguments.update(
        overrides
    )

    return AtlasPortraitIndexedLandmarkResult(
        **arguments
    )


def test_result_preserves_indexed_landmarks():
    result = _make_result()

    assert result.image_width == 1024
    assert result.image_height == 768
    assert result.landmark_ids == (
        4,
        33,
        133,
        263,
    )
    assert result.landmark_count == 4
    assert result.confidence == pytest.approx(
        0.98
    )
    assert result.provider_id == (
        "mediapipe-face-landmarker-tasks"
    )

    np.testing.assert_allclose(
        result.landmarks_3d,
        _landmarks_3d(),
    )


def test_result_exposes_two_dimensional_points():
    result = _make_result()

    np.testing.assert_allclose(
        result.points_2d,
        np.array(
            [
                [0.50, 0.40],
                [0.30, 0.35],
                [0.40, 0.35],
                [0.70, 0.35],
            ],
            dtype=np.float64,
        ),
    )

    assert result.points_2d.dtype == np.float64
    assert result.points_2d.flags.writeable is False


def test_result_builds_landmark_index_mapping():
    result = _make_result()

    assert result.index_by_id == {
        4: 0,
        33: 1,
        133: 2,
        263: 3,
    }

    with pytest.raises(
        TypeError
    ):
        result.index_by_id[
            4
        ] = 99


def test_result_returns_landmark_by_id():
    result = _make_result()

    np.testing.assert_allclose(
        result.landmark_3d(
            133
        ),
        np.array(
            [
                0.40,
                0.35,
                -0.04,
            ],
            dtype=np.float64,
        ),
    )

    np.testing.assert_allclose(
        result.landmark_2d(
            263
        ),
        np.array(
            [
                0.70,
                0.35,
            ],
            dtype=np.float64,
        ),
    )


def test_result_rejects_unknown_landmark_id_lookup():
    result = _make_result()

    with pytest.raises(
        KeyError
    ):
        result.landmark_3d(
            999
        )

    with pytest.raises(
        KeyError
    ):
        result.landmark_2d(
            999
        )


def test_result_returns_pixel_landmark_by_id():
    result = _make_result(
        image_width=1001,
        image_height=801,
        landmark_ids=(
            0,
            1,
            2,
        ),
        landmarks_3d=np.array(
            [
                [0.0, 0.0, -0.1],
                [0.5, 0.5, 0.0],
                [1.0, 1.0, 0.1],
            ],
            dtype=np.float64,
        ),
    )

    assert result.pixel_landmark(
        0
    ) == (
        0.0,
        0.0,
    )
    assert result.pixel_landmark(
        1
    ) == (
        500.0,
        400.0,
    )
    assert result.pixel_landmark(
        2
    ) == (
        1000.0,
        800.0,
    )


def test_result_converts_numeric_values():
    result = _make_result(
        image_width=1024.0,
        image_height=768.0,
        landmarks_3d=[
            [
                0.50,
                0.40,
                -0.10,
            ],
            [
                0.30,
                0.35,
                -0.05,
            ],
            [
                0.40,
                0.35,
                -0.04,
            ],
            [
                0.70,
                0.35,
                -0.05,
            ],
        ],
        confidence=1,
    )

    assert result.image_width == 1024
    assert result.image_height == 768
    assert result.confidence == 1.0
    assert result.landmarks_3d.dtype == np.float64


def test_result_strips_provider_id_whitespace():
    result = _make_result(
        provider_id=(
            "  mediapipe-face-landmarker-tasks  "
        )
    )

    assert result.provider_id == (
        "mediapipe-face-landmarker-tasks"
    )


def test_result_arrays_are_immutable_snapshots():
    source_points = _landmarks_3d()

    result = _make_result(
        landmarks_3d=source_points
    )

    source_points[
        0,
        0,
    ] = 0.0

    assert result.landmarks_3d[
        0,
        0,
    ] == pytest.approx(
        0.50
    )
    assert result.landmarks_3d.flags.writeable is False

    with pytest.raises(
        ValueError
    ):
        result.landmarks_3d[
            0,
            0,
        ] = 0.0


def test_result_metadata_is_immutable_snapshot():
    source_metadata = {
        "synthetic": False,
    }

    result = _make_result(
        metadata=source_metadata
    )

    source_metadata[
        "synthetic"
    ] = True

    assert result.metadata[
        "synthetic"
    ] is False

    with pytest.raises(
        TypeError
    ):
        result.metadata[
            "synthetic"
        ] = True


def test_result_to_dict_is_deterministic():
    result = _make_result(
        metadata={
            "zeta": 2,
            "alpha": 1,
        }
    )

    assert result.to_dict() == {
        "image_width": 1024,
        "image_height": 768,
        "landmark_count": 4,
        "landmark_ids": [
            4,
            33,
            133,
            263,
        ],
        "landmarks_3d": [
            [
                0.50,
                0.40,
                -0.10,
            ],
            [
                0.30,
                0.35,
                -0.05,
            ],
            [
                0.40,
                0.35,
                -0.04,
            ],
            [
                0.70,
                0.35,
                -0.05,
            ],
        ],
        "confidence": 0.98,
        "provider_id": (
            "mediapipe-face-landmarker-tasks"
        ),
        "metadata": {
            "alpha": 1,
            "zeta": 2,
        },
    }


@pytest.mark.parametrize(
    (
        "overrides",
        "match",
    ),
    [
        (
            {
                "image_width": 0,
            },
            "image_width",
        ),
        (
            {
                "image_width": 1000.5,
            },
            "image_width",
        ),
        (
            {
                "image_height": -1,
            },
            "image_height",
        ),
        (
            {
                "image_height": math.inf,
            },
            "image_height",
        ),
        (
            {
                "landmark_ids": (),
                "landmarks_3d": np.empty(
                    (
                        0,
                        3,
                    ),
                    dtype=np.float64,
                ),
            },
            "landmark_ids",
        ),
        (
            {
                "landmark_ids": (
                    4,
                    33,
                    33,
                    263,
                ),
            },
            "unique",
        ),
        (
            {
                "landmark_ids": (
                    4,
                    -1,
                    133,
                    263,
                ),
            },
            "negative",
        ),
        (
            {
                "landmark_ids": (
                    4,
                    33.5,
                    133,
                    263,
                ),
            },
            "integer",
        ),
        (
            {
                "landmark_ids": (
                    4,
                    True,
                    133,
                    263,
                ),
            },
            "integer",
        ),
        (
            {
                "landmarks_3d": np.zeros(
                    (
                        4,
                        2,
                    ),
                    dtype=np.float64,
                ),
            },
            r"\(4, 3\)",
        ),
        (
            {
                "landmarks_3d": np.zeros(
                    (
                        3,
                        3,
                    ),
                    dtype=np.float64,
                ),
            },
            r"\(4, 3\)",
        ),
        (
            {
                "landmarks_3d": np.array(
                    [
                        [
                            math.nan,
                            0.4,
                            0.0,
                        ],
                        [
                            0.3,
                            0.3,
                            0.0,
                        ],
                        [
                            0.4,
                            0.3,
                            0.0,
                        ],
                        [
                            0.7,
                            0.3,
                            0.0,
                        ],
                    ]
                ),
            },
            "finite",
        ),
        (
            {
                "landmarks_3d": np.array(
                    [
                        [
                            -0.01,
                            0.4,
                            0.0,
                        ],
                        [
                            0.3,
                            0.3,
                            0.0,
                        ],
                        [
                            0.4,
                            0.3,
                            0.0,
                        ],
                        [
                            0.7,
                            0.3,
                            0.0,
                        ],
                    ]
                ),
            },
            "0.0..1.0",
        ),
        (
            {
                "landmarks_3d": np.array(
                    [
                        [
                            0.5,
                            1.01,
                            0.0,
                        ],
                        [
                            0.3,
                            0.3,
                            0.0,
                        ],
                        [
                            0.4,
                            0.3,
                            0.0,
                        ],
                        [
                            0.7,
                            0.3,
                            0.0,
                        ],
                    ]
                ),
            },
            "0.0..1.0",
        ),
        (
            {
                "confidence": -0.01,
            },
            "confidence",
        ),
        (
            {
                "confidence": math.nan,
            },
            "confidence",
        ),
        (
            {
                "provider_id": "",
            },
            "provider_id",
        ),
        (
            {
                "provider_id": 123,
            },
            "provider_id",
        ),
        (
            {
                "metadata": None,
            },
            "metadata",
        ),
    ],
)
def test_result_rejects_invalid_values(
    overrides,
    match,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=match,
    ):
        _make_result(
            **overrides
        )
