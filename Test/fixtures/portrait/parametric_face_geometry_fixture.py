from __future__ import annotations

import numpy as np

from CORE.atlas_parametric_face_geometry import (
    AtlasParametricFaceGeometry,
)


_X_COORDINATES = np.array(
    [
        -1.0,
        -0.5,
        0.0,
        0.5,
        1.0,
    ],
    dtype=np.float64,
)

_Y_COORDINATES = np.array(
    [
        1.0,
        0.5,
        0.0,
        -0.5,
        -1.0,
    ],
    dtype=np.float64,
)

_Z_COORDINATES = np.array(
    [
        [0.05, 0.12, 0.18, 0.12, 0.05],
        [0.10, 0.20, 0.35, 0.20, 0.10],
        [0.12, 0.28, 1.00, 0.28, 0.12],
        [0.08, 0.18, 0.25, 0.18, 0.08],
        [0.02, 0.08, 0.15, 0.08, 0.02],
    ],
    dtype=np.float64,
)

_SEMANTIC_VERTEX_REGIONS = {
    "forehead": (
        1,
        2,
        3,
    ),
    "left_brow": (
        7,
        8,
        9,
    ),
    "right_brow": (
        5,
        6,
        7,
    ),
    "left_eye_socket": (
        8,
        9,
        13,
    ),
    "right_eye_socket": (
        5,
        6,
        11,
    ),
    "nose_bridge": (
        7,
        12,
    ),
    "nose_tip": (
        12,
    ),
    "left_ala": (
        13,
    ),
    "right_ala": (
        11,
    ),
    "columella": (
        12,
        17,
    ),
    "philtrum": (
        17,
    ),
    "upper_lip": (
        16,
        17,
        18,
    ),
    "lower_lip": (
        21,
        22,
        23,
    ),
    "chin": (
        22,
    ),
    "left_cheek": (
        13,
        18,
    ),
    "right_cheek": (
        11,
        16,
    ),
    "jaw": (
        20,
        21,
        22,
        23,
        24,
    ),
}

_LANDMARK_VERTEX_MAP = {
    "chin_tip": 22,
    "left_brow_center": 8,
    "left_eye_center": 8,
    "left_eye_inner": 7,
    "left_eye_outer": 9,
    "left_mouth_corner": 18,
    "nose_bridge": 7,
    "nose_tip": 12,
    "right_brow_center": 6,
    "right_eye_center": 6,
    "right_eye_inner": 7,
    "right_eye_outer": 5,
    "right_mouth_corner": 16,
}


def fixture_semantic_region_names() -> tuple[str, ...]:
    """
    Returns all synthetic canonical semantic-region names
    in deterministic order.
    """

    return tuple(
        sorted(
            _SEMANTIC_VERTEX_REGIONS,
        )
    )


def fixture_landmark_names() -> tuple[str, ...]:
    """
    Returns all synthetic canonical landmark names
    in deterministic order.
    """

    return tuple(
        sorted(
            _LANDMARK_VERTEX_MAP,
        )
    )


def load_parametric_face_geometry_fixture(
) -> AtlasParametricFaceGeometry:
    """
    Returns a deterministic provider-independent
    synthetic canonical face mesh.

    The fixture contains a small connected triangular
    surface with fixed topology and a frontal
    face-like depth profile. It has no dependency on
    FLAME model files, private portraits, machine-learning
    frameworks, or reconstruction weights.
    """

    vertices = _build_vertices()
    triangle_faces = _build_triangle_faces()
    surface_normals = _build_vertex_normals(
        vertices=vertices,
        triangle_faces=triangle_faces,
    )
    uv_coordinates = _build_uv_coordinates()

    return AtlasParametricFaceGeometry(
        vertices=vertices,
        triangle_faces=triangle_faces,
        surface_normals=surface_normals,
        uv_coordinates=uv_coordinates,
        semantic_vertex_regions=dict(
            _SEMANTIC_VERTEX_REGIONS,
        ),
        landmark_vertex_map=dict(
            _LANDMARK_VERTEX_MAP,
        ),
        identity_parameters=np.array(
            [
                0.10,
                -0.05,
                0.08,
                0.02,
            ],
            dtype=np.float64,
        ),
        expression_parameters=np.array(
            [
                0.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
        pose_parameters=np.array(
            [
                0.0,
                0.0,
                0.0,
            ],
            dtype=np.float64,
        ),
        confidence=np.ones(
            25,
            dtype=np.float64,
        ),
        visibility=np.ones(
            25,
            dtype=np.bool_,
        ),
        metadata={
            "coordinate_system": (
                "canonical_frontal_xyz"
            ),
            "fixture_name": (
                "synthetic_parametric_face_geometry_v1"
            ),
            "model_family": "synthetic",
            "provider_id": (
                "atlas-synthetic-canonical-fixture"
            ),
            "synthetic": True,
            "topology": "fixed",
            "view_type": "front",
        },
    )


def _build_vertices() -> np.ndarray:
    vertices: list[
        tuple[
            float,
            float,
            float,
        ]
    ] = []

    for row_index, y_coordinate in enumerate(
        _Y_COORDINATES,
    ):
        for column_index, x_coordinate in enumerate(
            _X_COORDINATES,
        ):
            vertices.append(
                (
                    float(
                        x_coordinate,
                    ),
                    float(
                        y_coordinate,
                    ),
                    float(
                        _Z_COORDINATES[
                            row_index,
                            column_index,
                        ]
                    ),
                )
            )

    return np.asarray(
        vertices,
        dtype=np.float64,
    )


def _build_triangle_faces() -> np.ndarray:
    triangle_faces: list[
        tuple[
            int,
            int,
            int,
        ]
    ] = []

    column_count = len(
        _X_COORDINATES,
    )

    row_count = len(
        _Y_COORDINATES,
    )

    for row_index in range(
        row_count - 1,
    ):
        for column_index in range(
            column_count - 1,
        ):
            top_left = (
                row_index * column_count
                + column_index
            )

            top_right = top_left + 1

            bottom_left = (
                top_left + column_count
            )

            bottom_right = (
                bottom_left + 1
            )

            triangle_faces.append(
                (
                    top_left,
                    bottom_left,
                    top_right,
                )
            )

            triangle_faces.append(
                (
                    top_right,
                    bottom_left,
                    bottom_right,
                )
            )

    return np.asarray(
        triangle_faces,
        dtype=np.int64,
    )


def _build_vertex_normals(
    *,
    vertices: np.ndarray,
    triangle_faces: np.ndarray,
) -> np.ndarray:
    normals = np.zeros_like(
        vertices,
        dtype=np.float64,
    )

    for triangle in triangle_faces:
        first_index = int(
            triangle[0],
        )

        second_index = int(
            triangle[1],
        )

        third_index = int(
            triangle[2],
        )

        first_vertex = vertices[
            first_index
        ]

        second_vertex = vertices[
            second_index
        ]

        third_vertex = vertices[
            third_index
        ]

        face_normal = np.cross(
            second_vertex - first_vertex,
            third_vertex - first_vertex,
        )

        normals[
            first_index
        ] += face_normal

        normals[
            second_index
        ] += face_normal

        normals[
            third_index
        ] += face_normal

    lengths = np.linalg.norm(
        normals,
        axis=1,
    )

    if np.any(
        lengths <= 1e-12,
    ):
        raise RuntimeError(
            "Synthetic fixture produced a zero "
            "vertex normal."
        )

    return (
        normals
        / lengths[
            :,
            np.newaxis,
        ]
    ).astype(
        np.float64,
        copy=True,
    )


def _build_uv_coordinates() -> np.ndarray:
    uv_coordinates: list[
        tuple[
            float,
            float,
        ]
    ] = []

    for y_coordinate in _Y_COORDINATES:
        for x_coordinate in _X_COORDINATES:
            uv_coordinates.append(
                (
                    float(
                        (
                            x_coordinate
                            + 1.0
                        )
                        * 0.5
                    ),
                    float(
                        (
                            y_coordinate
                            + 1.0
                        )
                        * 0.5
                    ),
                )
            )

    return np.asarray(
        uv_coordinates,
        dtype=np.float64,
    )
