from __future__ import annotations

from types import MappingProxyType

import numpy as np
import pytest

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_dense_identity_pipeline_result import (
    AtlasPortraitFlameDenseIdentityPipelineResult,
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
    AtlasPortraitFlameShadedPreviewPipeline,
    AtlasPortraitFlameShadedPreviewPipelineResult,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)
from Test.fixtures.portrait.portrait_flame_synthetic_face_fixture import (
    build_synthetic_flame_face_fixture,
)


def _camera(
    *,
    scale: float = 1.0,
    coordinate_space: str = "pixel",
    error: float = 0.0,
) -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=scale,
        translation_x=0.0,
        translation_y=0.0,
        projected_points_2d=np.array(
            [
                [1.0, 1.0],
                [2.0, 2.0],
                [3.0, 3.0],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=error,
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
                0.05,
                0.02,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            scale=2.0,
            coordinate_space="normalized",
            error=0.008,
        ),
        initial_weighted_root_mean_square_error=0.012,
        final_weighted_root_mean_square_error=0.008,
        function_evaluation_count=11,
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
                0.25,
                -0.15,
            ],
            dtype=np.float64,
        ),
        camera=_camera(
            scale=2.1,
            coordinate_space="normalized",
            error=0.005,
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


def _shaded_result(
) -> AtlasPortraitFlameShadedPreviewPipelineResult:
    fixture = build_synthetic_flame_face_fixture()

    return AtlasPortraitFlameShadedPreviewPipeline.run(
        fixture.model,
        skinned_vertices=fixture.skinned_vertices,
        camera=fixture.camera,
        image_width=fixture.image_width,
        image_height=fixture.image_height,
        light_direction=(
            0.35,
            -0.45,
            0.82,
        ),
        ambient_strength=0.24,
        diffuse_strength=0.76,
        background_intensity=0.06,
    )


def _result(
    **overrides,
) -> AtlasPortraitFlameFittedShadedPreviewPipelineResult:
    shaded_result = _shaded_result()

    values = {
        "fitting_result": _fitting_result(),
        "fitted_mesh": shaded_result.mesh,
        "pixel_camera": _camera(
            scale=2048.0,
            coordinate_space="pixel",
            error=4.0,
        ),
        "shaded_preview_result": shaded_result,
        "metadata": {
            "model_family": "flame",
            "pipeline": "flame_fitted_shaded_preview",
            "synthetic": True,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitFlameFittedShadedPreviewPipelineResult(
        **values,
    )


def test_result_preserves_expected_contract_types():
    result = _result()

    assert isinstance(
        result.fitting_result,
        AtlasPortraitFlameDenseIdentityPipelineResult,
    )
    assert isinstance(
        result.fitted_mesh,
        AtlasPortraitFlameDeformedMesh,
    )
    assert isinstance(
        result.pixel_camera,
        AtlasPortraitWeakPerspectiveCamera,
    )
    assert isinstance(
        result.shaded_preview_result,
        AtlasPortraitFlameShadedPreviewPipelineResult,
    )


def test_result_reports_mesh_counts():
    result = _result()

    assert result.vertex_count == (
        result.fitted_mesh.vertex_count
    )
    assert result.face_count == (
        result.fitted_mesh.face_count
    )


def test_result_reports_preview_counts():
    result = _result()

    assert result.visible_triangle_count == (
        result.shaded_preview_result
        .visible_triangle_count
    )
    assert result.covered_pixel_count == (
        result.shaded_preview_result
        .covered_pixel_count
    )
    assert result.background_pixel_count == (
        result.shaded_preview_result
        .background_pixel_count
    )


def test_result_reports_image_dimensions():
    result = _result()

    assert result.image_width == (
        result.shaded_preview_result.image_width
    )
    assert result.image_height == (
        result.shaded_preview_result.image_height
    )


def test_result_reports_optimizer_success():
    result = _result()

    assert result.optimizer_success is True


def test_result_requires_pixel_camera_metadata():
    with pytest.raises(
        ValueError,
        match="coordinate_space",
    ):
        _result(
            pixel_camera=_camera(
                coordinate_space="normalized",
            ),
        )


def test_result_requires_preview_mesh_vertices_to_match():
    shaded_result = _shaded_result()

    changed_vertices = (
        shaded_result.mesh.vertices.copy()
    )
    changed_vertices[
        0,
        0,
    ] += 0.01

    incompatible_mesh = AtlasPortraitFlameDeformedMesh(
        vertices=changed_vertices,
        triangle_faces=(
            shaded_result.mesh.triangle_faces
        ),
    )

    with pytest.raises(
        ValueError,
        match="vertices",
    ):
        _result(
            fitted_mesh=incompatible_mesh,
            shaded_preview_result=shaded_result,
        )


def test_result_requires_preview_mesh_topology_to_match():
    shaded_result = _shaded_result()

    reversed_faces = (
        shaded_result.mesh.triangle_faces[
            :,
            [
                0,
                2,
                1,
            ],
        ]
    )

    incompatible_mesh = AtlasPortraitFlameDeformedMesh(
        vertices=shaded_result.mesh.vertices,
        triangle_faces=reversed_faces,
    )

    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        _result(
            fitted_mesh=incompatible_mesh,
            shaded_preview_result=shaded_result,
        )


def test_result_metadata_is_immutable_and_sorted():
    result = _result()

    assert isinstance(
        result.metadata,
        MappingProxyType,
    )
    assert tuple(
        result.metadata,
    ) == tuple(
        sorted(
            result.metadata,
        )
    )

    with pytest.raises(
        TypeError,
    ):
        result.metadata[
            "pipeline"
        ] = "changed"


def test_result_to_dict_returns_plain_values():
    result = _result()

    payload = result.to_dict()

    assert set(
        payload,
    ) == {
        "background_pixel_count",
        "covered_pixel_count",
        "face_count",
        "fitted_mesh",
        "fitting_result",
        "image_height",
        "image_width",
        "metadata",
        "optimizer_success",
        "pixel_camera",
        "shaded_preview_result",
        "vertex_count",
        "visible_triangle_count",
    }

    assert payload[
        "vertex_count"
    ] == result.vertex_count
    assert payload[
        "face_count"
    ] == result.face_count
    assert payload[
        "pixel_camera"
    ][
        "metadata"
    ][
        "coordinate_space"
    ] == "pixel"
    assert payload[
        "metadata"
    ][
        "pipeline"
    ] == "flame_fitted_shaded_preview"


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "expected_name",
    ),
    [
        (
            "fitting_result",
            object(),
            "AtlasPortraitFlameDenseIdentityPipelineResult",
        ),
        (
            "fitted_mesh",
            object(),
            "AtlasPortraitFlameDeformedMesh",
        ),
        (
            "pixel_camera",
            object(),
            "AtlasPortraitWeakPerspectiveCamera",
        ),
        (
            "shaded_preview_result",
            object(),
            "AtlasPortraitFlameShadedPreviewPipelineResult",
        ),
    ],
)
def test_result_rejects_wrong_nested_contract_type(
    field_name,
    invalid_value,
    expected_name,
):
    with pytest.raises(
        TypeError,
        match=expected_name,
    ):
        _result(
            **{
                field_name: invalid_value,
            }
        )


def test_result_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _result(
            metadata=[
                "invalid",
            ],
        )
