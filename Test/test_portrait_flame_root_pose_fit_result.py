from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _camera():
    return AtlasPortraitWeakPerspectiveCamera(
        scale=2.75,
        translation_x=0.42,
        translation_y=0.51,
        projected_points_2d=np.array(
            [
                [0.40, 0.30],
                [0.60, 0.30],
                [0.50, 0.60],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.006,
        metadata={
            "camera_model": "weak_perspective",
            "synthetic": True,
        },
    )


def _result(
    **overrides,
):
    values = {
        "root_pose_parameters": np.array(
            [
                -0.20,
                -0.04,
                0.03,
            ],
            dtype=np.float64,
        ),
        "camera": _camera(),
        "initial_weighted_root_mean_square_error": 0.011,
        "final_weighted_root_mean_square_error": 0.006,
        "function_evaluation_count": 9,
        "optimizer_success": True,
        "optimizer_status": 2,
        "optimizer_message": (
            "`ftol` termination condition is satisfied."
        ),
        "metadata": {
            "fitting_stage": "root_pose",
            "model_family": "flame",
            "synthetic": True,
        },
    }

    values.update(
        overrides
    )

    return AtlasPortraitFlameRootPoseFitResult(
        **values
    )


def test_result_stores_root_pose_parameters():
    result = _result()

    np.testing.assert_allclose(
        result.root_pose_parameters,
        np.array(
            [
                -0.20,
                -0.04,
                0.03,
            ],
            dtype=np.float64,
        ),
    )


def test_result_exposes_three_root_pose_parameters():
    result = _result()

    assert result.root_pose_parameter_count == 3


def test_result_stores_camera():
    result = _result()

    assert isinstance(
        result.camera,
        AtlasPortraitWeakPerspectiveCamera,
    )


def test_result_reports_error_improvement():
    result = _result()

    assert result.error_improvement == pytest.approx(
        0.005
    )

    assert (
        result.relative_error_improvement
        == pytest.approx(
            1.0 - 0.006 / 0.011
        )
    )


def test_result_arrays_are_float64_read_only_copies():
    source = np.array(
        [
            -0.20,
            -0.04,
            0.03,
        ],
        dtype=np.float32,
    )

    result = _result(
        root_pose_parameters=source
    )

    assert result.root_pose_parameters.dtype == np.float64
    assert result.root_pose_parameters.flags.writeable is False
    assert not np.shares_memory(
        result.root_pose_parameters,
        source,
    )


def test_result_metadata_is_immutable():
    result = _result()

    with pytest.raises(
        TypeError,
    ):
        result.metadata[
            "new"
        ] = "value"


def test_result_to_dict_is_deterministic():
    first = _result()
    second = _result()

    assert first.to_dict() == second.to_dict()


@pytest.mark.parametrize(
    "root_pose_parameters",
    [
        np.zeros(
            2,
            dtype=np.float64,
        ),
        np.zeros(
            4,
            dtype=np.float64,
        ),
        np.zeros(
            (
                1,
                3,
            ),
            dtype=np.float64,
        ),
    ],
)
def test_result_rejects_invalid_root_pose_shape(
    root_pose_parameters,
):
    with pytest.raises(
        ValueError,
        match=r"shape \(3,\)",
    ):
        _result(
            root_pose_parameters=root_pose_parameters
        )


def test_result_rejects_non_finite_root_pose():
    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        _result(
            root_pose_parameters=np.array(
                [
                    0.0,
                    np.nan,
                    0.0,
                ],
                dtype=np.float64,
            )
        )


def test_result_rejects_wrong_camera_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitWeakPerspectiveCamera",
    ):
        _result(
            camera=object()
        )


def test_result_rejects_final_error_above_initial_error():
    with pytest.raises(
        ValueError,
        match="must not exceed",
    ):
        _result(
            initial_weighted_root_mean_square_error=0.005,
            final_weighted_root_mean_square_error=0.006,
        )


def test_result_rejects_non_positive_function_evaluation_count():
    with pytest.raises(
        ValueError,
        match="function_evaluation_count",
    ):
        _result(
            function_evaluation_count=0
        )
