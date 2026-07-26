import math


class AtlasGalataBridgeSupportResolver:
    """Galata footprint'indeki dört yan platformun merkezlerini çözer."""

    MIN_CLUSTER_DISTANCE_RATIO = 0.12
    SUPPORT_CENTER_INSET_MM = 2.0
    DEFAULT_SUPPORT_WIDTH = 2.0
    DEFAULT_SUPPORT_DEPTH = 3.0

    @staticmethod
    def _resolve_frame(footprint):
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

        return {
            "center_x": center_x,
            "center_y": center_y,
            "axis_x": axis_x,
            "axis_y": axis_y,
            "normal_x": normal_x,
            "normal_y": normal_y,
        }

    @staticmethod
    def _build_records(
        footprint,
        frame,
    ):
        records = []

        for x, y in footprint:
            longitudinal = (
                (x - frame["center_x"])
                * frame["axis_x"]
                + (y - frame["center_y"])
                * frame["axis_y"]
            )

            lateral = (
                (x - frame["center_x"])
                * frame["normal_x"]
                + (y - frame["center_y"])
                * frame["normal_y"]
            )

            records.append(
                {
                    "x": x,
                    "y": y,
                    "longitudinal": longitudinal,
                    "lateral": lateral,
                }
            )

        minimum = min(
            record["longitudinal"]
            for record in records
        )
        maximum = max(
            record["longitudinal"]
            for record in records
        )
        span = maximum - minimum

        if span <= 1e-12:
            raise ValueError(
                "Bridge footprint has no longitudinal span"
            )

        for record in records:
            record["position"] = (
                record["longitudinal"] - minimum
            ) / span

        return records

    @classmethod
    def _select_side_supports(
        cls,
        records,
        side,
        frame,
    ):
        if side == "positive":
            candidates = [
                record
                for record in records
                if record["lateral"] > 0.0
            ]
        else:
            candidates = [
                record
                for record in records
                if record["lateral"] < 0.0
            ]

        candidates.sort(
            key=lambda record: abs(
                record["lateral"]
            ),
            reverse=True,
        )

        selected = []

        for candidate in candidates:
            if any(
                abs(
                    candidate["position"]
                    - existing["position"]
                )
                < cls.MIN_CLUSTER_DISTANCE_RATIO
                for existing in selected
            ):
                continue

            selected.append(candidate)

            if len(selected) == 2:
                break

        if len(selected) != 2:
            raise ValueError(
                f"Could not resolve two {side} support regions"
            )

        resolved = []

        for record in selected:
            lateral_sign = (
                1.0
                if record["lateral"] > 0.0
                else -1.0
            )

            inset_x = (
                record["x"]
                - lateral_sign
                * cls.SUPPORT_CENTER_INSET_MM
                * frame["normal_x"]
            )
            inset_y = (
                record["y"]
                - lateral_sign
                * cls.SUPPORT_CENTER_INSET_MM
                * frame["normal_y"]
            )

            resolved.append(
                {
                    "side": side,
                    "center": (
                        float(inset_x),
                        float(inset_y),
                    ),
                    "longitudinal_position": float(
                        record["position"]
                    ),
                    "lateral_offset": float(
                        record["lateral"]
                        - lateral_sign
                        * cls.SUPPORT_CENTER_INSET_MM
                    ),
                    "support_width": (
                        cls.DEFAULT_SUPPORT_WIDTH
                    ),
                    "support_depth": (
                        cls.DEFAULT_SUPPORT_DEPTH
                    ),
                }
            )

        return resolved

    @classmethod
    def resolve(
        cls,
        footprint,
    ):
        footprint = tuple(
            (float(x), float(y))
            for x, y in footprint
        )

        if len(footprint) < 4:
            raise ValueError(
                "Galata bridge footprint requires at least 4 points"
            )

        frame = cls._resolve_frame(footprint)

        records = cls._build_records(
            footprint=footprint,
            frame=frame,
        )

        supports = []

        supports.extend(
            cls._select_side_supports(
                records=records,
                side="positive",
                frame=frame,
            )
        )
        supports.extend(
            cls._select_side_supports(
                records=records,
                side="negative",
                frame=frame,
            )
        )

        supports.sort(
            key=lambda support: (
                support["longitudinal_position"],
                support["side"],
            )
        )

        return tuple(supports)
