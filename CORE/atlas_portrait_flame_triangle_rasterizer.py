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

    Background pixels contain triangle index -1 and positive
    infinite depth.
    """

    image_width: int
    image_height: int
    coverage_mask: np.ndarray
    triangle_index_buffer: np.ndarray
    depth_buffer: np.ndarray

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
        }

    @staticmethod
    def _normalize_dimension(
        value: Any,
        *,
        name: str,
    ) -> int:
        if isinstance(
            value,
            bool,
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

    This rasterizer performs no viewport transformation, perspective
    correction, interpolated vertex depth, shading, or preview export.
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

        coverage_mask = np.zeros(
            (
                normalized_height,
                normalized_width,
            ),
            dtype=np.bool_,
        )
        triangle_index_buffer = np.full(
            (
                normalized_height,
                normalized_width,
            ),
            -1,
            dtype=np.int64,
        )
        depth_buffer = np.full(
            (
                normalized_height,
                normalized_width,
            ),
            np.inf,
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
                    if not cls._contains_point(
                        triangle,
                        x=float(
                            pixel_x
                        ),
                        y=float(
                            pixel_y
                        ),
                    ):
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

        return AtlasPortraitFlameTriangleRasterization(
            image_width=normalized_width,
            image_height=normalized_height,
            coverage_mask=coverage_mask,
            triangle_index_buffer=triangle_index_buffer,
            depth_buffer=depth_buffer,
        )

    @classmethod
    def _contains_point(
        cls,
        triangle: np.ndarray,
        *,
        x: float,
        y: float,
    ) -> bool:
        first = triangle[
            0
        ]
        second = triangle[
            1
        ]
        third = triangle[
            2
        ]

        first_edge = cls._signed_edge(
            first,
            second,
            x=x,
            y=y,
        )
        second_edge = cls._signed_edge(
            second,
            third,
            x=x,
            y=y,
        )
        third_edge = cls._signed_edge(
            third,
            first,
            x=x,
            y=y,
        )

        return (
            first_edge >= -cls._EDGE_TOLERANCE
            and second_edge >= -cls._EDGE_TOLERANCE
            and third_edge >= -cls._EDGE_TOLERANCE
        )

    @staticmethod
    def _signed_edge(
        start: np.ndarray,
        end: np.ndarray,
        *,
        x: float,
        y: float,
    ) -> float:
        return float(
            (
                end[
                    0
                ]
                - start[
                    0
                ]
            )
            * (
                y
                - start[
                    1
                ]
            )
            - (
                end[
                    1
                ]
                - start[
                    1
                ]
            )
            * (
                x
                - start[
                    0
                ]
            )
        )
