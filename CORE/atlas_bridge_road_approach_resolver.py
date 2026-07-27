import math


class AtlasBridgeRoadApproachResolver:
    @staticmethod
    def _resolve_frame(deck_top):
        center_x = sum(
            point[0]
            for point in deck_top
        ) / len(deck_top)
        center_y = sum(
            point[1]
            for point in deck_top
        ) / len(deck_top)

        covariance_xx = sum(
            (point[0] - center_x) ** 2
            for point in deck_top
        )
        covariance_yy = sum(
            (point[1] - center_y) ** 2
            for point in deck_top
        )
        covariance_xy = sum(
            (point[0] - center_x)
            * (point[1] - center_y)
            for point in deck_top
        )

        angle = 0.5 * math.atan2(
            2.0 * covariance_xy,
            covariance_xx - covariance_yy,
        )

        axis_x = math.cos(angle)
        axis_y = math.sin(angle)

        return {
            "center_x": center_x,
            "center_y": center_y,
            "axis_x": axis_x,
            "axis_y": axis_y,
            "normal_x": -axis_y,
            "normal_y": axis_x,
        }

    @staticmethod
    def _projection(point, frame):
        return (
            (point[0] - frame["center_x"])
            * frame["axis_x"]
            + (point[1] - frame["center_y"])
            * frame["axis_y"]
        )

    @staticmethod
    def _edge_record(first, second, frame):
        midpoint = (
            (first[0] + second[0]) / 2.0,
            (first[1] + second[1]) / 2.0,
        )

        delta_x = second[0] - first[0]
        delta_y = second[1] - first[1]

        longitudinal_length = abs(
            delta_x * frame["axis_x"]
            + delta_y * frame["axis_y"]
        )
        lateral_length = abs(
            delta_x * frame["normal_x"]
            + delta_y * frame["normal_y"]
        )

        return {
            "first": first,
            "second": second,
            "projection": (
                AtlasBridgeRoadApproachResolver
                ._projection(
                    midpoint,
                    frame,
                )
            ),
            "longitudinal_length": longitudinal_length,
            "lateral_length": lateral_length,
        }

    @classmethod
    def resolve(cls, deck_top):
        deck_top = tuple(
            (
                float(x),
                float(y),
                float(z),
            )
            for x, y, z in deck_top
        )

        if len(deck_top) < 3:
            raise ValueError(
                "Bridge deck requires at least three points"
            )

        frame = cls._resolve_frame(deck_top)

        longitudinal = tuple(
            cls._projection(
                point,
                frame,
            )
            for point in deck_top
        )

        minimum = min(longitudinal)
        maximum = max(longitudinal)
        span = maximum - minimum

        if span <= 1e-12:
            raise ValueError(
                "Bridge deck has no longitudinal span"
            )

        end_tolerance = max(
            0.25,
            span * 0.02,
        )

        first_points = tuple(
            point
            for point, value in zip(
                deck_top,
                longitudinal,
            )
            if value <= minimum + end_tolerance
        )

        second_points = tuple(
            point
            for point, value in zip(
                deck_top,
                longitudinal,
            )
            if value >= maximum - end_tolerance
        )

        if (
            len(first_points) < 2
            or len(second_points) < 2
        ):
            raise ValueError(
                "Could not resolve complete bridge end edges"
            )

        def lateral(point):
            return (
                (point[0] - frame["center_x"])
                * frame["normal_x"]
                + (point[1] - frame["center_y"])
                * frame["normal_y"]
            )

        first_high = max(
            first_points,
            key=lateral,
        )
        first_low = min(
            first_points,
            key=lateral,
        )

        second_low = min(
            second_points,
            key=lateral,
        )
        second_high = max(
            second_points,
            key=lateral,
        )

        def xy(point):
            return (
                point[0],
                point[1],
            )

        def average_z(points):
            return sum(
                point[2]
                for point in points
            ) / len(points)

        return (
            {
                "start_edge": (
                    xy(first_high),
                    xy(first_low),
                ),
                "outward_axis": (
                    -frame["axis_x"],
                    -frame["axis_y"],
                ),
                "bridge_top_z": average_z(
                    first_points
                ),
                "longitudinal_projection": minimum,
                "end_point_count": len(
                    first_points
                ),
            },
            {
                "start_edge": (
                    xy(second_low),
                    xy(second_high),
                ),
                "outward_axis": (
                    frame["axis_x"],
                    frame["axis_y"],
                ),
                "bridge_top_z": average_z(
                    second_points
                ),
                "longitudinal_projection": maximum,
                "end_point_count": len(
                    second_points
                ),
            },
        )
