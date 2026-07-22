from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _camera(
    *,
    error: float,
    point_count: int,
) -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=2.75,
        translation_x=0.43,
        translation_y=0.52,
        projected_points_2d=np.full(
            (
                point_count,
                2,
            ),
            0.5,
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=error,
        metadata={
            "camera_model": "weak_perspective",
            "synthetic": True,
        },
    )


def _root_pose_result() -> (
    AtlasPortraitFlameRootPoseFitResult
):
    return AtlasPortraitFlameRootPoseFitResult(
        root_pose_parameters=np.array(
            [
                -0.20,
                -0.04,
                0.03,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            error=0.0067,
            point_count=17,
        ),
        initial_weighted_root_mean_square_error=(
            0.0111
        ),
        final_weighted_root_mean_square_error=(
            0.0067
        ),
        function_evaluation_count=21,
        optimizer_success=True,
        optimizer_status=2,
        optimizer_message=(
            "`ftol` termination condition is satisfied."
        ),
        metadata={
            "fitting_stage": "root_pose",
            "landmark_count": 17,
            "synthetic": True,
        },
    )


def _identity_fit_result() -> (
    AtlasPortraitFlameIdentityFitResult
):
    parameters = np.zeros(
        300,
        dtype=np.float64,
    )
    parameters[
        :5
    ] = np.array(
        [
            -0.72,
            -2.15,
            -1.18,
            -0.56,
            2.30,
        ],
        dtype=np.float64,
    )

    return AtlasPortraitFlameIdentityFitResult(
        identity_parameters=parameters,
        camera=_camera(
            error=0.0042,
            point_count=105,
        ),
        initial_weighted_root_mean_square_error=(
            0.0065
        ),
        final_weighted_root_mean_square_error=(
            0.0042
        ),
        regularization_weight=1.0e-5,
        function_evaluation_count=14,
        optimizer_success=True,
        optimizer_status=2,
        optimizer_message=(
            "`ftol` termination condition is satisfied."
        ),
        metadata={
            "active_identity_count": 20,
            "fitting_stage": "dense_identity",
            "landmark_count": 105,
            "synthetic": True,
        },
    )


def _make_result(
    **overrides,
) -> AtlasPortraitFlameDenseIdentityPipelineResult:
    arguments = {
        "root_pose_result": _root_pose_result(),
        "identity_fit_result": _identity_fit_result(),
        "metadata": {
            "pipeline": "flame_dense_identity",
            "model_family": "flame",
            "synthetic": True,
        },
    }
    arguments.update(
        overrides
    )

    return AtlasPortraitFlameDenseIdentityPipelineResult(
        **arguments
    )


def test_result_preserves_pipeline_stage_results():
    result = _make_result()

    assert isinstance(
        result.root_pose_result,
        AtlasPortraitFlameRootPoseFitResult,
    )
    assert isinstance(
        result.identity_fit_result,
        AtlasPortraitFlameIdentityFitResult,
    )


def test_result_exposes_final_root_pose_parameters():
    result = _make_result()

    np.testing.assert_allclose(
        result.final_root_pose_parameters,
        np.array(
            [
                -0.20,
                -0.04,
                0.03,
            ],
            dtype=np.float64,
        ),
    )

    assert (
        result.final_root_pose_parameters.flags.writeable
        is False
    )


def test_result_exposes_final_identity_parameters():
    result = _make_result()

    np.testing.assert_allclose(
        result.final_identity_parameters[
            :5
        ],
        np.array(
            [
                -0.72,
                -2.15,
                -1.18,
                -0.56,
                2.30,
            ],
            dtype=np.float64,
        ),
    )

    assert (
        result.final_identity_parameters.flags.writeable
        is False
    )


def test_result_exposes_final_camera():
    result = _make_result()

    assert result.final_camera.to_dict() == (
        result.identity_fit_result.camera.to_dict()
    )
    assert result.final_camera is not (
        result.identity_fit_result.camera
    )


def test_result_exposes_stage_error_improvements():
    result = _make_result()

    assert (
        result.root_pose_error_improvement
        == pytest.approx(
            0.0111 - 0.0067
        )
    )
    assert (
        result.root_pose_relative_error_improvement
        == pytest.approx(
            (
                0.0111
                - 0.0067
            )
            / 0.0111
        )
    )
    assert (
        result.identity_error_improvement
        == pytest.approx(
            0.0065 - 0.0042
        )
    )
    assert (
        result.identity_relative_error_improvement
        == pytest.approx(
            (
                0.0065
                - 0.0042
            )
            / 0.0065
        )
    )


def test_result_exposes_combined_optimizer_statistics():
    result = _make_result()

    assert (
        result.total_function_evaluation_count
        == 35
    )
    assert result.optimizer_success is True


def test_result_nested_results_are_independent_snapshots():
    root_result = _root_pose_result()
    identity_result = _identity_fit_result()

    result = _make_result(
        root_pose_result=root_result,
        identity_fit_result=identity_result,
    )

    assert result.root_pose_result is not root_result
    assert result.identity_fit_result is not identity_result

    assert (
        result.root_pose_result.to_dict()
        == root_result.to_dict()
    )
    assert (
        result.identity_fit_result.to_dict()
        == identity_result.to_dict()
    )


def test_result_metadata_is_immutable_snapshot():
    metadata = {
        "pipeline": "flame_dense_identity",
        "synthetic": True,
    }

    result = _make_result(
        metadata=metadata
    )

    metadata[
        "synthetic"
    ] = False

    assert result.metadata[
        "synthetic"
    ] is True

    with pytest.raises(
        TypeError
    ):
        result.metadata[
            "synthetic"
        ] = False


def test_result_to_dict_is_deterministic():
    result = _make_result(
        metadata={
            "zeta": 2,
            "alpha": 1,
        }
    )

    payload = result.to_dict()

    assert payload[
        "root_pose_result"
    ] == result.root_pose_result.to_dict()

    assert payload[
        "identity_fit_result"
    ] == result.identity_fit_result.to_dict()

    assert payload[
        "final_root_pose_parameters"
    ] == pytest.approx(
        [
            -0.20,
            -0.04,
            0.03,
        ]
    )

    assert payload[
        "final_identity_parameters"
    ][
        :5
    ] == pytest.approx(
        [
            -0.72,
            -2.15,
            -1.18,
            -0.56,
            2.30,
        ]
    )

    assert payload[
        "total_function_evaluation_count"
    ] == 35

    assert payload[
        "optimizer_success"
    ] is True

    assert payload[
        "metadata"
    ] == {
        "alpha": 1,
        "zeta": 2,
    }


def test_result_reports_failure_when_root_optimizer_failed():
    root_result = _root_pose_result()

    failed_root = AtlasPortraitFlameRootPoseFitResult(
        root_pose_parameters=(
            root_result.root_pose_parameters
        ),
        camera=root_result.camera,
        initial_weighted_root_mean_square_error=(
            root_result
            .initial_weighted_root_mean_square_error
        ),
        final_weighted_root_mean_square_error=(
            root_result
            .final_weighted_root_mean_square_error
        ),
        function_evaluation_count=(
            root_result.function_evaluation_count
        ),
        optimizer_success=False,
        optimizer_status=0,
        optimizer_message=(
            "Maximum evaluations reached."
        ),
        metadata=root_result.metadata,
    )

    result = _make_result(
        root_pose_result=failed_root
    )

    assert result.optimizer_success is False


def test_result_reports_failure_when_identity_optimizer_failed():
    identity_result = _identity_fit_result()

    failed_identity = AtlasPortraitFlameIdentityFitResult(
        identity_parameters=(
            identity_result.identity_parameters
        ),
        camera=identity_result.camera,
        initial_weighted_root_mean_square_error=(
            identity_result
            .initial_weighted_root_mean_square_error
        ),
        final_weighted_root_mean_square_error=(
            identity_result
            .final_weighted_root_mean_square_error
        ),
        regularization_weight=(
            identity_result.regularization_weight
        ),
        function_evaluation_count=(
            identity_result.function_evaluation_count
        ),
        optimizer_success=False,
        optimizer_status=0,
        optimizer_message=(
            "Maximum evaluations reached."
        ),
        metadata=identity_result.metadata,
    )

    result = _make_result(
        identity_fit_result=failed_identity
    )

    assert result.optimizer_success is False


def test_result_rejects_wrong_root_pose_result_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameRootPoseFitResult",
    ):
        _make_result(
            root_pose_result=object()
        )


def test_result_rejects_wrong_identity_fit_result_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameIdentityFitResult",
    ):
        _make_result(
            identity_fit_result=object()
        )


def test_result_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _make_result(
            metadata=None
        )
