import math


class AtlasTreeRowContextResolver:
    PARALLEL_COSINE_THRESHOLD = 0.95
    MAX_ADJACENT_DISTANCE_M = 20.0

    @staticmethod
    def _vector_meters(start, end):
        lat1, lon1 = start
        lat2, lon2 = end

        mean_lat = math.radians(
            (float(lat1) + float(lat2)) / 2.0
        )

        meters_per_degree_lat = 111_320.0
        meters_per_degree_lon = (
            111_320.0 * math.cos(mean_lat)
        )

        return (
            (float(lon2) - float(lon1))
            * meters_per_degree_lon,
            (float(lat2) - float(lat1))
            * meters_per_degree_lat,
        )

    @staticmethod
    def _midpoint(geometry):
        first = geometry[0]
        last = geometry[-1]

        return (
            (float(first[0]) + float(last[0])) / 2.0,
            (float(first[1]) + float(last[1])) / 2.0,
        )

    @classmethod
    def _distance_meters(cls, a, b):
        east_m, north_m = cls._vector_meters(
            a,
            b,
        )

        return math.hypot(
            east_m,
            north_m,
        )

    @classmethod
    def _direction_cosine(
        cls,
        geometry_a,
        geometry_b,
    ):
        ax, ay = cls._vector_meters(
            geometry_a[0],
            geometry_a[-1],
        )
        bx, by = cls._vector_meters(
            geometry_b[0],
            geometry_b[-1],
        )

        a_length = math.hypot(ax, ay)
        b_length = math.hypot(bx, by)

        if a_length <= 0.0 or b_length <= 0.0:
            return 0.0

        return abs(
            (ax * bx + ay * by)
            / (a_length * b_length)
        )

    @classmethod
    def resolve(
        cls,
        *,
        row_profile,
        roads,
        pedestrian_paths,
    ):
        row_geometry = tuple(
            row_profile.get(
                "source_geometry",
                (),
            )
        )

        if len(row_geometry) < 2:
            raise ValueError(
                "row_profile source_geometry must contain "
                "at least two points"
            )

        candidates = []

        for feature_type, features in (
            ("road", roads or ()),
            (
                "pedestrian_path",
                pedestrian_paths or (),
            ),
        ):
            for feature in features:
                geometry = tuple(
                    feature.get(
                        "geometry",
                        (),
                    )
                )

                if len(geometry) < 2:
                    continue

                distance_m = cls._distance_meters(
                    cls._midpoint(row_geometry),
                    cls._midpoint(geometry),
                )

                cosine = cls._direction_cosine(
                    row_geometry,
                    geometry,
                )

                if (
                    distance_m
                    > cls.MAX_ADJACENT_DISTANCE_M
                ):
                    continue

                if (
                    cosine
                    < cls.PARALLEL_COSINE_THRESHOLD
                ):
                    continue

                candidates.append(
                    (
                        distance_m,
                        str(feature.get("id")),
                        feature_type,
                        feature,
                        cosine,
                    )
                )

        if not candidates:
            return {
                "adjacent_feature_type": None,
                "adjacent_feature_id": None,
                "relationship": None,
                "distance_m": None,
                "direction_cosine": None,
            }

        (
            distance_m,
            _,
            feature_type,
            feature,
            cosine,
        ) = min(candidates)

        return {
            "adjacent_feature_type": feature_type,
            "adjacent_feature_id": feature.get("id"),
            "relationship": "parallel",
            "distance_m": distance_m,
            "direction_cosine": cosine,
        }
