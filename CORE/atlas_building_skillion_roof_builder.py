"""
ATLAS Building Skillion Roof Builder v0.1

Normal binalar ve building:part eklentileri için tek eğimli
çatı geometrisi üretir.
"""

import math

from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasBuildingSkillionRoofBuilder:
    Z_TOLERANCE = 1e-7

    DEFAULT_ROOF_HEIGHT_RATIO = 0.20
    MIN_ROOF_HEIGHT_MM = 0.40
    MAX_INFERRED_ROOF_HEIGHT_MM = 3.00

    @staticmethod
    def apply(
        mesh,
        roof_height_m=None,
        roof_direction=None,
        coordinate_engine=None,
    ):
        if not mesh:
            return mesh

        if mesh.get("building_roof_profile") != "skillion":
            return mesh

        if mesh.get("is_castle_building") is True:
            return mesh

        ring = AtlasBuildingSkillionRoofBuilder._clean_ring(
            mesh.get("top", [])
        )

        if len(ring) < 3:
            return mesh

        body_top_z = mesh.get("top_z")

        if body_top_z is None:
            body_top_z = (
                AtlasBuildingSkillionRoofBuilder
                ._derive_z_level(
                    ring,
                    mode="max",
                )
            )

        bottom_z = mesh.get("bottom_z")

        if bottom_z is None:
            bottom_z = (
                AtlasBuildingSkillionRoofBuilder
                ._derive_z_level(
                    mesh.get("bottom", []),
                    mode="min",
                )
            )

        if body_top_z is None:
            return mesh

        roof_height_mm = (
            AtlasBuildingSkillionRoofBuilder
            ._resolve_roof_height_mm(
                roof_height_m=roof_height_m,
                coordinate_engine=coordinate_engine,
                ring=ring,
                body_top_z=float(body_top_z),
                bottom_z=bottom_z,
            )
        )

        if roof_height_mm <= 0.0:
            return mesh

        direction = (
            AtlasBuildingSkillionRoofBuilder
            ._resolve_direction_vector(
                roof_direction=roof_direction,
                ring=ring,
            )
        )

        if direction is None:
            return mesh

        projections = [
            point[0] * direction[0]
            + point[1] * direction[1]
            for point in ring
        ]

        projection_min = min(projections)
        projection_max = max(projections)
        projection_span = projection_max - projection_min

        if projection_span <= AtlasBuildingSkillionRoofBuilder.Z_TOLERANCE:
            return mesh

        roof_points = []

        for point, projection in zip(ring, projections):
            height_ratio = (
                projection - projection_min
            ) / projection_span

            roof_points.append(
                (
                    float(point[0]),
                    float(point[1]),
                    float(body_top_z)
                    + roof_height_mm * height_ratio,
                )
            )

        remaining_triangles = []
        removed_top_count = 0

        for triangle in mesh.get("triangles", []):
            if AtlasBuildingSkillionRoofBuilder._is_top_triangle(
                triangle=triangle,
                top_z=float(body_top_z),
            ):
                removed_top_count += 1
                continue

            remaining_triangles.append(triangle)

        if removed_top_count == 0:
            return mesh

        flat_ring = [
            (point[0], point[1])
            for point in ring
        ]

        flat_triangles = AtlasPolygonTriangulator.triangulate(
            flat_ring
        )

        if not flat_triangles:
            return mesh

        roof_point_by_xy = {
            (
                round(point[0], 9),
                round(point[1], 9),
            ): point
            for point in roof_points
        }

        roof_triangles = []

        for triangle in flat_triangles:
            mapped = []

            for point in triangle:
                key = (
                    round(float(point[0]), 9),
                    round(float(point[1]), 9),
                )

                roof_point = roof_point_by_xy.get(key)

                if roof_point is None:
                    return mesh

                mapped.append(roof_point)

            roof_triangles.append(tuple(mapped))

        side_triangles = []

        for index, base_point_1 in enumerate(ring):
            next_index = (index + 1) % len(ring)

            base_point_2 = ring[next_index]
            roof_point_1 = roof_points[index]
            roof_point_2 = roof_points[next_index]

            side_polygon = (
                AtlasBuildingSkillionRoofBuilder
                ._unique_points(
                    [
                        base_point_1,
                        base_point_2,
                        roof_point_2,
                        roof_point_1,
                    ]
                )
            )

            if len(side_polygon) == 3:
                side_triangles.append(
                    tuple(side_polygon)
                )
            elif len(side_polygon) == 4:
                side_triangles.extend(
                    [
                        (
                            side_polygon[0],
                            side_polygon[1],
                            side_polygon[2],
                        ),
                        (
                            side_polygon[0],
                            side_polygon[2],
                            side_polygon[3],
                        ),
                    ]
                )

        all_roof_triangles = [
            *roof_triangles,
            *side_triangles,
        ]

        mesh["triangles"] = [
            *remaining_triangles,
            *all_roof_triangles,
        ]

        mesh["body_top_z"] = float(body_top_z)
        mesh["roof_top_z"] = (
            float(body_top_z) + roof_height_mm
        )
        mesh["top_z"] = mesh["roof_top_z"]

        mesh["roof_height_mm"] = roof_height_mm
        mesh["roof_direction"] = (
            str(roof_direction).strip().lower()
            if roof_direction is not None
            else None
        )
        mesh["roof_geometry"] = "skillion"

        mesh["building_skillion_removed_top_triangles"] = (
            removed_top_count
        )
        mesh["building_skillion_roof_points"] = roof_points
        mesh["building_skillion_roof_triangles"] = (
            all_roof_triangles
        )
        mesh["building_flat_roof_triangles"] = []
        mesh["building_roof_triangles"] = all_roof_triangles
        mesh["building_skillion_roof_applied"] = True

        return mesh

    @staticmethod
    def _unique_points(points):
        unique = []

        for point in points:
            normalized = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if any(
                all(
                    abs(normalized[index] - existing[index])
                    <= AtlasBuildingSkillionRoofBuilder.Z_TOLERANCE
                    for index in range(3)
                )
                for existing in unique
            ):
                continue

            unique.append(normalized)

        return unique

    @staticmethod
    def _resolve_direction_vector(
        roof_direction,
        ring,
    ):
        normalized = (
            str(roof_direction).strip().lower()
            if roof_direction is not None
            else None
        )

        cardinal_vectors = {
            "north": (0.0, 1.0),
            "n": (0.0, 1.0),
            "south": (0.0, -1.0),
            "s": (0.0, -1.0),
            "east": (1.0, 0.0),
            "e": (1.0, 0.0),
            "west": (-1.0, 0.0),
            "w": (-1.0, 0.0),
        }

        if normalized in cardinal_vectors:
            return cardinal_vectors[normalized]

        if normalized is not None:
            try:
                degrees = float(normalized)
            except (TypeError, ValueError):
                degrees = None

            if degrees is not None and math.isfinite(degrees):
                radians = math.radians(degrees)

                return (
                    math.sin(radians),
                    math.cos(radians),
                )

        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]

        width = max(xs) - min(xs)
        depth = max(ys) - min(ys)

        if width <= 0.0 and depth <= 0.0:
            return None

        if width <= depth:
            return (1.0, 0.0)

        return (0.0, 1.0)

    @staticmethod
    def _resolve_roof_height_mm(
        roof_height_m,
        coordinate_engine,
        ring,
        body_top_z,
        bottom_z,
    ):
        parsed_height_m = (
            AtlasBuildingSkillionRoofBuilder
            ._parse_positive_float(roof_height_m)
        )

        if (
            parsed_height_m is not None
            and coordinate_engine is not None
        ):
            try:
                resolved = (
                    coordinate_engine.height_to_stl_mm(
                        parsed_height_m
                    )
                )
                resolved = float(resolved)
            except (AttributeError, TypeError, ValueError):
                resolved = None

            if (
                resolved is not None
                and math.isfinite(resolved)
                and resolved > 0.0
            ):
                return resolved

        xs = [point[0] for point in ring]
        ys = [point[1] for point in ring]

        short_span = min(
            max(xs) - min(xs),
            max(ys) - min(ys),
        )

        body_height = 0.0

        if bottom_z is not None:
            body_height = max(
                0.0,
                float(body_top_z) - float(bottom_z),
            )

        inferred = max(
            short_span
            * AtlasBuildingSkillionRoofBuilder
            .DEFAULT_ROOF_HEIGHT_RATIO,
            body_height
            * AtlasBuildingSkillionRoofBuilder
            .DEFAULT_ROOF_HEIGHT_RATIO,
            AtlasBuildingSkillionRoofBuilder
            .MIN_ROOF_HEIGHT_MM,
        )

        return min(
            inferred,
            AtlasBuildingSkillionRoofBuilder
            .MAX_INFERRED_ROOF_HEIGHT_MM,
        )

    @staticmethod
    def _parse_positive_float(value):
        if value is None:
            return None

        try:
            parsed = float(
                str(value)
                .strip()
                .lower()
                .replace("meters", "")
                .replace("meter", "")
                .replace("metres", "")
                .replace("metre", "")
                .replace("m", "")
                .strip()
            )
        except (TypeError, ValueError):
            return None

        if parsed <= 0.0:
            return None

        return parsed

    @staticmethod
    def _clean_ring(points):
        cleaned = []

        for point in points:
            if len(point) < 3:
                continue

            normalized = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if cleaned and normalized == cleaned[-1]:
                continue

            cleaned.append(normalized)

        if (
            len(cleaned) > 1
            and cleaned[0] == cleaned[-1]
        ):
            cleaned.pop()

        return cleaned

    @staticmethod
    def _derive_z_level(points, mode):
        values = []

        for point in points:
            if len(point) < 3:
                continue

            try:
                value = float(point[2])
            except (TypeError, ValueError):
                continue

            if math.isfinite(value):
                values.append(value)

        if not values:
            return None

        return max(values) if mode == "max" else min(values)

    @staticmethod
    def _is_top_triangle(
        triangle,
        top_z,
    ):
        if len(triangle) != 3:
            return False

        return all(
            len(point) >= 3
            and abs(float(point[2]) - top_z)
            <= AtlasBuildingSkillionRoofBuilder.Z_TOLERANCE
            for point in triangle
        )
