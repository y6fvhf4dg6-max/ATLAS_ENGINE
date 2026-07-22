from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_dense_weak_perspective_fitting_input_builder import (
    AtlasPortraitDenseWeakPerspectiveFittingInputBuilder,
)
from CORE.atlas_portrait_indexed_landmark_result import (
    AtlasPortraitIndexedLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)


def _indexed_result(
    **overrides,
) -> AtlasPortraitIndexedLandmarkResult:
    arguments = {
        "image_width": 1024,
        "image_height": 768,
        "landmark_ids": (
            4,
            33,
            133,
            197,
            263,
        ),
        "landmarks_3d": np.array(
            [
                [0.50, 0.48, -0.10],
                [0.30, 0.35, -0.05],
                [0.40, 0.35, -0.04],
                [0.50, 0.42, -0.08],
                [0.70, 0.35, -0.05],
            ],
            dtype=np.float64,
        ),
        "confidence": 0.99,
        "provider_id": (
            "mediapipe-face-landmarker-tasks"
        ),
        "metadata": {
            "schema_version": (
                "atlas-mediapipe-face-landmarks-v1"
            ),
            "image_sha256": "abc123",
            "synthetic": False,
            "view_type": "front",
        },
    }
    arguments.update(
        overrides
    )

    return AtlasPortraitIndexedLandmarkResult(
        **arguments
    )


def _source_points() -> np.ndarray:
    return np.array(
        [
            [-0.10, 0.20, 0.30],
            [0.00, 0.10, 0.40],
            [0.10, 0.20, 0.50],
        ],
        dtype=np.float64,
    )


def _requested_ids() -> tuple[int, ...]:
    return (
        263,
        4,
        197,
    )


def test_builder_returns_weak_perspective_fitting_input():
    result = (
        AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
        .build(
            landmark_result=_indexed_result(),
            source_points_3d=_source_points(),
            requested_mediapipe_ids=_requested_ids(),
        )
    )

    assert isinstance(
        result,
        AtlasPortraitWeakPerspectiveFittingInput,
    )


def test_builder_preserves_requested_id_order():
    result = (
        AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
        .build(
            landmark_result=_indexed_result(),
            source_points_3d=_source_points(),
            requested_mediapipe_ids=_requested_ids(),
        )
    )

    assert result.landmark_names == (
        "mediapipe_263",
        "mediapipe_4",
        "mediapipe_197",
    )

    np.testing.assert_allclose(
        result.target_points_2d,
        np.array(
            [
                [0.70, 0.35],
                [0.50, 0.48],
                [0.50, 0.42],
            ],
            dtype=np.float64,
        ),
    )


def test_builder_preserves_source_points():
    source_points = _source_points()

    result = (
        AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
        .build(
            landmark_result=_indexed_result(),
            source_points_3d=source_points,
            requested_mediapipe_ids=_requested_ids(),
        )
    )

    np.testing.assert_allclose(
        result.source_points_3d,
        source_points,
    )


def test_builder_uses_unit_weights_by_default():
    result = (
        AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
        .build(
            landmark_result=_indexed_result(),
            source_points_3d=_source_points(),
            requested_mediapipe_ids=_requested_ids(),
        )
    )

    np.testing.assert_allclose(
        result.landmark_weights,
        np.ones(
            3,
            dtype=np.float64,
        ),
    )


def test_builder_preserves_explicit_weights():
    weights = np.array(
        [
            2.0,
            1.5,
            0.5,
        ],
        dtype=np.float64,
    )

    result = (
        AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
        .build(
            landmark_result=_indexed_result(),
            source_points_3d=_source_points(),
            requested_mediapipe_ids=_requested_ids(),
            landmark_weights=weights,
        )
    )

    np.testing.assert_allclose(
        result.landmark_weights,
        weights,
    )


def test_builder_preserves_dimensions_and_metadata():
    result = (
        AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
        .build(
            landmark_result=_indexed_result(),
            source_points_3d=_source_points(),
            requested_mediapipe_ids=_requested_ids(),
        )
    )

    assert result.image_width == 1024
    assert result.image_height == 768

    assert result.metadata == {
        "correspondence_type": (
            "indexed-mediapipe"
        ),
        "input_view": "front",
        "landmark_count": 3,
        "landmark_provider_id": (
            "mediapipe-face-landmarker-tasks"
        ),
        "model_family": "flame",
        "source_image_sha256": "abc123",
        "synthetic": False,
    }


def test_builder_does_not_modify_sources():
    source_points = _source_points()
    weights = np.array(
        [
            2.0,
            1.5,
            0.5,
        ],
        dtype=np.float64,
    )

    source_before = source_points.copy()
    weights_before = weights.copy()

    AtlasPortraitDenseWeakPerspectiveFittingInputBuilder.build(
        landmark_result=_indexed_result(),
        source_points_3d=source_points,
        requested_mediapipe_ids=_requested_ids(),
        landmark_weights=weights,
    )

    np.testing.assert_array_equal(
        source_points,
        source_before,
    )
    np.testing.assert_array_equal(
        weights,
        weights_before,
    )


def test_builder_rejects_wrong_landmark_result_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitIndexedLandmarkResult",
    ):
        (
            AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
            .build(
                landmark_result=object(),
                source_points_3d=_source_points(),
                requested_mediapipe_ids=_requested_ids(),
            )
        )


@pytest.mark.parametrize(
    "requested_ids",
    [
        None,
        (),
        "4,33,133",
        (
            4,
            4,
            197,
        ),
        (
            4,
            -1,
            197,
        ),
        (
            4,
            33.5,
            197,
        ),
        (
            4,
            True,
            197,
        ),
    ],
)
def test_builder_rejects_invalid_requested_ids(
    requested_ids,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
    ):
        (
            AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
            .build(
                landmark_result=_indexed_result(),
                source_points_3d=_source_points(),
                requested_mediapipe_ids=requested_ids,
            )
        )


def test_builder_rejects_missing_requested_id():
    with pytest.raises(
        ValueError,
        match="999",
    ):
        (
            AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
            .build(
                landmark_result=_indexed_result(),
                source_points_3d=_source_points(),
                requested_mediapipe_ids=(
                    4,
                    33,
                    999,
                ),
            )
        )


def test_builder_rejects_source_point_count_mismatch():
    with pytest.raises(
        ValueError,
        match=r"\(3, 3\)",
    ):
        (
            AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
            .build(
                landmark_result=_indexed_result(),
                source_points_3d=np.zeros(
                    (
                        2,
                        3,
                    ),
                    dtype=np.float64,
                ),
                requested_mediapipe_ids=_requested_ids(),
            )
        )


def test_builder_rejects_weight_count_mismatch():
    with pytest.raises(
        ValueError,
        match=r"\(3,\)",
    ):
        (
            AtlasPortraitDenseWeakPerspectiveFittingInputBuilder
            .build(
                landmark_result=_indexed_result(),
                source_points_3d=_source_points(),
                requested_mediapipe_ids=_requested_ids(),
                landmark_weights=np.ones(
                    2,
                    dtype=np.float64,
                ),
            )
        )
