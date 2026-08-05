from __future__ import annotations

import math


class AtlasFacadeCircularPanelBuilder:
    DEFAULT_DEPTH_MM = 0.18
    DEFAULT_EMBED_MM = 0.04
    DEFAULT_SEGMENTS = 16

    @staticmethod
    def _length(vector):
        return math.sqrt(
            sum(
                float(value) ** 2
                for value in vector
            )
        )

    @staticmethod
    def _normalize(
        vector,
        *,
        error_message,
    ):
        length = (
            AtlasFacadeCircularPanelBuilder
            ._length(vector)
        )

        if length <= 1e-12:
            raise ValueError(
                error_message
            )

        return tuple(
            float(value) / length
            for value in vector
        )

    @classmethod
    def build(
        cls,
        *,
        wall_quad,
        center_u,
        center_v,
        diameter_ratio,
        depth_mm=None,
        embed_mm=None,
        segments=None,
        metadata=None,
    ):
        if (
            not wall_quad
            or len(wall_quad) != 4
        ):
            raise ValueError(
                "wall_quad must contain four points"
            )

        points = tuple(
            tuple(
                float(coordinate)
                for coordinate in point
            )
            for point in wall_quad
        )

        if any(
            len(point) != 3
            for point in points
        ):
            raise ValueError(
                "wall_quad points must be 3D"
            )

        center_u = float(center_u)
        center_v = float(center_v)
        diameter_ratio = float(
            diameter_ratio
        )

        if not 0.0 <= center_u <= 1.0:
            raise ValueError(
                "center_u must be in the range [0, 1]"
            )

        if not 0.0 <= center_v <= 1.0:
            raise ValueError(
                "center_v must be in the range [0, 1]"
            )

        if not 0.0 < diameter_ratio <= 1.0:
            raise ValueError(
                "diameter_ratio must be in "
                "the range (0, 1]"
            )

        if depth_mm is None:
            depth_mm = cls.DEFAULT_DEPTH_MM

        if embed_mm is None:
            embed_mm = cls.DEFAULT_EMBED_MM

        if segments is None:
            segments = cls.DEFAULT_SEGMENTS

        depth_mm = float(depth_mm)
        embed_mm = float(embed_mm)
        segments = int(segments)

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        if segments < 8:
            raise ValueError(
                "segments must be at least eight"
            )

        bottom_left = points[0]
        bottom_right = points[1]
        top_left = points[3]

        wall_u = tuple(
            bottom_right[axis]
            - bottom_left[axis]
            for axis in range(3)
        )
        wall_v = tuple(
            top_left[axis]
            - bottom_left[axis]
            for axis in range(3)
        )

        unit_u = cls._normalize(
            wall_u,
            error_message="wall_quad is degenerate",
        )
        unit_v = cls._normalize(
            wall_v,
            error_message="wall_quad is degenerate",
        )

        normal = (
            wall_u[1] * wall_v[2]
            - wall_u[2] * wall_v[1],
            wall_u[2] * wall_v[0]
            - wall_u[0] * wall_v[2],
            wall_u[0] * wall_v[1]
            - wall_u[1] * wall_v[0],
        )
        normal = cls._normalize(
            normal,
            error_message="wall_quad is degenerate",
        )

        wall_width = cls._length(
            wall_u
        )
        wall_height = cls._length(
            wall_v
        )
        radius = (
            min(
                wall_width,
                wall_height,
            )
            * diameter_ratio
            / 2.0
        )

        center = tuple(
            bottom_left[axis]
            + wall_u[axis] * center_u
            + wall_v[axis] * center_v
            for axis in range(3)
        )

        back_offset = -embed_mm
        front_offset = (
            depth_mm - embed_mm
        )

        def ring_point(
            angle,
            normal_offset,
        ):
            radial_u = (
                math.cos(angle) * radius
            )
            radial_v = (
                math.sin(angle) * radius
            )

            return tuple(
                center[axis]
                + unit_u[axis] * radial_u
                + unit_v[axis] * radial_v
                + normal[axis] * normal_offset
                for axis in range(3)
            )

        back_ring = tuple(
            ring_point(
                2.0
                * math.pi
                * index
                / segments,
                back_offset,
            )
            for index in range(segments)
        )
        front_ring = tuple(
            ring_point(
                2.0
                * math.pi
                * index
                / segments,
                front_offset,
            )
            for index in range(segments)
        )

        back_center = tuple(
            center[axis]
            + normal[axis] * back_offset
            for axis in range(3)
        )
        front_center = tuple(
            center[axis]
            + normal[axis] * front_offset
            for axis in range(3)
        )

        triangles = []

        for index in range(segments):
            next_index = (
                index + 1
            ) % segments

            triangles.extend(
                (
                    (
                        back_center,
                        back_ring[next_index],
                        back_ring[index],
                    ),
                    (
                        front_center,
                        front_ring[index],
                        front_ring[next_index],
                    ),
                    (
                        back_ring[index],
                        back_ring[next_index],
                        front_ring[next_index],
                    ),
                    (
                        back_ring[index],
                        front_ring[next_index],
                        front_ring[index],
                    ),
                )
            )

        result = {
            "type": "circular_facade_panel",
            "geometry_type": (
                "circular_facade_panel_prism"
            ),
            "triangles": triangles,
            "center": center,
            "back_center": back_center,
            "front_center": front_center,
            "back_ring": back_ring,
            "front_ring": front_ring,
            "diameter_ratio": diameter_ratio,
            "diameter": radius * 2.0,
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "segments": segments,
            "source_system": (
                "facade_circular_panel_builder"
            ),
        }

        if metadata:
            result.update(
                dict(metadata)
            )

        return result
