from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_shaded_preview_pipeline import (
    AtlasPortraitFlameShadedPreviewPipeline,
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


def _canonical_model() -> AtlasPortraitFlameCanonicalModel:
    return AtlasPortraitFlameCanonicalModel(
        template_vertices=np.array(
            [
                [1.0, 1.0, 1.0],
                [4.0, 1.0, 1.0],
                [1.0, 4.0, 1.0],
                [4.0, 4.0, 1.0],
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
        identity_shape_directions=np.zeros(
            (
                4,
                3,
                1,
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
            ],
            dtype=np.float64,
        ),
        skinning_weights=np.ones(
            (
                4,
                1,
            ),
            dtype=np.float64,
        ),
        kinematic_tree=np.array(
            [
                -1,
            ],
            dtype=np.int64,
        ),
        metadata={
            "model_family": "flame",
            "model_version": "synthetic-preview-v1",
            "synthetic": True,
        },
    )


def _skinned_vertices() -> np.ndarray:
    return np.array(
        [
            [1.0, 1.0, 1.0],
            [4.0, 1.0, 1.0],
            [1.0, 4.0, 1.0],
            [4.0, 4.0, 1.0],
        ],
        dtype=np.float64,
    )


def _camera() -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=1.0,
        translation_x=0.0,
        translation_y=0.0,
        projected_points_2d=np.array(
            [
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.0,
        metadata={
            "camera_model": "weak_perspective",
            "synthetic": True,
        },
    )


def _run_pipeline(
    **overrides,
) -> AtlasPortraitFlameShadedPreviewPipelineResult:
    arguments = {
        "model": _canonical_model(),
        "skinned_vertices": _skinned_vertices(),
        "camera": _camera(),
        "image_width": 6,
        "image_height": 6,
        "light_direction": (
            0.0,
            0.0,
            1.0,
        ),
        "ambient_strength": 0.20,
        "diffuse_strength": 0.80,
        "background_intensity": 0.10,
    }
    arguments.update(
        overrides,
    )

    return AtlasPortraitFlameShadedPreviewPipeline.run(
        **arguments,
    )


def test_pipeline_returns_pipeline_result_contract():
    result = _run_pipeline()

    assert isinstance(
        result,
        AtlasPortraitFlameShadedPreviewPipelineResult,
    )


def test_pipeline_exposes_all_intermediate_contracts():
    result = _run_pipeline()

    assert isinstance(
        result.mesh,
        AtlasPortraitFlameDeformedMesh,
    )
    assert isinstance(
        result.normal_field,
        AtlasPortraitFlameNormalField,
    )
    assert isinstance(
        result.projection,
        AtlasPortraitFlameWeakPerspectiveProjection,
    )
    assert isinstance(
        result.visibility,
        AtlasPortraitFlameTriangleVisibility,
    )
    assert isinstance(
        result.rasterization,
        AtlasPortraitFlameTriangleRasterization,
    )
    assert isinstance(
        result.preview,
        AtlasPortraitFlameShadedPreviewResult,
    )


def test_pipeline_preserves_expected_mesh_counts():
    result = _run_pipeline()

    assert result.vertex_count == 4
    assert result.face_count == 2
    assert result.visible_triangle_count == 2


def test_pipeline_preserves_image_dimensions():
    result = _run_pipeline(
        image_width=7,
        image_height=8,
    )

    assert result.image_width == 7
    assert result.image_height == 8
    assert result.preview.shape == (
        8,
        7,
    )
    assert result.rasterization.image_width == 7
    assert result.rasterization.image_height == 8


def test_pipeline_projects_vertices_with_camera():
    result = _run_pipeline()

    assert np.array_equal(
        result.projection.projected_vertices_2d,
        np.array(
            [
                [1.0, 1.0],
                [4.0, 1.0],
                [1.0, 4.0],
                [4.0, 4.0],
            ],
            dtype=np.float64,
        ),
    )


def test_pipeline_rasterizes_expected_square_region():
    result = _run_pipeline()

    expected_coverage = np.zeros(
        (
            6,
            6,
        ),
        dtype=np.bool_,
    )
    expected_coverage[
        1:5,
        1:5,
    ] = True

    assert np.array_equal(
        result.rasterization.coverage_mask,
        expected_coverage,
    )
    assert result.covered_pixel_count == 16
    assert result.background_pixel_count == 20


def test_pipeline_renders_expected_foreground_and_background():
    result = _run_pipeline()

    assert np.allclose(
        result.preview.shading[
            result.preview.coverage_mask
        ],
        1.0,
        rtol=0.0,
        atol=1.0e-12,
    )
    assert np.allclose(
        result.preview.shading[
            ~result.preview.coverage_mask
        ],
        0.10,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_pipeline_preserves_render_settings():
    result = _run_pipeline(
        light_direction=(
            0.0,
            0.0,
            2.0,
        ),
        ambient_strength=0.30,
        diffuse_strength=0.60,
        background_intensity=0.15,
    )

    assert result.preview.light_direction == pytest.approx(
        (
            0.0,
            0.0,
            1.0,
        )
    )
    assert result.preview.ambient_strength == pytest.approx(
        0.30,
    )
    assert result.preview.diffuse_strength == pytest.approx(
        0.60,
    )
    assert result.preview.background_intensity == pytest.approx(
        0.15,
    )


def test_pipeline_is_deterministic():
    first = _run_pipeline()
    second = _run_pipeline()

    assert np.array_equal(
        first.mesh.vertices,
        second.mesh.vertices,
    )
    assert np.array_equal(
        first.normal_field.face_normals,
        second.normal_field.face_normals,
    )
    assert np.array_equal(
        first.projection.projected_vertices_2d,
        second.projection.projected_vertices_2d,
    )
    assert np.array_equal(
        first.visibility.visible_triangle_mask,
        second.visibility.visible_triangle_mask,
    )
    assert np.array_equal(
        first.rasterization.triangle_index_buffer,
        second.rasterization.triangle_index_buffer,
    )
    assert np.array_equal(
        first.preview.preview,
        second.preview.preview,
    )


def test_pipeline_does_not_modify_inputs():
    model = _canonical_model()
    skinned_vertices = _skinned_vertices()
    camera = _camera()

    model_before = model.to_dict()
    vertices_before = skinned_vertices.copy()
    camera_before = camera.to_dict()

    _run_pipeline(
        model=model,
        skinned_vertices=skinned_vertices,
        camera=camera,
    )

    assert model.to_dict() == model_before
    assert np.array_equal(
        skinned_vertices,
        vertices_before,
    )
    assert camera.to_dict() == camera_before


def test_pipeline_result_to_dict_returns_nested_plain_values():
    result = _run_pipeline()

    payload = result.to_dict()

    assert set(
        payload,
    ) == {
        "vertex_count",
        "face_count",
        "visible_triangle_count",
        "image_width",
        "image_height",
        "covered_pixel_count",
        "background_pixel_count",
        "mesh",
        "normal_field",
        "projection",
        "visibility",
        "rasterization",
        "preview",
    }

    assert payload["vertex_count"] == 4
    assert payload["face_count"] == 2
    assert payload["visible_triangle_count"] == 2
    assert payload["image_width"] == 6
    assert payload["image_height"] == 6
    assert payload["covered_pixel_count"] == 16
    assert payload["background_pixel_count"] == 20

    assert payload["mesh"]["vertex_count"] == 4
    assert payload["normal_field"]["face_count"] == 2
    assert payload["projection"]["face_count"] == 2
    assert payload["visibility"]["triangle_count"] == 2
    assert payload["rasterization"]["image_width"] == 6
    assert payload["preview"]["image_width"] == 6


def test_pipeline_rejects_wrong_model_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameCanonicalModel",
    ):
        _run_pipeline(
            model=object(),
        )


def test_pipeline_rejects_wrong_camera_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitWeakPerspectiveCamera",
    ):
        _run_pipeline(
            camera=object(),
        )


@pytest.mark.parametrize(
    "invalid_vertices",
    [
        np.zeros(
            (
                4,
                2,
            ),
            dtype=np.float64,
        ),
        np.zeros(
            (
                3,
                3,
            ),
            dtype=np.float64,
        ),
        np.full(
            (
                4,
                3,
            ),
            np.nan,
            dtype=np.float64,
        ),
    ],
)
def test_pipeline_rejects_invalid_skinned_vertices(
    invalid_vertices,
):
    with pytest.raises(
        ValueError,
        match="skinned_vertices",
    ):
        _run_pipeline(
            skinned_vertices=invalid_vertices,
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
            6.5,
        ),
        (
            "image_height",
            -1,
        ),
        (
            "image_height",
            None,
        ),
    ],
)
def test_pipeline_rejects_invalid_image_dimensions(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _run_pipeline(
            **{
                field_name: value,
            },
        )
