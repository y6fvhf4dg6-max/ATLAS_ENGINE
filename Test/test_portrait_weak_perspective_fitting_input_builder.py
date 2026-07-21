from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_fitting_input import (
    AtlasPortraitWeakPerspectiveFittingInput,
)
from CORE.atlas_portrait_weak_perspective_fitting_input_builder import (
    AtlasPortraitWeakPerspectiveFittingInputBuilder,
)
from CORE.providers.portrait.atlas_flame_mediapipe_landmark_correspondence import (
    AtlasFlameMediaPipeLandmarkCorrespondence,
)


def _landmarks() -> dict[str, tuple[float, float]]:
    result = {}

    for index, name in enumerate(
        AtlasFlameMediaPipeLandmarkCorrespondence.landmark_names(),
    ):
        result[name] = (
            0.30 + index * 0.01,
            0.25 + index * 0.008,
        )

    result.update(
        {
            "chin_tip": (
                0.50,
                0.80,
            ),
            "hairline_center": (
                0.50,
                0.10,
            ),
            "left_face_edge": (
                0.75,
                0.45,
            ),
            "right_face_edge": (
                0.25,
                0.45,
            ),
        }
    )

    return result


def _landmark_result() -> AtlasPortraitLandmarkResult:
    return AtlasPortraitLandmarkResult(
        image_width=1122,
        image_height=1402,
        landmarks=_landmarks(),
        confidence=0.95,
        provider_id="manual-ground-truth-fixture",
        metadata={
            "fixture_name": (
                "portrait_graphic_v1_ground_truth"
            ),
            "image_sha256": "fixture-sha256",
            "manual_ground_truth": True,
            "synthetic": False,
            "view_type": "front",
        },
    )


def _source_points() -> np.ndarray:
    landmark_count = (
        AtlasFlameMediaPipeLandmarkCorrespondence.landmark_count()
    )

    return np.column_stack(
        (
            np.linspace(
                -0.05,
                0.05,
                landmark_count,
                dtype=np.float64,
            ),
            np.linspace(
                0.04,
                -0.05,
                landmark_count,
                dtype=np.float64,
            ),
            np.linspace(
                0.03,
                0.08,
                landmark_count,
                dtype=np.float64,
            ),
        )
    )


def test_builder_returns_fitting_input():
    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert isinstance(
        result,
        AtlasPortraitWeakPerspectiveFittingInput,
    )


def test_builder_uses_correspondence_landmark_order():
    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert result.landmark_names == (
        AtlasFlameMediaPipeLandmarkCorrespondence.landmark_names()
    )


def test_builder_selects_supported_target_landmarks():
    landmark_result = _landmark_result()

    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=landmark_result,
            source_points_3d=_source_points(),
        )
    )

    expected = np.asarray(
        [
            landmark_result.landmarks[name]
            for name in (
                AtlasFlameMediaPipeLandmarkCorrespondence
                .landmark_names()
            )
        ],
        dtype=np.float64,
    )

    assert np.array_equal(
        result.target_points_2d,
        expected,
    )


def test_builder_ignores_unsupported_ground_truth_landmarks():
    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert "chin_tip" not in result.landmark_names
    assert "hairline_center" not in result.landmark_names
    assert "left_face_edge" not in result.landmark_names
    assert "right_face_edge" not in result.landmark_names


def test_builder_preserves_source_points():
    source_points = _source_points()

    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=source_points,
        )
    )

    assert np.array_equal(
        result.source_points_3d,
        source_points,
    )


def test_builder_uses_uniform_default_weights():
    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert np.array_equal(
        result.landmark_weights,
        np.ones(
            result.landmark_count,
            dtype=np.float64,
        ),
    )


def test_builder_accepts_explicit_weights():
    weights = np.linspace(
        0.75,
        1.0,
        AtlasFlameMediaPipeLandmarkCorrespondence.landmark_count(),
        dtype=np.float64,
    )

    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
            landmark_weights=weights,
        )
    )

    assert np.array_equal(
        result.landmark_weights,
        weights,
    )


def test_builder_preserves_image_dimensions():
    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert result.image_width == 1122
    assert result.image_height == 1402


def test_builder_records_deterministic_provenance():
    result = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert result.metadata == {
        "correspondence_version": (
            "flame-mediapipe-ground-truth-v1"
        ),
        "input_view": "front",
        "landmark_provider_id": (
            "manual-ground-truth-fixture"
        ),
        "model_family": "flame",
        "portrait_fixture": (
            "portrait_graphic_v1_ground_truth"
        ),
        "source_image_sha256": "fixture-sha256",
        "synthetic": False,
    }


def test_builder_is_deterministic():
    first = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    second = (
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
        )
    )

    assert first.to_dict() == second.to_dict()


def test_builder_rejects_wrong_landmark_result_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitLandmarkResult",
    ):
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result={
                "landmarks": {},
            },
            source_points_3d=_source_points(),
        )


def test_builder_rejects_missing_supported_landmark():
    landmark_result = _landmark_result()

    landmarks = dict(
        landmark_result.landmarks,
    )

    del landmarks[
        "nose_tip"
    ]

    incomplete_result = AtlasPortraitLandmarkResult(
        image_width=landmark_result.image_width,
        image_height=landmark_result.image_height,
        landmarks=landmarks,
        confidence=landmark_result.confidence,
        provider_id=landmark_result.provider_id,
        metadata=landmark_result.metadata,
    )

    with pytest.raises(
        ValueError,
        match="nose_tip",
    ):
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=incomplete_result,
            source_points_3d=_source_points(),
        )


def test_builder_rejects_wrong_source_point_count():
    with pytest.raises(
        ValueError,
        match="source_points_3d",
    ):
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points()[:-1],
        )


def test_builder_rejects_wrong_weight_count():
    with pytest.raises(
        ValueError,
        match="landmark_weights",
    ):
        AtlasPortraitWeakPerspectiveFittingInputBuilder.build(
            landmark_result=_landmark_result(),
            source_points_3d=_source_points(),
            landmark_weights=np.ones(
                16,
                dtype=np.float64,
            ),
        )
