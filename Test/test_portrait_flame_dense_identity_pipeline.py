from __future__ import annotations

import math

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline import (
    AtlasPortraitFlameDenseIdentityPipeline,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_flame_identity_fitter import (
    AtlasPortraitFlameIdentityFitter,
)
from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_flame_root_pose_fitter import (
    AtlasPortraitFlameRootPoseFitter,
)
from CORE.atlas_portrait_indexed_landmark_result import (
    AtlasPortraitIndexedLandmarkResult,
)
from CORE.atlas_portrait_landmark_result import (
    AtlasPortraitLandmarkResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _model() -> AtlasPortraitFlameCanonicalModel:
    return AtlasPortraitFlameCanonicalModel(
        template_vertices=np.array(
            [
                [-0.5, -0.5, 0.0],
                [0.5, -0.5, 0.0],
                [0.0, 0.5, 0.1],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
            ],
            dtype=np.int64,
        ),
        identity_shape_directions=np.zeros(
            (
                3,
                3,
                4,
            ),
            dtype=np.float64,
        ),
        expression_shape_directions=np.zeros(
            (
                3,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        pose_directions=np.zeros(
            (
                3,
                3,
                9,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=6,
        joint_regressor=np.array(
            [
                [
                    1.0 / 3.0,
                    1.0 / 3.0,
                    1.0 / 3.0,
                ],
                [
                    1.0 / 3.0,
                    1.0 / 3.0,
                    1.0 / 3.0,
                ],
            ],
            dtype=np.float64,
        ),
        skinning_weights=np.array(
            [
                [1.0, 0.0],
                [1.0, 0.0],
                [1.0, 0.0],
            ],
            dtype=np.float64,
        ),
        kinematic_tree=np.array(
            [
                -1,
                0,
            ],
            dtype=np.int64,
        ),
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-pipeline-v1",
            "synthetic": True,
        },
    )


def _named_landmark_result() -> AtlasPortraitLandmarkResult:
    return AtlasPortraitLandmarkResult(
        image_width=1024,
        image_height=1024,
        landmarks={
            "left_eye_outer": (
                0.30,
                0.40,
            ),
            "right_eye_outer": (
                0.70,
                0.40,
            ),
            "nose_tip": (
                0.50,
                0.55,
            ),
        },
        confidence=1.0,
        provider_id="synthetic-named",
        metadata={
            "image_sha256": "synthetic-sha256",
            "synthetic": True,
            "view_type": "front",
        },
    )


def _indexed_landmark_result() -> (
    AtlasPortraitIndexedLandmarkResult
):
    return AtlasPortraitIndexedLandmarkResult(
        image_width=1024,
        image_height=1024,
        landmark_ids=(
            10,
            20,
            30,
        ),
        landmarks_3d=np.array(
            [
                [0.30, 0.40, 0.0],
                [0.50, 0.55, 0.0],
                [0.70, 0.40, 0.0],
            ],
            dtype=np.float64,
        ),
        confidence=1.0,
        provider_id="synthetic-indexed",
        metadata={
            "image_sha256": "synthetic-sha256",
            "synthetic": True,
            "view_type": "front",
        },
    )


def _camera(
    *,
    point_count: int,
    error: float,
) -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=2.5,
        translation_x=0.5,
        translation_y=0.5,
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
            point_count=3,
            error=0.0067,
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
            "landmark_count": 3,
            "model_family": "flame",
            "model_version": "synthetic-pipeline-v1",
            "synthetic": True,
        },
    )


def _identity_fit_result() -> (
    AtlasPortraitFlameIdentityFitResult
):
    return AtlasPortraitFlameIdentityFitResult(
        identity_parameters=np.array(
            [
                -0.72,
                -2.15,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            point_count=3,
            error=0.0042,
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
            "active_identity_count": 2,
            "fitting_stage": "dense_identity",
            "landmark_count": 3,
            "model_family": "flame",
            "model_version": "synthetic-pipeline-v1",
            "synthetic": True,
        },
    )


def _embedding():
    return (
        np.array(
            [
                10,
                20,
                30,
            ],
            dtype=np.int64,
        ),
        np.array(
            [
                0,
                0,
                0,
            ],
            dtype=np.int64,
        ),
        np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        ),
    )


def _run(
    monkeypatch,
    **overrides,
):
    root_result = _root_pose_result()
    identity_result = _identity_fit_result()
    calls: list[tuple[str, object, dict]] = []

    def fake_root_fit(
        cls,
        model,
        **kwargs,
    ):
        calls.append(
            (
                "root",
                model,
                kwargs,
            )
        )
        return root_result

    def fake_identity_fit(
        cls,
        model,
        **kwargs,
    ):
        calls.append(
            (
                "identity",
                model,
                kwargs,
            )
        )
        return identity_result

    monkeypatch.setattr(
        AtlasPortraitFlameRootPoseFitter,
        "fit",
        classmethod(
            fake_root_fit
        ),
    )
    monkeypatch.setattr(
        AtlasPortraitFlameIdentityFitter,
        "fit",
        classmethod(
            fake_identity_fit
        ),
    )

    (
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _embedding()

    arguments = {
        "model": _model(),
        "named_landmark_result": (
            _named_landmark_result()
        ),
        "indexed_landmark_result": (
            _indexed_landmark_result()
        ),
        "landmark_indices": landmark_indices,
        "landmark_face_indices": (
            landmark_face_indices
        ),
        "landmark_barycentric_coordinates": (
            landmark_barycentric_coordinates
        ),
        "root_landmark_weights": np.array(
            [
                1.0,
                2.0,
                1.0,
            ],
            dtype=np.float64,
        ),
        "identity_landmark_weights": np.array(
            [
                1.0,
                1.5,
                1.0,
            ],
            dtype=np.float64,
        ),
        "angle_limit_degrees": 25.0,
        "root_maximum_function_evaluations": 180,
        "active_identity_count": 2,
        "regularization_weight": 1.0e-5,
        "identity_parameter_limit": 3.0,
        "identity_maximum_function_evaluations": 220,
    }
    arguments.update(
        overrides
    )

    result = AtlasPortraitFlameDenseIdentityPipeline.fit(
        **arguments
    )

    return (
        result,
        calls,
        root_result,
        identity_result,
        arguments,
    )


def test_pipeline_returns_dense_identity_pipeline_result(
    monkeypatch,
):
    result, _, _, _, _ = _run(
        monkeypatch
    )

    assert isinstance(
        result,
        AtlasPortraitFlameDenseIdentityPipelineResult,
    )


def test_pipeline_runs_root_pose_before_identity(
    monkeypatch,
):
    _, calls, _, _, _ = _run(
        monkeypatch
    )

    assert [
        call[
            0
        ]
        for call in calls
    ] == [
        "root",
        "identity",
    ]


def test_pipeline_forwards_root_pose_configuration(
    monkeypatch,
):
    _, calls, _, _, arguments = _run(
        monkeypatch
    )

    root_kwargs = calls[
        0
    ][
        2
    ]

    assert root_kwargs[
        "landmark_result"
    ] is arguments[
        "named_landmark_result"
    ]
    assert root_kwargs[
        "angle_limit_degrees"
    ] == pytest.approx(
        25.0
    )
    assert root_kwargs[
        "maximum_function_evaluations"
    ] == 180
    np.testing.assert_allclose(
        root_kwargs[
            "landmark_weights"
        ],
        arguments[
            "root_landmark_weights"
        ],
    )


def test_pipeline_forwards_root_result_to_identity_fitter(
    monkeypatch,
):
    _, calls, root_result, _, arguments = _run(
        monkeypatch
    )

    identity_kwargs = calls[
        1
    ][
        2
    ]

    assert identity_kwargs[
        "landmark_result"
    ] is arguments[
        "indexed_landmark_result"
    ]

    np.testing.assert_allclose(
        identity_kwargs[
            "root_pose_parameters"
        ],
        root_result.root_pose_parameters,
    )

    assert tuple(
        identity_kwargs[
            "requested_mediapipe_ids"
        ]
    ) == (
        10,
        20,
        30,
    )


def test_pipeline_forwards_identity_configuration(
    monkeypatch,
):
    _, calls, _, _, arguments = _run(
        monkeypatch
    )

    identity_kwargs = calls[
        1
    ][
        2
    ]

    assert identity_kwargs[
        "active_identity_count"
    ] == 2
    assert identity_kwargs[
        "regularization_weight"
    ] == pytest.approx(
        1.0e-5
    )
    assert identity_kwargs[
        "identity_parameter_limit"
    ] == pytest.approx(
        3.0
    )
    assert identity_kwargs[
        "maximum_function_evaluations"
    ] == 220

    np.testing.assert_allclose(
        identity_kwargs[
            "landmark_weights"
        ],
        arguments[
            "identity_landmark_weights"
        ],
    )


def test_pipeline_preserves_embedding_order(
    monkeypatch,
):
    _, calls, _, _, arguments = _run(
        monkeypatch
    )

    for call in calls:
        kwargs = call[
            2
        ]

        np.testing.assert_array_equal(
            kwargs[
                "landmark_indices"
            ],
            arguments[
                "landmark_indices"
            ],
        )
        np.testing.assert_array_equal(
            kwargs[
                "landmark_face_indices"
            ],
            arguments[
                "landmark_face_indices"
            ],
        )
        np.testing.assert_allclose(
            kwargs[
                "landmark_barycentric_coordinates"
            ],
            arguments[
                "landmark_barycentric_coordinates"
            ],
        )


def test_pipeline_builds_deterministic_metadata(
    monkeypatch,
):
    result, _, _, _, _ = _run(
        monkeypatch
    )

    assert result.metadata == {
        "dense_landmark_count": 3,
        "model_family": "flame",
        "model_version": "synthetic-pipeline-v1",
        "pipeline": "flame_dense_identity",
        "root_landmark_count": 3,
        "synthetic": True,
    }


def test_pipeline_result_contains_stage_results(
    monkeypatch,
):
    (
        result,
        _,
        root_result,
        identity_result,
        _,
    ) = _run(
        monkeypatch
    )

    assert (
        result.root_pose_result.to_dict()
        == root_result.to_dict()
    )
    assert (
        result.identity_fit_result.to_dict()
        == identity_result.to_dict()
    )


def test_pipeline_does_not_modify_embedding_inputs(
    monkeypatch,
):
    (
        landmark_indices,
        landmark_face_indices,
        landmark_barycentric_coordinates,
    ) = _embedding()

    indices_before = landmark_indices.copy()
    faces_before = landmark_face_indices.copy()
    barycentric_before = (
        landmark_barycentric_coordinates.copy()
    )

    _run(
        monkeypatch,
        landmark_indices=landmark_indices,
        landmark_face_indices=landmark_face_indices,
        landmark_barycentric_coordinates=(
            landmark_barycentric_coordinates
        ),
    )

    np.testing.assert_array_equal(
        landmark_indices,
        indices_before,
    )
    np.testing.assert_array_equal(
        landmark_face_indices,
        faces_before,
    )
    np.testing.assert_allclose(
        landmark_barycentric_coordinates,
        barycentric_before,
    )


def test_pipeline_rejects_wrong_model_type(
    monkeypatch,
):
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        _run(
            monkeypatch,
            model=object(),
        )


def test_pipeline_rejects_wrong_named_landmark_result_type(
    monkeypatch,
):
    with pytest.raises(
        TypeError,
        match="AtlasPortraitLandmarkResult",
    ):
        _run(
            monkeypatch,
            named_landmark_result=object(),
        )


def test_pipeline_rejects_wrong_indexed_landmark_result_type(
    monkeypatch,
):
    with pytest.raises(
        TypeError,
        match="AtlasPortraitIndexedLandmarkResult",
    ):
        _run(
            monkeypatch,
            indexed_landmark_result=object(),
        )


@pytest.mark.parametrize(
    (
        "overrides",
        "match",
    ),
    [
        (
            {
                "angle_limit_degrees": 0.0,
            },
            "angle_limit_degrees",
        ),
        (
            {
                "angle_limit_degrees": math.nan,
            },
            "angle_limit_degrees",
        ),
        (
            {
                "root_maximum_function_evaluations": 0,
            },
            "root_maximum_function_evaluations",
        ),
        (
            {
                "active_identity_count": 0,
            },
            "active_identity_count",
        ),
        (
            {
                "regularization_weight": -1.0,
            },
            "regularization_weight",
        ),
        (
            {
                "identity_parameter_limit": 0.0,
            },
            "identity_parameter_limit",
        ),
        (
            {
                "identity_maximum_function_evaluations": 2.5,
            },
            "identity_maximum_function_evaluations",
        ),
        (
            {
                "landmark_indices": np.array(
                    [
                        10,
                        20,
                        20,
                    ],
                    dtype=np.int64,
                ),
            },
            "unique",
        ),
    ],
)
def test_pipeline_rejects_invalid_configuration(
    monkeypatch,
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
        _run(
            monkeypatch,
            **overrides
        )
