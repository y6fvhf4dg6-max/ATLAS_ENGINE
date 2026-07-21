from dataclasses import FrozenInstanceError
from types import MappingProxyType

import numpy as np
import pytest

from CORE.atlas_parametric_face_geometry import (
    AtlasParametricFaceGeometry,
)


REQUIRED_REGIONS = {
    "forehead": (0, 1),
    "left_brow": (0,),
    "right_brow": (1,),
    "left_eye_socket": (0, 2),
    "right_eye_socket": (1, 3),
    "nose_bridge": (0, 1, 2, 3),
    "nose_tip": (4,),
    "left_ala": (2,),
    "right_ala": (3,),
    "columella": (4,),
    "philtrum": (4, 5),
    "upper_lip": (4, 5),
    "lower_lip": (5,),
    "chin": (5,),
    "left_cheek": (2, 5),
    "right_cheek": (3, 5),
    "jaw": (2, 3, 5),
}


def _geometry(
    *,
    vertices=None,
    triangle_faces=None,
    surface_normals=None,
    uv_coordinates=None,
    semantic_vertex_regions=None,
    landmark_vertex_map=None,
    identity_parameters=None,
    expression_parameters=None,
    pose_parameters=None,
    confidence=None,
    visibility=None,
    metadata=None,
):
    if vertices is None:
        vertices = np.array(
            [
                [-1.0, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [-1.0, 0.0, 0.2],
                [1.0, 0.0, 0.2],
                [0.0, 0.1, 1.0],
                [0.0, -1.0, 0.0],
            ],
            dtype=np.float64,
        )

    if triangle_faces is None:
        triangle_faces = np.array(
            [
                [0, 2, 4],
                [0, 4, 1],
                [1, 4, 3],
                [2, 5, 4],
                [4, 5, 3],
            ],
            dtype=np.int64,
        )

    if surface_normals is None:
        surface_normals = np.array(
            [
                [0.0, 0.0, 2.0],
                [0.0, 0.0, 2.0],
                [0.0, 0.0, 2.0],
                [0.0, 0.0, 2.0],
                [0.0, 0.0, 2.0],
                [0.0, 0.0, 2.0],
            ],
            dtype=np.float64,
        )

    if uv_coordinates is None:
        uv_coordinates = np.array(
            [
                [0.0, 1.0],
                [1.0, 1.0],
                [0.0, 0.5],
                [1.0, 0.5],
                [0.5, 0.55],
                [0.5, 0.0],
            ],
            dtype=np.float64,
        )

    if semantic_vertex_regions is None:
        semantic_vertex_regions = REQUIRED_REGIONS

    if landmark_vertex_map is None:
        landmark_vertex_map = {
            "left_eye_outer": 0,
            "right_eye_outer": 1,
            "nose_tip": 4,
            "mouth_center": 5,
        }

    if identity_parameters is None:
        identity_parameters = np.array(
            [0.1, -0.2, 0.3],
            dtype=np.float64,
        )

    if expression_parameters is None:
        expression_parameters = np.array(
            [0.0, 0.25],
            dtype=np.float64,
        )

    if pose_parameters is None:
        pose_parameters = np.array(
            [0.0, 0.0, 0.0],
            dtype=np.float64,
        )

    if confidence is None:
        confidence = np.array(
            [0.95, 0.95, 0.9, 0.9, 0.98, 0.85],
            dtype=np.float64,
        )

    if visibility is None:
        visibility = np.array(
            [True, True, True, True, True, True],
            dtype=np.bool_,
        )

    if metadata is None:
        metadata = {
            "provider_id": "synthetic-canonical-fixture",
            "model_version": "1.0",
        }

    return AtlasParametricFaceGeometry(
        vertices=vertices,
        triangle_faces=triangle_faces,
        surface_normals=surface_normals,
        uv_coordinates=uv_coordinates,
        semantic_vertex_regions=semantic_vertex_regions,
        landmark_vertex_map=landmark_vertex_map,
        identity_parameters=identity_parameters,
        expression_parameters=expression_parameters,
        pose_parameters=pose_parameters,
        confidence=confidence,
        visibility=visibility,
        metadata=metadata,
    )


def test_geometry_normalizes_array_dtypes_and_shapes():
    geometry = _geometry(
        vertices=[
            [-1, 1, 0],
            [1, 1, 0],
            [-1, 0, 0.2],
            [1, 0, 0.2],
            [0, 0.1, 1],
            [0, -1, 0],
        ],
        triangle_faces=[
            [0, 2, 4],
            [0, 4, 1],
            [1, 4, 3],
            [2, 5, 4],
            [4, 5, 3],
        ],
    )

    assert geometry.vertices.dtype == np.float64
    assert geometry.vertices.shape == (6, 3)
    assert geometry.triangle_faces.dtype == np.int64
    assert geometry.triangle_faces.shape == (5, 3)
    assert geometry.surface_normals.dtype == np.float64
    assert geometry.uv_coordinates.dtype == np.float64
    assert geometry.confidence.dtype == np.float64
    assert geometry.visibility.dtype == np.bool_


def test_geometry_reports_counts():
    geometry = _geometry()

    assert geometry.vertex_count == 6
    assert geometry.triangle_count == 5
    assert geometry.identity_parameter_count == 3
    assert geometry.expression_parameter_count == 2
    assert geometry.pose_parameter_count == 3


@pytest.mark.parametrize(
    "field_name",
    [
        "vertices",
        "triangle_faces",
        "surface_normals",
        "uv_coordinates",
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
        "confidence",
        "visibility",
    ],
)
def test_geometry_arrays_are_read_only(field_name):
    geometry = _geometry()

    array = getattr(
        geometry,
        field_name,
    )

    assert not array.flags.writeable

    with pytest.raises(ValueError):
        array.flat[0] = array.flat[0]


def test_geometry_copies_input_arrays():
    vertices = np.array(
        [
            [-1.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, 0.0, 0.2],
            [1.0, 0.0, 0.2],
            [0.0, 0.1, 1.0],
            [0.0, -1.0, 0.0],
        ]
    )

    geometry = _geometry(
        vertices=vertices,
    )

    vertices[0, 0] = 99.0

    assert geometry.vertices[0, 0] == pytest.approx(-1.0)


def test_geometry_is_frozen():
    geometry = _geometry()

    with pytest.raises(FrozenInstanceError):
        geometry.vertices = np.zeros((6, 3))


def test_geometry_normalizes_surface_normals():
    geometry = _geometry()

    lengths = np.linalg.norm(
        geometry.surface_normals,
        axis=1,
    )

    assert np.allclose(
        lengths,
        1.0,
    )


def test_geometry_normalizes_semantic_regions():
    regions = dict(REQUIRED_REGIONS)
    regions["upper_lip"] = (5, 4, 5, 4)

    geometry = _geometry(
        semantic_vertex_regions=regions,
    )

    assert isinstance(
        geometry.semantic_vertex_regions,
        MappingProxyType,
    )
    assert geometry.semantic_vertex_regions[
        "upper_lip"
    ] == (4, 5)


def test_geometry_preserves_region_overlap():
    geometry = _geometry()

    assert 4 in geometry.semantic_vertex_regions[
        "nose_tip"
    ]
    assert 4 in geometry.semantic_vertex_regions[
        "columella"
    ]
    assert 4 in geometry.semantic_vertex_regions[
        "upper_lip"
    ]


def test_geometry_normalizes_landmark_map():
    geometry = _geometry(
        landmark_vertex_map={
            " nose_tip ": 4,
            "left_eye_outer": 0,
        }
    )

    assert isinstance(
        geometry.landmark_vertex_map,
        MappingProxyType,
    )
    assert geometry.landmark_vertex_map == {
        "left_eye_outer": 0,
        "nose_tip": 4,
    }


def test_geometry_preserves_parameter_separation():
    geometry = _geometry()

    assert not np.shares_memory(
        geometry.identity_parameters,
        geometry.expression_parameters,
    )
    assert not np.shares_memory(
        geometry.identity_parameters,
        geometry.pose_parameters,
    )
    assert not np.shares_memory(
        geometry.expression_parameters,
        geometry.pose_parameters,
    )


def test_geometry_copies_metadata():
    metadata = {
        "provider_id": "synthetic",
    }

    geometry = _geometry(
        metadata=metadata,
    )

    metadata["provider_id"] = "changed"

    assert geometry.metadata == {
        "provider_id": "synthetic",
    }
    assert isinstance(
        geometry.metadata,
        MappingProxyType,
    )


@pytest.mark.parametrize(
    (
        "field_name",
        "value",
        "match",
    ),
    [
        (
            "vertices",
            np.zeros((6, 2)),
            "vertices",
        ),
        (
            "triangle_faces",
            np.zeros((5, 2), dtype=np.int64),
            "triangle_faces",
        ),
        (
            "surface_normals",
            np.zeros((6, 2)),
            "surface_normals",
        ),
        (
            "uv_coordinates",
            np.zeros((6, 3)),
            "uv_coordinates",
        ),
        (
            "identity_parameters",
            np.zeros((2, 2)),
            "identity_parameters",
        ),
        (
            "expression_parameters",
            np.zeros((2, 2)),
            "expression_parameters",
        ),
        (
            "pose_parameters",
            np.zeros((2, 2)),
            "pose_parameters",
        ),
        (
            "confidence",
            np.zeros((6, 1)),
            "confidence",
        ),
        (
            "visibility",
            np.zeros((6, 1)),
            "visibility",
        ),
    ],
)
def test_geometry_rejects_invalid_array_shapes(
    field_name,
    value,
    match,
):
    with pytest.raises(
        ValueError,
        match=match,
    ):
        _geometry(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "vertices",
        "surface_normals",
        "uv_coordinates",
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
        "confidence",
    ],
)
def test_geometry_rejects_non_finite_values(field_name):
    geometry = _geometry()
    value = np.array(
        getattr(
            geometry,
            field_name,
        ),
        copy=True,
    )

    value.flat[0] = np.nan

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        _geometry(
            **{
                field_name: value,
            }
        )


def test_geometry_rejects_too_few_vertices():
    with pytest.raises(
        ValueError,
        match="at least three",
    ):
        _geometry(
            vertices=np.zeros((2, 3)),
        )


def test_geometry_rejects_empty_triangle_faces():
    with pytest.raises(
        ValueError,
        match="triangle_faces",
    ):
        _geometry(
            triangle_faces=np.empty(
                (0, 3),
                dtype=np.int64,
            ),
        )


@pytest.mark.parametrize(
    "triangle_faces",
    [
        np.array(
            [
                [-1, 1, 2],
            ]
        ),
        np.array(
            [
                [0, 1, 6],
            ]
        ),
    ],
)
def test_geometry_rejects_out_of_range_triangle_indices(
    triangle_faces,
):
    with pytest.raises(
        ValueError,
        match="triangle",
    ):
        _geometry(
            triangle_faces=triangle_faces,
        )


def test_geometry_rejects_non_integer_triangle_indices():
    with pytest.raises(
        ValueError,
        match="integer",
    ):
        _geometry(
            triangle_faces=np.array(
                [
                    [0.0, 1.5, 2.0],
                ]
            ),
        )


def test_geometry_rejects_degenerate_triangle():
    with pytest.raises(
        ValueError,
        match="degenerate",
    ):
        _geometry(
            triangle_faces=np.array(
                [
                    [0, 0, 1],
                ]
            ),
        )


def test_geometry_rejects_zero_surface_normal():
    normals = np.ones(
        (6, 3),
        dtype=np.float64,
    )
    normals[2] = 0.0

    with pytest.raises(
        ValueError,
        match="zero",
    ):
        _geometry(
            surface_normals=normals,
        )


def test_geometry_rejects_uv_outside_unit_range():
    uv_coordinates = np.zeros(
        (6, 2),
        dtype=np.float64,
    )
    uv_coordinates[0, 0] = 1.01

    with pytest.raises(
        ValueError,
        match="0.0..1.0",
    ):
        _geometry(
            uv_coordinates=uv_coordinates,
        )


def test_geometry_requires_all_semantic_regions():
    regions = dict(REQUIRED_REGIONS)
    del regions["philtrum"]

    with pytest.raises(
        ValueError,
        match="philtrum",
    ):
        _geometry(
            semantic_vertex_regions=regions,
        )


def test_geometry_rejects_empty_semantic_region():
    regions = dict(REQUIRED_REGIONS)
    regions["philtrum"] = ()

    with pytest.raises(
        ValueError,
        match="philtrum",
    ):
        _geometry(
            semantic_vertex_regions=regions,
        )


def test_geometry_rejects_out_of_range_semantic_index():
    regions = dict(REQUIRED_REGIONS)
    regions["philtrum"] = (6,)

    with pytest.raises(
        ValueError,
        match="philtrum",
    ):
        _geometry(
            semantic_vertex_regions=regions,
        )


def test_geometry_rejects_out_of_range_landmark_index():
    with pytest.raises(
        ValueError,
        match="landmark",
    ):
        _geometry(
            landmark_vertex_map={
                "nose_tip": 6,
            },
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
    ],
)
def test_geometry_rejects_empty_parameter_vector(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _geometry(
            **{
                field_name: np.array(
                    [],
                    dtype=np.float64,
                ),
            }
        )


@pytest.mark.parametrize(
    "value",
    [
        -0.01,
        1.01,
    ],
)
def test_geometry_rejects_confidence_outside_unit_range(
    value,
):
    confidence = np.full(
        6,
        0.9,
        dtype=np.float64,
    )
    confidence[0] = value

    with pytest.raises(
        ValueError,
        match="0.0..1.0",
    ):
        _geometry(
            confidence=confidence,
        )


def test_geometry_rejects_non_boolean_visibility():
    with pytest.raises(
        TypeError,
        match="visibility",
    ):
        _geometry(
            visibility=np.ones(
                6,
                dtype=np.int64,
            ),
        )


def test_geometry_rejects_invalid_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _geometry(
            metadata=[
                "invalid",
            ],
        )


def test_geometry_to_dict_is_deterministic():
    first = _geometry()
    second = _geometry(
        semantic_vertex_regions=dict(
            reversed(
                list(
                    REQUIRED_REGIONS.items()
                )
            )
        )
    )

    assert first.to_dict() == second.to_dict()


def test_geometry_to_dict_contains_plain_values():
    payload = _geometry().to_dict()

    assert payload["vertex_count"] == 6
    assert payload["triangle_count"] == 5
    assert isinstance(
        payload["vertices"],
        list,
    )
    assert isinstance(
        payload["triangle_faces"],
        list,
    )
    assert payload["semantic_vertex_regions"][
        "nose_tip"
    ] == [4]
    assert payload["landmark_vertex_map"][
        "nose_tip"
    ] == 4
    assert payload["visibility"] == [
        True,
        True,
        True,
        True,
        True,
        True,
    ]
