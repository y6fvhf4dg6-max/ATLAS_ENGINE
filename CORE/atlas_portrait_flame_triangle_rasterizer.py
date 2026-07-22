from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from CORE.atlas_portrait_flame_triangle_visibility_evaluator import (
    AtlasPortraitFlameTriangleVisibility,
)
from CORE.atlas_portrait_flame_weak_perspective_projection_evaluator import (
    AtlasPortraitFlameWeakPerspectiveProjection,
)


@dataclass(
    frozen=True,
    slots=True,
)
class AtlasPortraitFlameTriangleRasterization:
    """
    Immutable FLAME triangle-rasterization contract.

    Buffers use image-array ordering:

        shape = (image_height, image_width)
        access = buffer[y, x]

    Background pixels contain:
    - triangle index -1
    - positive infinite depth
    - zero barycentric coordinates

    Covered pixels contain barycentric coordinates in the
    triangle-face corner order.
    """

    image_width: int
    image_height: int
    coverage_mask: np.ndarray
    triangle_index_buffer: np.ndarray
    depth_buffer: np.ndarray
    barycentric_coordinates: Any = None

    _BARYCENTRIC_TOLERANCE = 1.0e-12

    def __post_init__(
        self,
    ) -> None:
        image_width = self._normalize_dimension(
            self.image_width,
            name="image_width",
        )
        image_height = self._normalize_dimension(
            self.image_height,
            name="image_height",
        )

        coverage_mask = np.asarray(
            self.coverage_mask,
            dtype=np.bool_,
        ).copy()
        triangle_index_buffer = np.asarray(
            self.triangle_index_buffer,
            dtype=np.int64,
        ).copy()
        depth_buffer = np.asarray(
            self.depth_buffer,
            dtype=np.float64,
        ).copy()

        expected_shape = (
            image_height,
            image_width,
        )

        if coverage_mask.shape != expected_shape:
            raise ValueError(
                "coverage_mask must have shape "
                f"{expected_shape}."
            )

        if triangle_index_buffer.shape != expected_shape:
            raise ValueError(
                "triangle_index_buffer must have shape "
                f"{expected_shape}."
            )

        if depth_buffer.shape != expected_shape:
            raise ValueError(
                "depth_buffer must have shape "
                f"{expected_shape}."
            )

        barycentric_coordinates = (
            self._normalize_barycentric_coordinates(
                self.barycentric_coordinates,
                coverage_mask=coverage_mask,
                image_width=image_width,
                image_height=image_height,
            )
        )

        if np.isnan(
            depth_buffer,
        ).any():
            raise ValueError(
                "depth_buffer must not contain NaN values."
            )

        if np.any(
            triangle_index_buffer[
                ~coverage_mask
            ]
            != -1
        ):
            raise ValueError(
                "Background triangle indices must equal -1."
            )

        if np.any(
            triangle_index_buffer[
                coverage_mask
            ]
            < 0
        ):
            raise ValueError(
                "Covered triangle indices must not be negative."
            )

        if np.any(
            ~np.isposinf(
                depth_buffer[
                    ~coverage_mask
                ]
            )
        ):
            raise ValueError(
                "Background depth values must equal positive infinity."
            )

        if np.any(
            ~np.isfinite(
                depth_buffer[
                    coverage_mask
                ]
            )
        ):
            raise ValueError(
                "Covered depth values must be finite."
            )

        coverage_mask.setflags(
            write=False,
        )
        triangle_index_buffer.setflags(
            write=False,
        )
        depth_buffer.setflags(
            write=False,
        )
        barycentric_coordinates.setflags(
            write=False,
        )

        object.__setattr__(
            self,
            "image_width",
            image_width,
        )
        object.__setattr__(
            self,
            "image_height",
            image_height,
        )
        object.__setattr__(
            self,
            "coverage_mask",
            coverage_mask,
        )
        object.__setattr__(
            self,
            "triangle_index_buffer",
            triangle_index_buffer,
        )
        object.__setattr__(
            self,
            "depth_buffer",
            depth_buffer,
        )
        object.__setattr__(
            self,
            "barycentric_coordinates",
            barycentric_coordinates,
        )

    @property
    def covered_pixel_count(
        self,
    ) -> int:
        return int(
            np.count_nonzero(
                self.coverage_mask,
            )
        )

    @property
    def background_pixel_count(
        self,
    ) -> int:
        return (
            self.image_width
            * self.image_height
            - self.covered_pixel_count
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "image_width": self.image_width,
            "image_height": self.image_height,
            "covered_pixel_count": (
                self.covered_pixel_count
            ),
            "background_pixel_count": (
                self.background_pixel_count
            ),
            "coverage_mask": self.coverage_mask.tolist(),
            "triangle_index_buffer": (
                self.triangle_index_buffer.tolist()
            ),
            "depth_buffer": self.depth_buffer.tolist(),
            "barycentric_coordinates": (
                self.barycentric_coordinates.tolist()
            ),
        }

    @classmethod
    def _normalize_barycentric_coordinates(
        cls,
        value: Any,
        *,
        coverage_mask: np.ndarray,
        image_width: int,
        image_height: int,
    ) -> np.ndarray:
        expected_shape = (
            image_height,
            image_width,
            3,
        )

        if value is None:
            coordinates = np.zeros(
                expected_shape,
                dtype=np.float64,
            )

            coordinates[
                coverage_mask,
                0,
            ] = 1.0

            return coordinates

        try:
            coordinates = np.asarray(
                value,
                dtype=np.float64,
            ).copy()
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "barycentric_coordinates must be numeric."
            ) from exc

        if coordinates.shape != expected_shape:
            raise ValueError(
                "barycentric_coordinates must have shape "
                f"{expected_shape}."
            )

        if not np.isfinite(
            coordinates,
        ).all():
            raise ValueError(
                "barycentric_coordinates contains "
                "non-finite values."
            )

        background_coordinates = coordinates[
            ~coverage_mask
        ]

        if not np.allclose(
            background_coordinates,
            0.0,
            rtol=0.0,
            atol=cls._BARYCENTRIC_TOLERANCE,
        ):
            raise ValueError(
                "Background barycentric coordinates "
                "must equal zero."
            )

        covered_coordinates = coordinates[
            coverage_mask
        ]

        if covered_coordinates.size:
            if np.any(
                covered_coordinates
                < -cls._BARYCENTRIC_TOLERANCE
            ):
                raise ValueError(
                    "Covered barycentric coordinates "
                    "must not be negative."
                )

            covered_sums = np.sum(
                covered_coordinates,
                axis=1,
                dtype=np.float64,
            )

            if not np.allclose(
                covered_sums,
                1.0,
                rtol=0.0,
                atol=cls._BARYCENTRIC_TOLERANCE,
            ):
                raise ValueError(
                    "Covered barycentric coordinates "
                    "must sum to 1.0."
                )

        return coordinates

    @staticmethod
    def _normalize_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            (
                bool,
                np.bool_,
            ),
        ):
            raise ValueError(
                f"{name} must be a positive integer."
            )

        try:
            numeric_value = float(
                value,
            )
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                f"{name} must be a positive integer."
            ) from exc

        if (
            not np.isfinite(
                numeric_value,
            )
            or not numeric_value.is_integer()
            or numeric_value <= 0.0
        ):
            raise ValueError(
                f"{name} must be a positive integer."
            )

        return int(
            numeric_value
        )


class AtlasPortraitFlameTriangleRasterizer:
    """
    Rasterizes visible projected FLAME triangles.

    Projected coordinates are interpreted directly as raster
    coordinates. Integer pixel coordinates are sampled and triangle
    boundaries are included.

    Occlusion uses a constant per-triangle mean depth supplied by the
    visibility contract. Smaller depth values are treated as nearer.

    Each covered pixel retains barycentric coordinates in triangle
    corner order for later vertex-attribute interpolation.

    This rasterizer performs no viewport transformation, perspective
    correction, interpolated depth, shading, or preview export.
    """

    _EDGE_TOLERANCE = 1.0e-12

    @classmethod
    def rasterize(
        cls,
        projection: (
            AtlasPortraitFlameWeakPerspectiveProjection
        ),
        *,
        visibility: AtlasPortraitFlameTriangleVisibility,
        image_width: Any,
        image_height: Any,
    ) -> AtlasPortraitFlameTriangleRasterization:
        if not isinstance(
            projection,
            AtlasPortraitFlameWeakPerspectiveProjection,
        ):
            raise TypeError(
                "projection must be an "
                "AtlasPortraitFlameWeakPerspectiveProjection "
                "instance."
            )

        if not isinstance(
            visibility,
            AtlasPortraitFlameTriangleVisibility,
        ):
            raise TypeError(
                "visibility must be an "
                "AtlasPortraitFlameTriangleVisibility instance."
            )

        normalized_width = (
            AtlasPortraitFlameTriangleRasterization
            ._normalize_dimension(
                image_width,
                name="image_width",
            )
        )
        normalized_height = (
            AtlasPortraitFlameTriangleRasterization
            ._normalize_dimension(
                image_height,
                name="image_height",
            )
        )

        if projection.face_count != visibility.triangle_count:
            raise ValueError(
                "projection and visibility triangle_count "
                "must match."
            )

        buffer_shape = (
            normalized_height,
            normalized_width,
        )

        coverage_mask = np.zeros(
            buffer_shape,
            dtype=np.bool_,
        )
        triangle_index_buffer = np.full(
            buffer_shape,
            -1,
            dtype=np.int64,
        )
        depth_buffer = np.full(
            buffer_shape,
            np.inf,
            dtype=np.float64,
        )
        barycentric_coordinates = np.zeros(
            (
                normalized_height,
                normalized_width,
                3,
            ),
            dtype=np.float64,
        )

        projected_vertices = np.asarray(
            projection.projected_vertices_2d,
            dtype=np.float64,
        )
        faces = np.asarray(
            projection.triangle_faces,
            dtype=np.int64,
        )

        for triangle_index in range(
            projection.face_count,
        ):
            if not bool(
                visibility.visible_triangle_mask[
                    triangle_index
                ]
            ):
                continue

            triangle = projected_vertices[
                faces[
                    triangle_index
                ]
            ]

            minimum_x = max(
                0,
                int(
                    np.ceil(
                        np.min(
                            triangle[
                                :,
                                0,
                            ]
                        )
                        - cls._EDGE_TOLERANCE
                    )
                ),
            )
            maximum_x = min(
                normalized_width - 1,
                int(
                    np.floor(
                        np.max(
                            triangle[
                                :,
                                0,
                            ]
                        )
                        + cls._EDGE_TOLERANCE
                    )
                ),
            )
            minimum_y = max(
                0,
                int(
                    np.ceil(
                        np.min(
                            triangle[
                                :,
                                1,
                            ]
                        )
                        - cls._EDGE_TOLERANCE
                    )
                ),
            )
            maximum_y = min(
                normalized_height - 1,
                int(
                    np.floor(
                        np.max(
                            triangle[
                                :,
                                1,
                            ]
                        )
                        + cls._EDGE_TOLERANCE
                    )
                ),
            )

            if (
                minimum_x > maximum_x
                or minimum_y > maximum_y
            ):
                continue

            triangle_depth = float(
                visibility.mean_triangle_depths[
                    triangle_index
                ]
            )

            for pixel_y in range(
                minimum_y,
                maximum_y + 1,
            ):
                for pixel_x in range(
                    minimum_x,
                    maximum_x + 1,
                ):
                    weights = cls._calculate_barycentric_coordinates(
                        triangle,
                        x=float(
                            pixel_x
                        ),
                        y=float(
                            pixel_y
                        ),
                    )

                    if weights is None:
                        continue

                    if triangle_depth >= depth_buffer[
                        pixel_y,
                        pixel_x,
                    ]:
                        continue

                    coverage_mask[
                        pixel_y,
                        pixel_x,
                    ] = True
                    triangle_index_buffer[
                        pixel_y,
                        pixel_x,
                    ] = triangle_index
                    depth_buffer[
                        pixel_y,
                        pixel_x,
                    ] = triangle_depth
                    barycentric_coordinates[
                        pixel_y,
                        pixel_x,
                    ] = weights

        return AtlasPortraitFlameTriangleRasterization(
            image_width=normalized_width,
            image_height=normalized_height,
            coverage_mask=coverage_mask,
            triangle_index_buffer=triangle_index_buffer,
            depth_buffer=depth_buffer,
            barycentric_coordinates=(
                barycentric_coordinates
            ),
        )

    @classmethod
    def _calculate_barycentric_coordinates(
        cls,
        triangle: np.ndarray,
        *,
        x: float,
        y: float,
    ) -> np.ndarray | None:
        first = triangle[
            0
        ]
        second = triangle[
            1
        ]
        third = triangle[
            2
        ]

        denominator = (
            (
                second[
                    1
                ]
                - third[
                    1
                ]
            )
            * (
                first[
                    0
                ]
                - third[
                    0
                ]
            )
            + (
                third[
                    0
                ]
                - second[
                    0
                ]
            )
            * (
                first[
                    1
                ]
                - third[
                    1
                ]
            )
        )

        if abs(
            float(
                denominator
            )
        ) <= cls._EDGE_TOLERANCE:
            return None

        first_weight = (
            (
                second[
                    1
                ]
                - third[
                    1
                ]
            )
            * (
                x
                - third[
                    0
                ]
            )
            + (
                third[
                    0
                ]
                - second[
                    0
                ]
            )
            * (
                y
                - third[
                    1
                ]
            )
        ) / denominator

        second_weight = (
            (
                third[
                    1
                ]
                - first[
                    1
                ]
            )
            * (
                x
                - third[
                    0
                ]
            )
            + (
                first[
                    0
                ]
                - third[
                    0
                ]
            )
            * (
                y
                - third[
                    1
                ]
            )
        ) / denominator

        third_weight = (
            1.0
            - first_weight
            - second_weight
        )

        weights = np.array(
            [
                first_weight,
                second_weight,
                third_weight,
            ],
            dtype=np.float64,
        )

        if np.any(
            weights
            < -cls._EDGE_TOLERANCE
        ):
            return None

        weights = np.where(
            np.abs(
                weights
            )
            <= cls._EDGE_TOLERANCE,
            0.0,
            weights,
        )

        weight_sum = float(
            np.sum(
                weights,
                dtype=np.float64,
            )
        )

        if weight_sum <= 0.0:
            return None

        weights /= weight_sum

        return weights
