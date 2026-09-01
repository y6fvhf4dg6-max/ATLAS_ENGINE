import numpy as np
import pytest

from CORE.atlas_portrait_flame_identity_geometry_evaluator import (
    AtlasPortraitFlameIdentityGeometryEvaluator,
)


def _fixture():
    template = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float64,
    )

    faces = np.array(
        [[0, 1, 2]],
        dtype=np.int64,
    )

    shapedirs = np.zeros(
        (3, 3, 2),
        dtype=np.float64,
    )

    shapedirs[:, 0, 0] = np.array(
        [1.0, 2.0, 3.0]
    )
    shapedirs[:, 1, 1] = np.array(
        [4.0, 5.0, 6.0]
    )

    return template, faces, shapedirs


def test_zero_identity_returns_template_geometry():
    template, faces, shapedirs = _fixture()

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=faces,
        identity_directions=shapedirs,
    )

    result = evaluator.evaluate(
        identity_vector=np.zeros(2),
    )

    np.testing.assert_array_equal(
        result.vertices,
        template,
    )
    np.testing.assert_array_equal(
        result.faces,
        faces,
    )


def test_identity_coefficients_apply_linear_shape_directions():
    template, faces, shapedirs = _fixture()

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=faces,
        identity_directions=shapedirs,
    )

    identity = np.array([2.0, -0.5])

    expected = (
        template
        + shapedirs[:, :, 0] * 2.0
        + shapedirs[:, :, 1] * -0.5
    )

    result = evaluator.evaluate(
        identity_vector=identity,
    )

    np.testing.assert_allclose(
        result.vertices,
        expected,
    )


def test_from_flame_mapping_selects_identity_channels_only():
    template, faces, shapedirs = _fixture()

    all_dirs = np.concatenate(
        [
            shapedirs,
            np.ones((3, 3, 3)),
        ],
        axis=2,
    )

    evaluator = (
        AtlasPortraitFlameIdentityGeometryEvaluator
        .from_flame_mapping(
            flame={
                "v_template": template,
                "f": faces,
                "shapedirs": all_dirs,
            },
            identity_parameter_count=2,
        )
    )

    assert evaluator.identity_parameter_count == 2
    np.testing.assert_array_equal(
        evaluator.identity_directions,
        shapedirs,
    )


def test_geometry_and_model_arrays_are_read_only():
    template, faces, shapedirs = _fixture()

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=faces,
        identity_directions=shapedirs,
    )

    result = evaluator.evaluate(
        identity_vector=np.zeros(2),
    )

    assert evaluator.template_vertices.flags.writeable is False
    assert evaluator.faces.flags.writeable is False
    assert evaluator.identity_directions.flags.writeable is False
    assert result.vertices.flags.writeable is False
    assert result.faces.flags.writeable is False
    assert result.identity_vector.flags.writeable is False


def test_reports_geometry_dimensions():
    template, faces, shapedirs = _fixture()

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=faces,
        identity_directions=shapedirs,
    )

    result = evaluator.evaluate(
        identity_vector=np.zeros(2),
    )

    assert evaluator.vertex_count == 3
    assert evaluator.face_count == 1
    assert evaluator.identity_parameter_count == 2
    assert result.vertex_count == 3
    assert result.face_count == 1


@pytest.mark.parametrize(
    "identity",
    [
        np.zeros(1),
        np.zeros(3),
        np.array([np.nan, 0.0]),
        np.array([np.inf, 0.0]),
    ],
)
def test_invalid_identity_vector_is_rejected(identity):
    template, faces, shapedirs = _fixture()

    evaluator = AtlasPortraitFlameIdentityGeometryEvaluator(
        template_vertices=template,
        faces=faces,
        identity_directions=shapedirs,
    )

    with pytest.raises(ValueError):
        evaluator.evaluate(
            identity_vector=identity,
        )


def test_missing_flame_mapping_field_is_rejected():
    template, faces, shapedirs = _fixture()

    with pytest.raises(
        ValueError,
        match="missing required fields",
    ):
        AtlasPortraitFlameIdentityGeometryEvaluator.from_flame_mapping(
            flame={
                "v_template": template,
                "f": faces,
            },
            identity_parameter_count=2,
        )


def test_requested_identity_count_must_fit_shapedirs():
    template, faces, shapedirs = _fixture()

    with pytest.raises(
        ValueError,
        match="do not contain the requested",
    ):
        AtlasPortraitFlameIdentityGeometryEvaluator.from_flame_mapping(
            flame={
                "v_template": template,
                "f": faces,
                "shapedirs": shapedirs,
            },
            identity_parameter_count=3,
        )


def test_invalid_face_indices_are_rejected():
    template, _, shapedirs = _fixture()

    with pytest.raises(
        ValueError,
        match="invalid vertex indices",
    ):
        AtlasPortraitFlameIdentityGeometryEvaluator(
            template_vertices=template,
            faces=np.array([[0, 1, 99]]),
            identity_directions=shapedirs,
        )
