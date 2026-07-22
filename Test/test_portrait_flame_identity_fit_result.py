from __future__ import annotations

import math

import numpy as np
import pytest

from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _camera() -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=2.75,
        translation_x=0.43,
        translation_y=0.52,
        projected_points_2d=np.array(
            [
                [0.30, 0.35],
                [0.50, 0.48],
                [0.70, 0.35],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.0041,
        metadata={
            "camera_model": "weak_perspective",
            "coordinate_space": "normalized",
            "synthetic": True,
        },
    )


def _identity_parameters() -> np.ndarray:
    return np.array(
        [
            -0.70,
            -2.10,
            -1.18,
            -0.55,
            2.30,
        ],
        dtype=np.float64,
    )


def _make_result(
    **overrides,
) -> AtlasPortraitFlameIdentityFitResult:
    arguments = {
        "identity_parameters": _identity_parameters(),
        "camera": _camera(),
        "initial_weighted_root_mean_square_error": 0.0065,
        "final_weighted_root_mean_square_error": 0.0041,
        "regularization_weight": 1.0e-5,
        "function_evaluation_count": 10,
        "optimizer_success": True,
        "optimizer_status": 2,
        "optimizer_message": (
            "`ftol` termination condition is satisfied."
        ),
        "metadata": {
            "active_identity_count": 5,
            "fitting_stage": "dense_identity",
            "landmark_count": 105,
            "model_family": "flame",
            "synthetic": False,
        },
    }
    arguments.update(
        overrides
    )

    return AtlasPortraitFlameIdentityFitResult(
        **arguments
    )


def test_result_preserves_identity_fit_values():
    result = _make_result()

    np.testing.assert_allclose(
        result.identity_parameters,
        _identity_parameters(),
    )

    assert result.camera is not None
    assert result.camera.scale == pytest.approx(
        2.75
    )
    assert (
        result.initial_weighted_root_mean_square_error
        == pytest.approx(0.0065)
    )
    assert (
        result.final_weighted_root_mean_square_error
        == pytest.approx(0.0041)
    )
    assert result.regularization_weight == pytest.approx(
        1.0e-5
    )
    assert result.function_evaluation_count == 10
    assert result.optimizer_success is True
    assert result.optimizer_status == 2
    assert (
        result.optimizer_message
        == "`ftol` termination condition is satisfied."
    )


def test_result_exposes_parameter_statistics():
    result = _make_result()

    assert result.identity_parameter_count == 5
    assert result.identity_parameter_l2_norm == pytest.approx(
        np.linalg.norm(
            _identity_parameters()
        )
    )
    assert (
        result.maximum_absolute_identity_parameter
        == pytest.approx(2.30)
    )


def test_result_exposes_error_improvement():
    result = _make_result()

    assert result.error_improvement == pytest.approx(
        0.0024
    )
    assert result.relative_error_improvement == pytest.approx(
        0.0024 / 0.0065
    )


def test_result_arrays_and_metadata_are_immutable_snapshots():
    parameters = _identity_parameters()
    metadata = {
        "landmark_count": 105,
    }

    result = _make_result(
        identity_parameters=parameters,
        metadata=metadata,
    )

    parameters[0] = 99.0
    metadata["landmark_count"] = 17

    assert result.identity_parameters[0] == pytest.approx(
        -0.70
    )
    assert result.metadata["landmark_count"] == 105
    assert result.identity_parameters.flags.writeable is False

    with pytest.raises(
        ValueError
    ):
        result.identity_parameters[0] = 0.0

    with pytest.raises(
        TypeError
    ):
        result.metadata["landmark_count"] = 17


def test_result_camera_is_an_independent_snapshot():
    camera = _camera()

    result = _make_result(
        camera=camera
    )

    assert result.camera is not camera
    assert result.camera.to_dict() == camera.to_dict()


def test_result_to_dict_is_deterministic():
    result = _make_result(
        metadata={
            "zeta": 2,
            "alpha": 1,
        }
    )

    payload = result.to_dict()

    assert payload["identity_parameter_count"] == 5
    assert payload["identity_parameters"] == pytest.approx(
        _identity_parameters().tolist()
    )
    assert payload["regularization_weight"] == pytest.approx(
        1.0e-5
    )
    assert payload["error_improvement"] == pytest.approx(
        0.0024
    )
    assert payload["relative_error_improvement"] == pytest.approx(
        0.0024 / 0.0065
    )
    assert payload["camera"]["scale"] == pytest.approx(
        2.75
    )
    assert payload["metadata"] == {
        "alpha": 1,
        "zeta": 2,
    }


def test_result_rejects_wrong_camera_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitWeakPerspectiveCamera",
    ):
        _make_result(
            camera=object()
        )


@pytest.mark.parametrize(
    (
        "overrides",
        "match",
    ),
    [
        (
            {
                "identity_parameters": [],
            },
            "identity_parameters",
        ),
        (
            {
                "identity_parameters": [
                    0.0,
                    math.nan,
                ],
            },
            "finite",
        ),
        (
            {
                "initial_weighted_root_mean_square_error": -0.1,
            },
            "initial",
        ),
        (
            {
                "final_weighted_root_mean_square_error": -0.1,
            },
            "final",
        ),
        (
            {
                "final_weighted_root_mean_square_error": 0.007,
            },
            "must not exceed",
        ),
        (
            {
                "regularization_weight": -1.0e-5,
            },
            "regularization_weight",
        ),
        (
            {
                "function_evaluation_count": 0,
            },
            "function_evaluation_count",
        ),
        (
            {
                "optimizer_success": 1,
            },
            "optimizer_success",
        ),
        (
            {
                "optimizer_status": 1.5,
            },
            "optimizer_status",
        ),
        (
            {
                "optimizer_message": "",
            },
            "optimizer_message",
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
