from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from CORE.atlas_portrait_flame_canonical_model import (
    AtlasPortraitFlameCanonicalModel,
)
from CORE.atlas_portrait_weak_perspective_camera import (
    AtlasPortraitWeakPerspectiveCamera,
)


DEFAULT_RING_COUNT = 18
DEFAULT_SEGMENT_COUNT = 72
DEFAULT_IMAGE_WIDTH = 256
DEFAULT_IMAGE_HEIGHT = 256


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasSyntheticFlameFaceFixture:
    model: AtlasPortraitFlameCanonicalModel
    skinned_vertices: np.ndarray
    camera: AtlasPortraitWeakPerspectiveCamera
    image_width: int
    image_height: int


def build_synthetic_flame_face_fixture(
    *,
    ring_count: int = DEFAULT_RING_COUNT,
    segment_count: int = DEFAULT_SEGMENT_COUNT,
    image_width: int = DEFAULT_IMAGE_WIDTH,
    image_height: int = DEFAULT_IMAGE_HEIGHT,
) -> AtlasSyntheticFlameFaceFixture:
    if ring_count < 2:
        raise ValueError(
            "ring_count must be at least 2."
        )

    if segment_count < 8:
        raise ValueError(
            "segment_count must be at least 8."
        )

    if image_width < 2:
        raise ValueError(
            "image_width must be at least 2."
        )

    if image_height < 2:
        raise ValueError(
            "image_height must be at least 2."
        )

    vertices = [
        (
            0.0,
            0.0,
            _surface_depth(
                0.0,
                0.0,
                radial_distance=0.0,
            ),
        )
    ]

    for ring_index in range(
        1,
        ring_count + 1,
    ):
        radial_distance = (
            float(ring_index)
            / float(ring_count)
        )

        for segment_index in range(
            segment_count,
        ):
            angle = (
                2.0
                * np.pi
                * float(segment_index)
                / float(segment_count)
            )

            normalized_x = (
                radial_distance
                * np.cos(
                    angle,
                )
            )
            normalized_y = (
                radial_distance
                * np.sin(
                    angle,
                )
            )

            x_coordinate = (
                0.92
                * normalized_x
            )
            y_coordinate = (
                1.15
                * normalized_y
            )
            z_coordinate = _surface_depth(
                normalized_x,
                normalized_y,
                radial_distance=radial_distance,
            )

            vertices.append(
                (
                    x_coordinate,
                    y_coordinate,
                    z_coordinate,
                )
            )

    faces: list[
        tuple[
            int,
            int,
            int,
        ]
    ] = []

    first_ring_start = 1

    for segment_index in range(
        segment_count,
    ):
        current_index = (
            first_ring_start
            + segment_index
        )
        next_index = (
            first_ring_start
            + (
                segment_index + 1
            )
            % segment_count
        )

        faces.append(
            (
                0,
                current_index,
                next_index,
            )
        )

    for ring_index in range(
        1,
        ring_count,
    ):
        inner_ring_start = (
            1
            + (
                ring_index - 1
            )
            * segment_count
        )
        outer_ring_start = (
            1
            + ring_index
            * segment_count
        )

        for segment_index in range(
            segment_count,
        ):
            next_segment_index = (
                segment_index + 1
            ) % segment_count

            inner_current = (
                inner_ring_start
                + segment_index
            )
            inner_next = (
                inner_ring_start
                + next_segment_index
            )
            outer_current = (
                outer_ring_start
                + segment_index
            )
            outer_next = (
                outer_ring_start
                + next_segment_index
            )

            faces.append(
                (
                    inner_current,
                    outer_current,
                    outer_next,
                )
            )
            faces.append(
                (
                    inner_current,
                    outer_next,
                    inner_next,
                )
            )

    template_vertices = np.asarray(
        vertices,
        dtype=np.float64,
    )
    triangle_faces = np.asarray(
        faces,
        dtype=np.int64,
    )

    vertex_count = int(
        template_vertices.shape[0]
    )

    model = AtlasPortraitFlameCanonicalModel(
        template_vertices=template_vertices,
        triangle_faces=triangle_faces,
        identity_shape_directions=np.zeros(
            (
                vertex_count,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        expression_shape_directions=np.zeros(
            (
                vertex_count,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        pose_directions=np.zeros(
            (
                vertex_count,
                3,
                1,
            ),
            dtype=np.float64,
        ),
        pose_parameter_count=3,
        joint_regressor=np.full(
            (
                1,
                vertex_count,
            ),
            1.0
            / float(vertex_count),
            dtype=np.float64,
        ),
        skinning_weights=np.ones(
            (
                vertex_count,
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
            "model_version": (
                "synthetic-face-preview-v1"
            ),
            "synthetic": True,
            "ring_count": ring_count,
            "segment_count": segment_count,
        },
    )

    camera = AtlasPortraitWeakPerspectiveCamera(
        scale=90.0,
        translation_x=(
            float(image_width - 1)
            * 0.50
        ),
        translation_y=(
            float(image_height - 1)
            * 0.50
        ),
        projected_points_2d=np.array(
            [
                [
                    float(image_width - 1)
                    * 0.50,
                    float(image_height - 1)
                    * 0.50,
                ],
            ],
            dtype=np.float64,
        ),
        weighted_root_mean_square_error=0.0,
        metadata={
            "camera_model": "weak_perspective",
            "synthetic": True,
            "fixture": (
                "synthetic-face-preview-v1"
            ),
        },
    )

    skinned_vertices = (
        template_vertices.copy()
    )

    skinned_vertices.setflags(
        write=False,
    )

    return AtlasSyntheticFlameFaceFixture(
        model=model,
        skinned_vertices=skinned_vertices,
        camera=camera,
        image_width=image_width,
        image_height=image_height,
    )


def _surface_depth(
    normalized_x: float,
    normalized_y: float,
    *,
    radial_distance: float,
) -> float:
    base_face = (
        0.56
        * max(
            0.0,
            1.0
            - radial_distance
            * radial_distance,
        )
    )

    forehead = (
        0.08
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=-0.48,
            scale_x=0.55,
            scale_y=0.34,
        )
    )

    nose_bridge = (
        0.38
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=-0.08,
            scale_x=0.13,
            scale_y=0.42,
        )
    )

    nose_tip = (
        0.31
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=0.10,
            scale_x=0.17,
            scale_y=0.17,
        )
    )

    left_cheek = (
        0.16
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=-0.38,
            center_y=0.08,
            scale_x=0.28,
            scale_y=0.30,
        )
    )

    right_cheek = (
        0.16
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.38,
            center_y=0.08,
            scale_x=0.28,
            scale_y=0.30,
        )
    )

    left_eye_socket = (
        -0.15
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=-0.30,
            center_y=-0.24,
            scale_x=0.20,
            scale_y=0.11,
        )
    )

    right_eye_socket = (
        -0.15
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.30,
            center_y=-0.24,
            scale_x=0.20,
            scale_y=0.11,
        )
    )

    philtrum = (
        -0.07
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=0.31,
            scale_x=0.09,
            scale_y=0.10,
        )
    )

    mouth_groove = (
        -0.11
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=0.43,
            scale_x=0.34,
            scale_y=0.075,
        )
    )

    lower_lip = (
        0.08
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=0.50,
            scale_x=0.27,
            scale_y=0.09,
        )
    )

    chin = (
        0.14
        * _gaussian(
            normalized_x,
            normalized_y,
            center_x=0.0,
            center_y=0.72,
            scale_x=0.31,
            scale_y=0.22,
        )
    )

    return float(
        base_face
        + forehead
        + nose_bridge
        + nose_tip
        + left_cheek
        + right_cheek
        + left_eye_socket
        + right_eye_socket
        + philtrum
        + mouth_groove
        + lower_lip
        + chin
    )


def _gaussian(
    x_coordinate: float,
    y_coordinate: float,
    *,
    center_x: float,
    center_y: float,
    scale_x: float,
    scale_y: float,
) -> float:
    return float(
        np.exp(
            -(
                (
                    (
                        x_coordinate
                        - center_x
                    )
                    / scale_x
                )
                ** 2
                + (
                    (
                        y_coordinate
                        - center_y
                    )
                    / scale_y
                )
                ** 2
            )
        )
    )
