from __future__ import annotations

import re

from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)
from CORE.atlas_worship_grammar_resolver import (
    AtlasWorshipGrammarResolver,
)


class AtlasWorshipLandmarkFallbackMesher:
    DEFAULT_HEIGHTS_M = {
        AtlasLandmarkType.MOSQUE: 18.0,
        AtlasLandmarkType.SYNAGOGUE: 16.0,
    }

    PROFILE_NAMES = {
        AtlasLandmarkType.MOSQUE: "mosque",
        AtlasLandmarkType.SYNAGOGUE: "synagogue",
    }

    @staticmethod
    def _read_positive_metres(value):
        if value is None:
            return None

        normalized = str(value).strip()

        match = re.fullmatch(
            r"""
            ([+]?
            (?:\d+(?:\.\d*)?|\.\d+)
            (?:[eE][+-]?\d+)?)
            \s*(?:m)?
            """,
            normalized,
            flags=re.VERBOSE | re.IGNORECASE,
        )

        if match is None:
            return None

        result = float(match.group(1))

        if result <= 0.0:
            return None

        return result

    @staticmethod
    def _normalize_footprint(geometry):
        exterior = getattr(
            geometry,
            "exterior",
            geometry,
        )
        coordinates = getattr(
            exterior,
            "coords",
            exterior,
        )

        footprint = tuple(
            (
                float(point[0]),
                float(point[1]),
            )
            for point in coordinates
        )

        if (
            len(footprint) > 1
            and footprint[0] == footprint[-1]
        ):
            footprint = footprint[:-1]

        if len(footprint) < 3:
            raise ValueError(
                "Worship landmark fallback requires "
                "at least three footprint points"
            )

        return footprint

    @staticmethod
    def _signed_area(footprint):
        return sum(
            (
                footprint[index][0]
                * footprint[(index + 1) % len(footprint)][1]
                - footprint[(index + 1) % len(footprint)][0]
                * footprint[index][1]
            )
            for index in range(len(footprint))
        ) / 2.0

    @classmethod
    def build(cls, landmark):
        landmark_type = landmark.landmark_type

        if landmark_type not in cls.DEFAULT_HEIGHTS_M:
            raise ValueError(
                "Worship fallback supports only mosque "
                "and synagogue landmarks"
            )

        footprint = cls._normalize_footprint(
            landmark.geometry
        )

        tags = getattr(
            landmark,
            "tags",
            {},
        ) or {}

        height_m = cls._read_positive_metres(
            tags.get("height")
        )

        if height_m is None:
            height_m = cls.DEFAULT_HEIGHTS_M[
                landmark_type
            ]

        bottom_z = 0.0
        top_z = float(height_m)

        minimum_x = min(
            point[0]
            for point in footprint
        )
        minimum_y = min(
            point[1]
            for point in footprint
        )
        span_x = (
            max(point[0] for point in footprint)
            - minimum_x
        )
        span_y = (
            max(point[1] for point in footprint)
            - minimum_y
        )
        normalization_scale = max(
            span_x,
            span_y,
        )

        if normalization_scale <= 1e-15:
            raise ValueError(
                "Worship landmark footprint has no span"
            )

        normalized_footprint = tuple(
            (
                (x - minimum_x)
                / normalization_scale,
                (y - minimum_y)
                / normalization_scale,
            )
            for x, y in footprint
        )

        surface_triangles = tuple(
            tuple(
                (
                    minimum_x
                    + normalized_x
                    * normalization_scale,
                    minimum_y
                    + normalized_y
                    * normalization_scale,
                )
                for normalized_x, normalized_y
                in triangle
            )
            for triangle in (
                AtlasPolygonTriangulator.triangulate(
                    normalized_footprint
                )
            )
        )

        if not surface_triangles:
            raise ValueError(
                "Worship landmark footprint "
                "triangulation produced no surface"
            )

        bottom = tuple(
            (
                x,
                y,
                bottom_z,
            )
            for x, y in footprint
        )
        top = tuple(
            (
                x,
                y,
                top_z,
            )
            for x, y in footprint
        )

        triangles = []

        for surface_triangle in surface_triangles:
            bottom_triangle = tuple(
                (
                    x,
                    y,
                    bottom_z,
                )
                for x, y in surface_triangle
            )
            top_triangle = tuple(
                (
                    x,
                    y,
                    top_z,
                )
                for x, y in surface_triangle
            )

            triangles.append(
                (
                    bottom_triangle[0],
                    bottom_triangle[2],
                    bottom_triangle[1],
                )
            )
            triangles.append(
                (
                    top_triangle[0],
                    top_triangle[1],
                    top_triangle[2],
                )
            )

        counterclockwise = (
            cls._signed_area(footprint) > 0.0
        )
        walls = []

        for index in range(len(footprint)):
            next_index = (
                index + 1
            ) % len(footprint)

            first_bottom = bottom[index]
            second_bottom = bottom[next_index]
            first_top = top[index]
            second_top = top[next_index]

            walls.append(
                (
                    first_bottom,
                    second_bottom,
                    second_top,
                    first_top,
                )
            )

            if counterclockwise:
                triangles.extend(
                    (
                        (
                            first_bottom,
                            second_bottom,
                            second_top,
                        ),
                        (
                            first_bottom,
                            second_top,
                            first_top,
                        ),
                    )
                )
            else:
                triangles.extend(
                    (
                        (
                            first_bottom,
                            second_top,
                            second_bottom,
                        ),
                        (
                            first_bottom,
                            first_top,
                            second_top,
                        ),
                    )
                )

        worship_grammar = (
            AtlasWorshipGrammarResolver.resolve(
                landmark
            )
        )

        if worship_grammar != "footprint_fallback":
            raise ValueError(
                f"worship grammar {worship_grammar!r} "
                "is not implemented"
            )

        return {
            "type": "worship_landmark_fallback",
            "landmark_id": int(landmark.id),
            "worship_profile": cls.PROFILE_NAMES[
                landmark_type
            ],
            "worship_grammar": worship_grammar,
            "uses_real_footprint": True,
            "special_architecture_applied": False,
            "height_m": height_m,
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "footprint": footprint,
            "min_z": bottom_z,
            "max_z": top_z,
            "top_z": top_z,
        }
