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

    footprint: tuple[
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

        return points

    @staticmethod
    def _resolve_principal_axis(
        points,
    ):
        mean_x = sum(
            x
            for x, _ in points
        ) / len(points)
        mean_y = sum(
            y
            for _, y in points
        ) / len(points)

        covariance_xx = sum(
            (x - mean_x) ** 2
            for x, _ in points
        )
        covariance_yy = sum(
            (y - mean_y) ** 2
            for _, y in points
        )
        covariance_xy = sum(
            (x - mean_x)
            * (y - mean_y)
            for x, y in points
        )

        if (
            covariance_xx <= 1e-24
            and covariance_yy <= 1e-24
        ):
            raise ValueError(
                "Church footprint has no measurable span"
            )

        angle = 0.5 * math.atan2(
            2.0 * covariance_xy,
            covariance_xx - covariance_yy,
        )

        first_axis = (
            math.cos(angle),
            math.sin(angle),
        )
        second_axis = (
            -first_axis[1],
            first_axis[0],
        )

        def span(axis):
            projections = tuple(
                x * axis[0]
                + y * axis[1]
                for x, y in points
            )

            return (
                max(projections)
                - min(projections)
            )

        first_span = span(first_axis)
        second_span = span(second_axis)

        if second_span > first_span:
            return second_axis

        return first_axis

    @classmethod
    def resolve(
        cls,
        footprint,
    ) -> AtlasChurchFootprintFrame:
        points = cls._normalize_footprint(
            footprint
        )

        axis_x, axis_y = (
            cls._resolve_principal_axis(
                points
            )
        )

        axis_length = math.hypot(
            axis_x,
            axis_y,
        )

        if axis_length <= 1e-12:
            raise ValueError(
                "Church footprint has no longitudinal axis"
            )

        axis_x /= axis_length
        axis_y /= axis_length

        normal_x = -axis_y
        normal_y = axis_x

        longitudinal_values = tuple(
            x * axis_x
            + y * axis_y
            for x, y in points
        )
        lateral_values = tuple(
            x * normal_x
            + y * normal_y
            for x, y in points
        )

        minimum_longitudinal = min(
            longitudinal_values
        )
        maximum_longitudinal = max(
            longitudinal_values
        )
        minimum_lateral = min(
            lateral_values
        )
        maximum_lateral = max(
            lateral_values
        )

        longitudinal_span = (
            maximum_longitudinal
            - minimum_longitudinal
        )
        lateral_span = (
            maximum_lateral
            - minimum_lateral
        )

        if longitudinal_span <= 1e-12:
            raise ValueError(
                "Church footprint has no longitudinal span"
            )

        if lateral_span <= 1e-12:
            raise ValueError(
                "Church footprint has no lateral span"
            )

        center_longitudinal = (
            minimum_longitudinal
            + maximum_longitudinal
        ) / 2.0
        center_lateral = (
            minimum_lateral
            + maximum_lateral
        ) / 2.0

        center_x = (
            center_longitudinal * axis_x
            + center_lateral * normal_x
        )
        center_y = (
            center_longitudinal * axis_y
            + center_lateral * normal_y
        )

        half_longitudinal = (
            longitudinal_span / 2.0
        )
        half_lateral = (
            lateral_span / 2.0
        )

        def world(
            longitudinal,
            lateral,
        ):
            return (
                center_x
                + longitudinal * axis_x
                + lateral * normal_x,
                center_y
                + longitudinal * axis_y
                + lateral * normal_y,
            )

        oriented_rectangle = (
            world(
                -half_longitudinal,
                -half_lateral,
            ),
            world(
                half_longitudinal,
                -half_lateral,
            ),
            world(
                half_longitudinal,
                half_lateral,
            ),
            world(
                -half_longitudinal,
                half_lateral,
            ),
        )

        return AtlasChurchFootprintFrame(
            center_x=float(center_x),
            center_y=float(center_y),
            axis_x=float(axis_x),
            axis_y=float(axis_y),
            normal_x=float(normal_x),
            normal_y=float(normal_y),
            longitudinal_span=float(
                longitudinal_span
            ),
            lateral_span=float(
                lateral_span
            ),
            oriented_rectangle=tuple(
                (
                    float(x),
                    float(y),
                )
                for x, y in oriented_rectangle
            ),
            footprint=tuple(
                (
                    float(x),
                    float(y),
                )
                for x, y in points
            ),
        )
