from __future__ import annotations

from dataclasses import dataclass
import math

from shapely.geometry import Polygon


@dataclass(frozen=True, slots=True)
class AtlasChurchFootprintFrame:
    center_x: float
    center_y: float

    axis_x: float
    axis_y: float

    normal_x: float
    normal_y: float

    longitudinal_span: float
    lateral_span: float

    oriented_rectangle: tuple[
        tuple[float, float],
        ...,
    ]

    def to_world(
        self,
        *,
        longitudinal,
        lateral,
    ):
        longitudinal = float(longitudinal)
        lateral = float(lateral)

        return (
            self.center_x
            + longitudinal * self.axis_x
            + lateral * self.normal_x,
            self.center_y
            + longitudinal * self.axis_y
            + lateral * self.normal_y,
        )

    def to_local(
        self,
        point,
    ):
        x = float(point[0])
        y = float(point[1])

        offset_x = x - self.center_x
        offset_y = y - self.center_y

        return (
            offset_x * self.axis_x
            + offset_y * self.axis_y,
            offset_x * self.normal_x
            + offset_y * self.normal_y,
        )


class AtlasChurchFootprintResolver:
    @staticmethod
    def _normalize_footprint(
        footprint,
    ):
        points = tuple(
            (
                float(point[0]),
                float(point[1]),
            )
            for point in footprint
        )

        if (
            len(points) > 1
            and points[0] == points[-1]
        ):
            points = points[:-1]

        if len(points) < 3:
            raise ValueError(
                "Church footprint requires at least three points"
            )

        polygon = Polygon(points)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.area <= 1e-12
        ):
            raise ValueError(
                "Church footprint must define a valid area"
            )

        return points, polygon

    @classmethod
    def resolve(
        cls,
        footprint,
    ) -> AtlasChurchFootprintFrame:
        _, polygon = cls._normalize_footprint(
            footprint
        )

        rectangle = (
            polygon.minimum_rotated_rectangle
        )

        rectangle_points = tuple(
            (
                float(x),
                float(y),
            )
            for x, y in tuple(
                rectangle.exterior.coords
            )[:-1]
        )

        if len(rectangle_points) != 4:
            raise ValueError(
                "Could not resolve oriented church rectangle"
            )

        center = rectangle.centroid
        center_x = float(center.x)
        center_y = float(center.y)

        edges = []

        for index in range(4):
            first = rectangle_points[index]
            second = rectangle_points[
                (index + 1) % 4
            ]

            delta_x = second[0] - first[0]
            delta_y = second[1] - first[1]

            length = math.hypot(
                delta_x,
                delta_y,
            )

            edges.append(
                {
                    "delta_x": delta_x,
                    "delta_y": delta_y,
                    "length": length,
                }
            )

        longitudinal_edge = max(
            edges,
            key=lambda edge: edge["length"],
        )

        longitudinal_span = float(
            longitudinal_edge["length"]
        )

        if longitudinal_span <= 1e-12:
            raise ValueError(
                "Church footprint has no longitudinal span"
            )

        axis_x = (
            longitudinal_edge["delta_x"]
            / longitudinal_span
        )
        axis_y = (
            longitudinal_edge["delta_y"]
            / longitudinal_span
        )

        normal_x = -axis_y
        normal_y = axis_x

        local_points = tuple(
            (
                (
                    (x - center_x) * axis_x
                    + (y - center_y) * axis_y
                ),
                (
                    (x - center_x) * normal_x
                    + (y - center_y) * normal_y
                ),
            )
            for x, y in rectangle_points
        )

        longitudinal_values = tuple(
            point[0]
            for point in local_points
        )
        lateral_values = tuple(
            point[1]
            for point in local_points
        )

        resolved_longitudinal_span = (
            max(longitudinal_values)
            - min(longitudinal_values)
        )
        lateral_span = (
            max(lateral_values)
            - min(lateral_values)
        )

        if lateral_span <= 1e-12:
            raise ValueError(
                "Church footprint has no lateral span"
            )

        return AtlasChurchFootprintFrame(
            center_x=center_x,
            center_y=center_y,
            axis_x=axis_x,
            axis_y=axis_y,
            normal_x=normal_x,
            normal_y=normal_y,
            longitudinal_span=float(
                resolved_longitudinal_span
            ),
            lateral_span=float(
                lateral_span
            ),
            oriented_rectangle=rectangle_points,
        )
