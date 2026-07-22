from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_deformed_mesh_evaluator import (
    AtlasPortraitFlameDeformedMesh,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
    AtlasPortraitFlameWeakPerspectiveProjectionEvaluator,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


def _mesh() -> AtlasPortraitFlameDeformedMesh:
    return AtlasPortraitFlameDeformedMesh(
        vertices=np.array(
            [
                [-1.0, 2.0, -3.0],
                [0.5, -1.0, 4.0],
                [2.0, 0.25, 7.5],
                [-0.25, -2.0, -9.0],
            ],
            dtype=np.float64,
        ),
        triangle_faces=np.array(
            [
                [0, 1, 2],
                [0, 2, 3],
            ],
            dtype=np.int64,
        ),
    )


def _camera() -> AtlasPortraitWeakPerspectiveCamera:
    return AtlasPortraitWeakPerspectiveCamera(
        scale=2.5,
        translation_x=0.75,
        translation_y=-0.50,
        projected_points_2d=np.array(
            [
                [0.0, 0.0],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.0,
        metadata={
            "camera_model": "weak_perspective",
            "initialization_method": (
                "weighted_similarity_no_rotation"
            ),
            "synthetic": True,
        },
    )


def test_evaluator_returns_projection_contract():
    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=_camera(),
        )
    )

    assert isinstance(
        result,
        AtlasPortraitFlameWeakPerspectiveProjection,
    )


def test_evaluator_projects_vertices_with_camera_scale_and_translation():
    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=_camera(),
        )
    )

    expected = np.array(
        [
            [-1.75, 4.50],
            [2.00, -3.00],
            [5.75, 0.125],
            [0.125, -5.50],
        ],
        dtype=np.float64,
    )

    assert np.allclose(
        result.projected_vertices_2d,
        expected,
        rtol=0.0,
        atol=1.0e-12,
    )


def test_evaluator_ignores_vertex_depth_for_projection():
    first_mesh = _mesh()

    second_vertices = first_mesh.vertices.copy()
    second_vertices[
        :,
        2,
    ] = np.array(
        [
            100.0,
            -200.0,
            300.0,
            -400.0,
        ],
        dtype=np.float64,
    )

    second_mesh = AtlasPortraitFlameDeformedMesh(
        vertices=second_vertices,
        triangle_faces=first_mesh.triangle_faces,
    )

    first = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            first_mesh,
            camera=_camera(),
        )
    )
    second = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            second_mesh,
            camera=_camera(),
        )
    )

    assert np.array_equal(
        first.projected_vertices_2d,
        second.projected_vertices_2d,
    )


def test_projection_preserves_mesh_triangle_faces():
    mesh = _mesh()

    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            mesh,
            camera=_camera(),
        )
    )

    assert np.array_equal(
        result.triangle_faces,
        mesh.triangle_faces,
    )
    assert not np.shares_memory(
        result.triangle_faces,
        mesh.triangle_faces,
    )


def test_projection_reports_vertex_and_face_counts():
    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=_camera(),
        )
    )

    assert result.vertex_count == 4
    assert result.face_count == 2


def test_projection_preserves_camera_parameters():
    camera = _camera()

    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=camera,
        )
    )

    assert result.scale == pytest.approx(
        camera.scale,
    )
    assert result.translation_x == pytest.approx(
        camera.translation_x,
    )
    assert result.translation_y == pytest.approx(
        camera.translation_y,
    )


def test_projection_arrays_use_expected_dtypes():
    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=_camera(),
        )
    )

    assert (
        result.projected_vertices_2d.dtype
        == np.float64
    )
    assert result.triangle_faces.dtype == np.int64


def test_projection_arrays_are_read_only():
    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=_camera(),
        )
    )

    assert (
        result.projected_vertices_2d.flags.writeable
        is False
    )
    assert result.triangle_faces.flags.writeable is False

    with pytest.raises(
        ValueError,
    ):
        result.projected_vertices_2d[
            0,
            0,
        ] = 1.0

    with pytest.raises(
        ValueError,
    ):
        result.triangle_faces[
            0,
            0,
        ] = 1


def test_evaluator_returns_independent_results():
    mesh = _mesh()
    camera = _camera()

    first = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            mesh,
            camera=camera,
        )
    )
    second = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            mesh,
            camera=camera,
        )
    )

    assert first is not second
    assert not np.shares_memory(
        first.projected_vertices_2d,
        second.projected_vertices_2d,
    )
    assert not np.shares_memory(
        first.triangle_faces,
        second.triangle_faces,
    )


def test_evaluator_does_not_modify_mesh_or_camera():
    mesh = _mesh()
    camera = _camera()

    vertices_before = mesh.vertices.copy()
    faces_before = mesh.triangle_faces.copy()
    camera_before = camera.to_dict()

    (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            mesh,
            camera=camera,
        )
    )

    assert np.array_equal(
        mesh.vertices,
        vertices_before,
    )
    assert np.array_equal(
        mesh.triangle_faces,
        faces_before,
    )
    assert camera.to_dict() == camera_before


def test_projection_to_dict_returns_plain_independent_values():
    result = (
        AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
        .evaluate(
            _mesh(),
            camera=_camera(),
        )
    )

    payload = result.to_dict()

    assert set(
        payload,
    ) == {
        "scale",
        "translation_x",
        "translation_y",
        "projected_vertices_2d",
        "triangle_faces",
        "vertex_count",
        "face_count",
    }
    assert payload["scale"] == pytest.approx(
        2.5,
    )
    assert payload["translation_x"] == pytest.approx(
        0.75,
    )
    assert payload["translation_y"] == pytest.approx(
        -0.50,
    )
    assert payload["projected_vertices_2d"] == (
        result.projected_vertices_2d.tolist()
    )
    assert payload["triangle_faces"] == (
        result.triangle_faces.tolist()
    )
    assert payload["vertex_count"] == 4
    assert payload["face_count"] == 2


def test_evaluator_rejects_wrong_mesh_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitFlameDeformedMesh",
    ):
        (
            AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
            .evaluate(
                object(),
                camera=_camera(),
            )
        )


def test_evaluator_rejects_wrong_camera_type():
    with pytest.raises(
        TypeError,
        match="AtlasPortraitWeakPerspectiveCamera",
    ):
        (
            AtlasPortraitFlameWeakPerspectiveProjectionEvaluator
            .evaluate(
                _mesh(),
                camera=object(),
            )
        )
