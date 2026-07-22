from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
)
from CORE.atlas_portrait_flame_fitted_shaded_preview_pipeline import (
    AtlasPortraitFlameFittedShadedPreviewPipeline,
)
from CORE.atlas_portrait_flame_fitted_shaded_preview_pipeline_result import (
    AtlasPortraitFlameFittedShadedPreviewPipelineResult,
)
from CORE.atlas_portrait_flame_identity_fit_result import (
    AtlasPortraitFlameIdentityFitResult,
)
from CORE.atlas_portrait_flame_root_pose_fit_result import (
    AtlasPortraitFlameRootPoseFitResult,
)
from CORE.atlas_portrait_flame_shaded_preview_pipeline import (
    AtlasPortraitFlameShadedPreviewPipelineResult,
)
from CORE.atlas_portrait_flame_shaded_preview_result import (
    AtlasPortraitFlameShadedPreviewResult,
)
from CORE.atlas_portrait_flame_triangle_rasterizer import (
    AtlasPortraitFlameTriangleRasterization,
)
from CORE.atlas_portrait_flame_triangle_visibility_evaluator import (
    AtlasPortraitFlameTriangleVisibility,
)
from CORE.atlas_portrait_flame_vertex_normal_evaluator import (
    AtlasPortraitFlameNormalField,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _model() -> AtlasPortraitFlameCanonicalModel:
    return AtlasPortraitFlameCanonicalModel(
        template_vertices=np.array(
            [
                [-0.50, 0.40, 0.10],
                [0.50, 0.40, 0.10],
                [-0.50, -0.40, 0.10],
                [0.50, -0.40, 0.10],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 2, 1],
                [1, 2, 3],
            ],
            dtype=np.int64,
        ),
        identity_shape_directions=np.zeros(
            (
                4,
                3,
                2,
            ),
            dtype=np.float64,
        ),
        expression_shape_directions=np.zeros(
            (
                4,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        pose_directions=np.zeros(
            (
                4,
                3,
                9,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=6,
        joint_regressor=np.array(
            [
                [0.25, 0.25, 0.25, 0.25],
                [0.50, 0.50, 0.00, 0.00],
            ],
            dtype=np.float64,
        ),
        skinning_weights=np.array(
            [
                [1.0, 0.0],
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
            "model_version": "synthetic-fitted-preview-v1",
            "synthetic": True,
        },
    )


def _camera(
    *,
    coordinate_space: str,
    scale: float,
) -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=scale,
        translation_x=0.5,
        translation_y=0.5,
        projected_points_2d=np.array(
            [
                [0.25, 0.25],
                [0.75, 0.25],
                [0.25, 0.75],
                [0.75, 0.75],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.01,
        metadata={
            "camera_model": "weak_perspective",
            "coordinate_space": coordinate_space,
            "synthetic": True,
        },
    )


def _fitting_result(
) -> AtlasPortraitFlameDenseIdentityPipelineResult:
    root_result = AtlasPortraitFlameRootPoseFitResult(
        root_pose_parameters=np.array(
            [
                -0.10,
                0.04,
                0.02,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            coordinate_space="normalized",
            scale=2.0,
        ),
        initial_weighted_root_mean_square_error=0.012,
        final_weighted_root_mean_square_error=0.008,
        function_evaluation_count=10,
        optimizer_success=True,
        optimizer_status=2,
        optimizer_message="Root fit complete.",
        metadata={
            "fitting_stage": "root_pose",
            "synthetic": True,
        },
    )

    identity_result = AtlasPortraitFlameIdentityFitResult(
        identity_parameters=np.array(
            [
                0.30,
                -0.20,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            coordinate_space="normalized",
            scale=2.1,
        ),
        initial_weighted_root_mean_square_error=0.008,
        final_weighted_root_mean_square_error=0.005,
        regularization_weight=1.0e-5,
        function_evaluation_count=8,
        optimizer_success=True,
        optimizer_status=2,
        optimizer_message="Identity fit complete.",
        metadata={
            "active_identity_count": 2,
            "fitting_stage": "dense_identity",
            "synthetic": True,
        },
    )

    return AtlasPortraitFlameDenseIdentityPipelineResult(
        root_pose_result=root_result,
        identity_fit_result=identity_result,
        metadata={
            "pipeline": "flame_dense_identity",
            "synthetic": True,
        },
    )


def _fitted_mesh() -> AtlasPortraitFlameDeformedMesh:
    return AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
            [
                [-0.55, -0.42, 0.10],
                [0.52, -0.39, 0.12],
                [-0.48, 0.43, 0.08],
                [0.50, 0.40, 0.09],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
                [1, 3, 2],
            ],
            dtype=np.int64,
        ),
    )


def _pixel_camera() -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=210.0,
        translation_x=50.0,
        translation_y=50.0,
        projected_points_2d=np.array(
            [
                [25.0, 25.0],
                [75.0, 25.0],
                [25.0, 75.0],
                [75.0, 75.0],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=1.0,
        metadata={
            "camera_model": "weak_perspective",
            "coordinate_space": "pixel",
            "image_height": 100,
            "image_width": 100,
            "pixel_scale": 99.0,
            "source_coordinate_space": "normalized",
            "synthetic": True,
        },
    )


def _shaded_result(
    mesh: AtlasPortraitFlameDeformedMesh,
) -> AtlasPortraitFlameShadedPreviewPipelineResult:
    coverage_mask = np.array(
        [
            [False, False],
            [True, True],
        ],
        dtype=np.bool_,
    )

    rasterization = AtlasPortraitFlameTriangleRasterization(
        image_width=2,
        image_height=2,
        coverage_mask=coverage_mask,
        triangle_index_buffer=np.array(
            [
                [-1, -1],
                [0, 1],
            ],
            dtype=np.int64,
        ),
        depth_buffer=np.array(
            [
                [np.inf, np.inf],
                [0.10, 0.09],
            ],
            dtype=np.float64,
        ),
        barycentric_coordinates=np.array(
            [
                [
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ],
                [
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float64,
        ),
    )

    return AtlasPortraitFlameShadedPreviewPipelineResult(
        mesh=mesh,
        normal_field=AtlasPortraitFlameNormalField(
            face_normals=np.array(
                [
                    [0.0, 0.0, 1.0],
                    [0.0, 0.0, 1.0],
                ],
                dtype=np.float64,
            ),
            vertex_normals=np.array(
                [
                    [0.0, 0.0, 1.0],
                    [0.0, 0.0, 1.0],
                    [0.0, 0.0, 1.0],
                    [0.0, 0.0, 1.0],
                ],
                dtype=np.float64,
            ),
        ),
        projection=AtlasPortraitFlameWeakPerspectiveProjection(
            scale=1.0,
            translation_x=0.0,
            translation_y=0.0,
            projected_vertices_2d=np.array(
                [
                    [0.0, 0.0],
                    [1.0, 0.0],
                    [0.0, 1.0],
                    [1.0, 1.0],
                ],
                dtype=np.float64,
            ),
            triangle_faces=mesh.triangle_faces,
        ),
        visibility=AtlasPortraitFlameTriangleVisibility(
            visible_triangle_mask=np.array(
                [
                    True,
                    True,
                ],
                dtype=np.bool_,
            ),
            front_facing_triangle_mask=np.array(
                [
                    True,
                    True,
                ],
                dtype=np.bool_,
            ),
            signed_projected_areas=np.array(
                [
                    1.0,
                    1.0,
                ],
                dtype=np.float64,
            ),
            mean_triangle_depths=np.array(
                [
                    0.10,
                    0.09,
                ],
                dtype=np.float64,
            ),
        ),
        rasterization=rasterization,
        preview=AtlasPortraitFlameShadedPreviewResult(
            shading=np.array(
                [
                    [0.06, 0.06],
                    [0.80, 0.90],
                ],
                dtype=np.float64,
            ),
            preview=np.array(
                [
                    [15, 15],
                    [204, 230],
                ],
                dtype=np.uint8,
            ),
            coverage_mask=coverage_mask,
            light_direction=(
                0.0,
                0.0,
                1.0,
            ),
            ambient_strength=0.20,
            diffuse_strength=0.80,
            background_intensity=0.06,
        ),
    )


def _run(
    monkeypatch,
    **overrides,
):
    model = overrides.pop(
        "model",
        _model(),
    )
    fitting_result = overrides.pop(
        "fitting_result",
        _fitting_result(),
    )
    fitted_mesh = _fitted_mesh()
    pixel_camera = _pixel_camera()
    shaded_result = _shaded_result(
        fitted_mesh
    )

    calls = []

    def fake_build(
        received_model,
        *,
        pipeline_result,
    ):
        calls.append(
            (
                "mesh",
                received_model,
                pipeline_result,
            )
        )
        return fitted_mesh

    def fake_adapt(
        camera,
        *,
        image_width,
        image_height,
    ):
        calls.append(
            (
                "camera",
                camera,
                image_width,
                image_height,
            )
        )
        return pixel_camera

    def fake_preview_run(
        preview_model,
        *,
        skinned_vertices,
        camera,
        image_width,
        image_height,
        light_direction,
        ambient_strength,
        diffuse_strength,
        background_intensity,
    ):
        calls.append(
            (
                "preview",
                preview_model,
                skinned_vertices,
                camera,
                image_width,
                image_height,
                light_direction,
                ambient_strength,
                diffuse_strength,
                background_intensity,
            )
        )
        return shaded_result

    monkeypatch.setattr(
        "CORE.atlas_portrait_flame_fitted_shaded_preview_pipeline."
        "AtlasPortraitFlameFittedMeshBuilder.build",
        fake_build,
    )
    monkeypatch.setattr(
        "CORE.atlas_portrait_flame_fitted_shaded_preview_pipeline."
        "AtlasPortraitFlamePixelCameraAdapter.adapt",
        fake_adapt,
    )
    monkeypatch.setattr(
        "CORE.atlas_portrait_flame_fitted_shaded_preview_pipeline."
        "AtlasPortraitFlameShadedPreviewPipeline.run",
        fake_preview_run,
    )

    arguments = {
        "model": model,
        "fitting_result": fitting_result,
        "image_width": 100,
        "image_height": 100,
        "light_direction": (
            0.35,
            -0.45,
            0.82,
        ),
        "ambient_strength": 0.24,
        "diffuse_strength": 0.76,
        "background_intensity": 0.06,
    }
    arguments.update(
        overrides,
    )

    result = (
        AtlasPortraitFlameFittedShadedPreviewPipeline.run(
            **arguments,
        )
    )

    return (
        result,
        calls,
        model,
        fitting_result,
        fitted_mesh,
        pixel_camera,
        shaded_result,
    )


def test_pipeline_returns_aggregate_result(
    monkeypatch,
):
    result, *_ = _run(
        monkeypatch
    )

    assert isinstance(
        result,
        AtlasPortraitFlameFittedShadedPreviewPipelineResult,
    )


def test_pipeline_calls_components_in_order(
    monkeypatch,
):
    _, calls, *_ = _run(
        monkeypatch
    )

    assert [
        call[
            0
        ]
        for call in calls
    ] == [
        "mesh",
        "camera",
        "preview",
    ]


def test_pipeline_forwards_model_and_fitting_result(
    monkeypatch,
):
    (
        _,
        calls,
        model,
        fitting_result,
        *_
    ) = _run(
        monkeypatch
    )

    assert calls[
        0
    ][
        1
    ] is model
    assert calls[
        0
    ][
        2
    ] is fitting_result


def test_pipeline_adapts_final_fitted_camera(
    monkeypatch,
):
    (
        _,
        calls,
        _,
        fitting_result,
        *_
    ) = _run(
        monkeypatch
    )

    camera_call = calls[
        1
    ]

    assert camera_call[
        1
    ].to_dict() == (
        fitting_result.final_camera.to_dict()
    )
    assert camera_call[
        2:
    ] == (
        100,
        100,
    )


def test_pipeline_uses_fitted_triangle_topology(
    monkeypatch,
):
    (
        _,
        calls,
        model,
        _,
        fitted_mesh,
        *_
    ) = _run(
        monkeypatch
    )

    preview_model = calls[
        2
    ][
        1
    ]

    np.testing.assert_array_equal(
        preview_model.triangle_faces,
        fitted_mesh.triangle_faces,
    )
    assert not np.array_equal(
        preview_model.triangle_faces,
        model.triangle_faces,
    )


def test_pipeline_uses_fitted_vertices_and_pixel_camera(
    monkeypatch,
):
    (
        _,
        calls,
        _,
        _,
        fitted_mesh,
        pixel_camera,
        *_
    ) = _run(
        monkeypatch
    )

    preview_call = calls[
        2
    ]

    assert preview_call[
        2
    ] is fitted_mesh.vertices
    assert preview_call[
        3
    ] is pixel_camera


def test_pipeline_forwards_preview_configuration(
    monkeypatch,
):
    _, calls, *_ = _run(
        monkeypatch,
        image_width=640,
        image_height=480,
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.30,
        diffuse_strength=0.65,
        background_intensity=0.10,
    )

    preview_call = calls[
        2
    ]

    assert preview_call[
        4:
    ] == (
        640,
        480,
        (
            0.0,
            0.0,
            1.0,
        ),
        0.30,
        0.65,
        0.10,
    )


def test_pipeline_returns_component_results(
    monkeypatch,
):
    (
        result,
        _,
        _,
        fitting_result,
        fitted_mesh,
        pixel_camera,
        shaded_result,
    ) = _run(
        monkeypatch
    )

    assert result.fitting_result.to_dict() == (
        fitting_result.to_dict()
    )
    assert result.fitted_mesh is fitted_mesh
    assert result.pixel_camera is pixel_camera
    assert result.shaded_preview_result is shaded_result


def test_pipeline_generates_expected_metadata(
    monkeypatch,
):
    result, *_ = _run(
        monkeypatch
    )

    assert result.metadata == {
        "coordinate_space": "pixel",
        "image_height": 100,
        "image_width": 100,
        "model_family": "flame",
        "model_version": "synthetic-fitted-preview-v1",
        "pipeline": "flame_fitted_shaded_preview",
        "synthetic": True,
    }


def test_pipeline_does_not_modify_inputs(
    monkeypatch,
):
    model = _model()
    fitting_result = _fitting_result()

    model_before = model.to_dict()
    fitting_before = fitting_result.to_dict()

    _run(
        monkeypatch,
        model=model,
        fitting_result=fitting_result,
    )

    assert model.to_dict() == model_before
    assert fitting_result.to_dict() == fitting_before


def test_pipeline_is_deterministic(
    monkeypatch,
):
    first, *_ = _run(
        monkeypatch
    )
    second, *_ = _run(
        monkeypatch
    )

    assert first.to_dict() == second.to_dict()


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


def test_pipeline_rejects_wrong_fitting_result_type(
    monkeypatch,
):
    with pytest.raises(
        TypeError,
        match=(
            "AtlasPortraitFlameDenseIdentityPipelineResult"
        ),
    ):
        _run(
            monkeypatch,
            fitting_result=object(),
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
    ),
    [
        (
            "image_width",
            0,
        ),
        (
            "image_width",
            100.5,
        ),
        (
            "image_height",
            1,
        ),
        (
            "image_height",
            None,
        ),
    ],
)
def test_pipeline_rejects_invalid_image_dimensions(
    monkeypatch,
    field_name,
    value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field_name,
    ):
        _run(
            monkeypatch,
            **{
                field_name: value,
            },
        )
