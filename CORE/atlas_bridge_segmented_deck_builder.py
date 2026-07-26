import math

from shapely.geometry import Polygon


class AtlasBridgeSegmentedDeckBuilder:
    """Bridge footprint'ini iki yaklaşım ve ana tabliye olarak böler."""

    _KINDS = (
        "start_approach",
        "main_deck",
        "end_approach",
    )

    @staticmethod
    def _resolve_axis(footprint):
        center_x = (
            sum(x for x, _ in footprint)
            / len(footprint)
        )
        center_y = (
            sum(y for _, y in footprint)
            / len(footprint)
        )

        covariance_xx = sum(
            (x - center_x) ** 2
            for x, _ in footprint
        )
        covariance_yy = sum(
            (y - center_y) ** 2
            for _, y in footprint
        )
        covariance_xy = sum(
            (x - center_x) * (y - center_y)
            for x, y in footprint
        )

        angle = 0.5 * math.atan2(
            2.0 * covariance_xy,
            covariance_xx - covariance_yy,
        )

        axis_x = math.cos(angle)
        axis_y = math.sin(angle)

        normal_x = -axis_y
        normal_y = axis_x

        return (
            center_x,
            center_y,
            axis_x,
            axis_y,
            normal_x,
            normal_y,
        )

    @staticmethod
    def _projection(
        point,
        center_x,
        center_y,
        axis_x,
        axis_y,
    ):
        x, y = point

        return (
            (x - center_x) * axis_x
            + (y - center_y) * axis_y
        )

    @staticmethod
    def _build_strip(
        lower_projection,
        upper_projection,
        center_x,
        center_y,
        axis_x,
        axis_y,
        normal_x,
        normal_y,
        half_width,
    ):
        def world(longitudinal, lateral):
            return (
                center_x
                + axis_x * longitudinal
                + normal_x * lateral,
                center_y
                + axis_y * longitudinal
                + normal_y * lateral,
            )

        return Polygon(
            (
                world(lower_projection, -half_width),
                world(upper_projection, -half_width),
                world(upper_projection, half_width),
                world(lower_projection, half_width),
            )
        )

    @staticmethod
    def _extract_single_polygon(geometry):
        if geometry.is_empty:
            raise ValueError(
                "Bridge section intersection is empty"
            )

        if geometry.geom_type == "Polygon":
            return geometry

        if geometry.geom_type == "MultiPolygon":
            non_empty = [
                polygon
                for polygon in geometry.geoms
                if polygon.area > 0.0
            ]

            if len(non_empty) == 1:
                return non_empty[0]

            raise ValueError(
                "Bridge section became disconnected"
            )

        raise ValueError(
            "Bridge section did not produce a polygon"
        )

    @classmethod
    def split(
        cls,
        footprint,
        approach_ratio,
    ):
        footprint = tuple(
            (float(x), float(y))
            for x, y in footprint
        )
        approach_ratio = float(approach_ratio)

        if len(footprint) < 3:
            raise ValueError(
                "Bridge footprint requires at least 3 points"
            )

        if not 0.0 < approach_ratio < 0.5:
            raise ValueError(
                "approach_ratio must be greater than 0 and less than 0.5"
            )

        polygon = Polygon(footprint)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or polygon.geom_type != "Polygon"
            or polygon.area <= 0.0
        ):
            raise ValueError(
                "Bridge footprint must form one valid polygon"
            )

        (
            center_x,
            center_y,
            axis_x,
            axis_y,
            normal_x,
            normal_y,
        ) = cls._resolve_axis(footprint)

        projections = tuple(
            cls._projection(
                point,
                center_x,
                center_y,
                axis_x,
                axis_y,
            )
            for point in footprint
        )

        minimum = min(projections)
        maximum = max(projections)
        span = maximum - minimum

        if span <= 1e-12:
            raise ValueError(
                "Bridge footprint has no longitudinal span"
            )

        normalized_bounds = (
            (0.0, approach_ratio),
            (approach_ratio, 1.0 - approach_ratio),
            (1.0 - approach_ratio, 1.0),
        )

        lateral_projections = tuple(
            (
                (x - center_x) * normal_x
                + (y - center_y) * normal_y
            )
            for x, y in footprint
        )

        lateral_span = (
            max(lateral_projections)
            - min(lateral_projections)
        )

        half_width = max(
            span,
            lateral_span,
            1.0,
        ) * 4.0

        sections = []

        for kind, bounds in zip(
            cls._KINDS,
            normalized_bounds,
        ):
            lower_ratio, upper_ratio = bounds

            lower_projection = (
                minimum + span * lower_ratio
            )
            upper_projection = (
                minimum + span * upper_ratio
            )

            strip = cls._build_strip(
                lower_projection=lower_projection,
                upper_projection=upper_projection,
                center_x=center_x,
                center_y=center_y,
                axis_x=axis_x,
                axis_y=axis_y,
                normal_x=normal_x,
                normal_y=normal_y,
                half_width=half_width,
            )

            section_polygon = cls._extract_single_polygon(
                polygon.intersection(strip)
            )

            section_footprint = tuple(
                (
                    float(x),
                    float(y),
                )
                for x, y in list(
                    section_polygon.exterior.coords
                )[:-1]
            )

            sections.append(
                {
                    "kind": kind,
                    "footprint": section_footprint,
                    "longitudinal_bounds": bounds,
                }
            )

        return tuple(sections)
