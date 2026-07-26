import math


class AtlasGalataBridgeParapetMesher:
    DEFAULT_WIDTH_MM = 0.45
    DEFAULT_HEIGHT_MM = 0.35

    @staticmethod
    def _resolve_frame(points):
        center_x = sum(
            point[0]
            for point in points
        ) / len(points)
        center_y = sum(
            point[1]
            for point in points
        ) / len(points)

        covariance_xx = sum(
            (point[0] - center_x) ** 2
            for point in points
        )
        covariance_yy = sum(
            (point[1] - center_y) ** 2
            for point in points
        )
        covariance_xy = sum(
            (point[0] - center_x)
            * (point[1] - center_y)
            for point in points
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
    def _longitudinal(point, frame):
        return (
            (point[0] - frame["center_x"])
            * frame["axis_x"]
            + (point[1] - frame["center_y"])
            * frame["axis_y"]
        )

    @staticmethod
    def _lateral(point, frame):
        return (
            (point[0] - frame["center_x"])
            * frame["normal_x"]
            + (point[1] - frame["center_y"])
            * frame["normal_y"]
        )

    @staticmethod
    def _ring_path(
        points,
        start_index,
        end_index,
        step,
    ):
        path = []
        index = start_index
        count = len(points)

        while True:
            path.append(points[index])

            if index == end_index:
                break

            index = (index + step) % count

        return tuple(path)

    @classmethod
    def _trim_transverse_end_segments(
        cls,
        path,
        frame,
    ):
        path = list(path)

        def is_transverse(first, second):
            delta_x = second[0] - first[0]
            delta_y = second[1] - first[1]

            longitudinal = abs(
                delta_x * frame["axis_x"]
                + delta_y * frame["axis_y"]
            )
            lateral = abs(
                delta_x * frame["normal_x"]
                + delta_y * frame["normal_y"]
            )

            return lateral > longitudinal

        while (
            len(path) > 2
            and is_transverse(path[0], path[1])
        ):
            path.pop(0)

        while (
            len(path) > 2
            and is_transverse(path[-2], path[-1])
        ):
            path.pop()

        if len(path) < 2:
            raise ValueError(
                "Parapet path disappeared while trimming bridge ends"
            )

        return tuple(path)

    @staticmethod
    def _remove_consecutive_duplicates(path):
        cleaned = []

        for point in path:
            if not cleaned:
                cleaned.append(point)
                continue

            previous = cleaned[-1]

            if (
                abs(point[0] - previous[0]) <= 1e-12
                and abs(point[1] - previous[1]) <= 1e-12
                and abs(point[2] - previous[2]) <= 1e-12
            ):
                continue

            cleaned.append(point)

        return tuple(cleaned)

    @classmethod
    def _resolve_side_paths(
        cls,
        deck_top,
    ):
        frame = cls._resolve_frame(deck_top)

        longitudinal = [
            cls._longitudinal(
                point,
                frame,
            )
            for point in deck_top
        ]

        start_index = min(
            range(len(deck_top)),
            key=lambda index: longitudinal[index],
        )
        end_index = max(
            range(len(deck_top)),
            key=lambda index: longitudinal[index],
        )

        first = cls._remove_consecutive_duplicates(
            cls._ring_path(
                deck_top,
                start_index,
                end_index,
                1,
            )
        )
        second = cls._remove_consecutive_duplicates(
            cls._ring_path(
                deck_top,
                start_index,
                end_index,
                -1,
            )
        )

        first = cls._trim_transverse_end_segments(
            path=first,
            frame=frame,
        )
        second = cls._trim_transverse_end_segments(
            path=second,
            frame=frame,
        )

        return frame, (first, second)

    @staticmethod
    def _append_quad(
        triangles,
        first,
        second,
        third,
        fourth,
        reverse=False,
    ):
        if reverse:
            triangles.extend(
                (
                    (first, third, second),
                    (first, fourth, third),
                )
            )
        else:
            triangles.extend(
                (
                    (first, second, third),
                    (first, third, fourth),
                )
            )

    @classmethod
    def _build_side(
        cls,
        path,
        frame,
        width_mm,
        height_mm,
    ):
        if len(path) < 2:
            raise ValueError(
                "Parapet side requires at least two points"
            )

        average_lateral = sum(
            cls._lateral(
                point,
                frame,
            )
            for point in path
        ) / len(path)

        side_sign = (
            1.0
            if average_lateral >= 0.0
            else -1.0
        )

        inward_x = (
            -side_sign
            * frame["normal_x"]
        )
        inward_y = (
            -side_sign
            * frame["normal_y"]
        )

        outer_bottom = tuple(path)

        inner_bottom = tuple(
            (
                x + inward_x * width_mm,
                y + inward_y * width_mm,
                z,
            )
            for x, y, z in outer_bottom
        )

        outer_top = tuple(
            (
                x,
                y,
                z + height_mm,
            )
            for x, y, z in outer_bottom
        )

        inner_top = tuple(
            (
                x,
                y,
                z + height_mm,
            )
            for x, y, z in inner_bottom
        )

        triangles = []

        for index in range(len(path) - 1):
            next_index = index + 1

            # Bottom face.
            cls._append_quad(
                triangles,
                outer_bottom[index],
                inner_bottom[index],
                inner_bottom[next_index],
                outer_bottom[next_index],
                reverse=True,
            )

            # Top face.
            cls._append_quad(
                triangles,
                outer_top[index],
                outer_top[next_index],
                inner_top[next_index],
                inner_top[index],
            )

            # Outer longitudinal wall.
            cls._append_quad(
                triangles,
                outer_bottom[index],
                outer_bottom[next_index],
                outer_top[next_index],
                outer_top[index],
            )

            # Inner longitudinal wall.
            cls._append_quad(
                triangles,
                inner_bottom[index],
                inner_top[index],
                inner_top[next_index],
                inner_bottom[next_index],
            )

        # Start cap.
        cls._append_quad(
            triangles,
            outer_bottom[0],
            outer_top[0],
            inner_top[0],
            inner_bottom[0],
        )

        # End cap.
        cls._append_quad(
            triangles,
            outer_bottom[-1],
            inner_bottom[-1],
            inner_top[-1],
            outer_top[-1],
        )

        return {
            "bottom": (
                outer_bottom
                + inner_bottom
            ),
            "top": (
                outer_top
                + inner_top
            ),
            "outer_bottom": outer_bottom,
            "inner_bottom": inner_bottom,
            "outer_top": outer_top,
            "inner_top": inner_top,
            "triangles": tuple(triangles),
            "width_mm": width_mm,
            "height_mm": height_mm,
        }

    @classmethod
    def build(
        cls,
        deck_top,
        width_mm=None,
        height_mm=None,
    ):
        deck_top = tuple(
            (
                float(x),
                float(y),
                float(z),
            )
            for x, y, z in deck_top
        )

        if len(deck_top) < 4:
            raise ValueError(
                "Galata parapets require at least 4 deck points"
            )

        width_mm = (
            cls.DEFAULT_WIDTH_MM
            if width_mm is None
            else float(width_mm)
        )
        height_mm = (
            cls.DEFAULT_HEIGHT_MM
            if height_mm is None
            else float(height_mm)
        )

        if width_mm <= 0.0:
            raise ValueError(
                "Parapet width must be greater than 0"
            )

        if height_mm <= 0.0:
            raise ValueError(
                "Parapet height must be greater than 0"
            )

        frame, side_paths = cls._resolve_side_paths(
            deck_top
        )

        return tuple(
            cls._build_side(
                path=path,
                frame=frame,
                width_mm=width_mm,
                height_mm=height_mm,
            )
            for path in side_paths
        )
