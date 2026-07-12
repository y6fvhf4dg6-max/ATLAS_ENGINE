"""
ATLAS Castle Roof Builder v0.2

Kale kulelerinin düz üst kapaklarını kaldırır ve aynı sınır
üzerinden manifold sivri çatı yüzeyi üretir.

Temel kurallar:
- Çok sayıda footprint noktası otomatik olarak yuvarlak kule sayılmaz
- Kale kulelerinde varsayılan form çokgen/piramidal sivri çatıdır
- Gerçek dairesel kule desteği daha sonra açık semantik veya
  güvenilir dairesellik analiziyle etkinleştirilecektir
- Minare ve normal bina çatıları bu modülün kapsamı dışındadır
"""


class AtlasCastleRoofBuilder:
    POINT_PRECISION = 9
    Z_TOLERANCE = 1e-7
    COLLINEAR_TOLERANCE = 1e-7

    SUPPORTED_PROFILES = {
        "main_tower",
        "defensive_tower",
        "gate_tower",
    }

    ROOF_BODY_HEIGHT_RATIO = {
        "main_tower": 0.38,
        "defensive_tower": 0.32,
        "gate_tower": 0.28,
    }

    ROOF_WIDTH_MIN_RATIO = {
        "main_tower": 0.42,
        "defensive_tower": 0.34,
        "gate_tower": 0.30,
    }

    ROOF_WIDTH_MAX_RATIO = {
        "main_tower": 0.82,
        "defensive_tower": 0.70,
        "gate_tower": 0.62,
    }

    ROOF_BODY_MAX_RATIO = {
        "main_tower": 0.70,
        "defensive_tower": 0.62,
        "gate_tower": 0.56,
    }

    ROOF_SLENDERNESS_TARGET = {
        "main_tower": 1.05,
        "defensive_tower": 0.95,
        "gate_tower": 0.85,
    }

    MIN_ROOF_HEIGHT_MM = 0.60
    MAX_ROOF_HEIGHT_MM = 4.50

    @staticmethod
    def apply(
        mesh,
        castle_profile,
    ):
        if not mesh:
            return mesh

        if castle_profile not in AtlasCastleRoofBuilder.SUPPORTED_PROFILES:
            return mesh

        top_z = mesh.get("top_z")
        bottom_z = mesh.get("bottom_z")
        top_points = mesh.get("top", [])

        if top_z is None or bottom_z is None or len(top_points) < 3:
            return mesh

        ring = AtlasCastleRoofBuilder._clean_ring(top_points)

        # ring = AtlasCastleRoofBuilder._remove_collinear_ring_points(ring)

        if len(ring) < 3:
            return mesh

        remaining_triangles = []
        removed_top_count = 0

        for triangle in mesh.get(
            "triangles",
            [],
        ):
            if AtlasCastleRoofBuilder._is_top_triangle(
                triangle=triangle,
                top_z=top_z,
            ):
                removed_top_count += 1
                continue

            remaining_triangles.append(triangle)

        if removed_top_count == 0:
            return mesh

        centroid_x = sum(point[0] for point in ring) / len(ring)

        centroid_y = sum(point[1] for point in ring) / len(ring)

        xs = [point[0] for point in ring]

        ys = [point[1] for point in ring]

        width_mm = max(xs) - min(xs)

        depth_mm = max(ys) - min(ys)

        roof_width_mm = max(
            width_mm,
            depth_mm,
        )

        roof_short_side_mm = min(
            width_mm,
            depth_mm,
        )
        roof_profile = mesh.get("castle_roof_profile")

        footprint_ratio = roof_width_mm / max(
            roof_short_side_mm,
            1e-9,
        )

        use_gable_roof = roof_profile == "gabled" or footprint_ratio >= 1.80

        if use_gable_roof:
            mesh["castle_roof_skipped_for_gable"] = True
            mesh["roof_footprint_ratio"] = footprint_ratio
            return mesh

        body_height_mm = max(
            0.0,
            float(top_z) - float(bottom_z),
        )

        body_ratio_height = (
            body_height_mm
            * AtlasCastleRoofBuilder.ROOF_BODY_HEIGHT_RATIO[castle_profile]
        )

        width_min_height = (
            roof_width_mm * AtlasCastleRoofBuilder.ROOF_WIDTH_MIN_RATIO[castle_profile]
        )

        width_max_height = (
            roof_width_mm * AtlasCastleRoofBuilder.ROOF_WIDTH_MAX_RATIO[castle_profile]
        )

        footprint_slenderness = roof_width_mm / max(
            roof_short_side_mm,
            1e-9,
        )

        target_slenderness = AtlasCastleRoofBuilder.ROOF_SLENDERNESS_TARGET[
            castle_profile
        ]

        slenderness_factor = target_slenderness / max(
            footprint_slenderness,
            1.0,
        )

        slenderness_factor = max(
            0.72,
            min(
                slenderness_factor,
                1.08,
            ),
        )

        roof_height_mm = body_ratio_height * slenderness_factor

        roof_height_mm = max(
            roof_height_mm,
            width_min_height,
        )

        roof_height_mm = min(
            roof_height_mm,
            width_max_height,
        )

        body_max_height = (
            body_height_mm * AtlasCastleRoofBuilder.ROOF_BODY_MAX_RATIO[castle_profile]
        )

        roof_height_mm = min(
            roof_height_mm,
            body_max_height,
        )

        roof_height_mm = max(
            roof_height_mm,
            AtlasCastleRoofBuilder.MIN_ROOF_HEIGHT_MM,
        )

        roof_height_mm = min(
            roof_height_mm,
            AtlasCastleRoofBuilder.MAX_ROOF_HEIGHT_MM,
        )

        apex = (
            centroid_x,
            centroid_y,
            float(top_z) + roof_height_mm,
        )

        roof_triangles = []

        for index, point_1 in enumerate(ring):
            point_2 = ring[(index + 1) % len(ring)]

            roof_triangles.append(
                (
                    point_1,
                    point_2,
                    apex,
                )
            )

        mesh["triangles"] = [
            *remaining_triangles,
            *roof_triangles,
        ]

        mesh["body_top_z"] = float(top_z)

        mesh["roof_top_z"] = apex[2]
        mesh["top_z"] = apex[2]
        mesh["roof_apex"] = apex

        mesh["roof_triangles"] = roof_triangles

        mesh["roof_height_mm"] = roof_height_mm

        mesh["roof_geometry"] = AtlasCastleRoofBuilder._detect_roof_geometry(ring)

        mesh["roof_ring_point_count"] = len(ring)

        mesh["castle_roof_applied"] = True

        return mesh

    @staticmethod
    def _clean_ring(
        points,
    ):
        clean = []

        for point in points:
            if point is None or len(point) < 3:
                continue

            current = (
                float(point[0]),
                float(point[1]),
                float(point[2]),
            )

            if clean and AtlasCastleRoofBuilder._same_point(
                clean[-1],
                current,
            ):
                continue

            clean.append(current)

        if len(clean) >= 2 and AtlasCastleRoofBuilder._same_point(
            clean[0],
            clean[-1],
        ):
            clean.pop()

        return clean

    @staticmethod
    def _remove_collinear_ring_points(
        ring,
    ):
        if len(ring) <= 3:
            return list(ring)

        result = list(ring)
        changed = True

        while changed and len(result) > 3:
            changed = False
            cleaned = []
            point_count = len(result)

            for index, current in enumerate(result):
                previous_point = result[(index - 1) % point_count]

                next_point = result[(index + 1) % point_count]

                if AtlasCastleRoofBuilder._point_on_segment(
                    point=current,
                    segment_start=previous_point,
                    segment_end=next_point,
                ):
                    changed = True
                    continue

                cleaned.append(current)

            if len(cleaned) < 3:
                break

            result = cleaned

        return result

    @staticmethod
    def _point_on_segment(
        point,
        segment_start,
        segment_end,
    ):
        cross_product = (point[0] - segment_start[0]) * (
            segment_end[1] - segment_start[1]
        ) - (point[1] - segment_start[1]) * (segment_end[0] - segment_start[0])

        if abs(cross_product) > AtlasCastleRoofBuilder.COLLINEAR_TOLERANCE:
            return False

        minimum_x = (
            min(
                segment_start[0],
                segment_end[0],
            )
            - AtlasCastleRoofBuilder.COLLINEAR_TOLERANCE
        )

        maximum_x = (
            max(
                segment_start[0],
                segment_end[0],
            )
            + AtlasCastleRoofBuilder.COLLINEAR_TOLERANCE
        )

        minimum_y = (
            min(
                segment_start[1],
                segment_end[1],
            )
            - AtlasCastleRoofBuilder.COLLINEAR_TOLERANCE
        )

        maximum_y = (
            max(
                segment_start[1],
                segment_end[1],
            )
            + AtlasCastleRoofBuilder.COLLINEAR_TOLERANCE
        )

        return (
            minimum_x <= point[0] <= maximum_x
            and minimum_y <= point[1] <= maximum_y
            and not AtlasCastleRoofBuilder._same_xy(
                point,
                segment_start,
            )
            and not AtlasCastleRoofBuilder._same_xy(
                point,
                segment_end,
            )
        )

    @staticmethod
    def _is_top_triangle(
        triangle,
        top_z,
    ):
        if len(triangle) != 3:
            return False

        return all(
            abs(float(point[2]) - float(top_z)) <= AtlasCastleRoofBuilder.Z_TOLERANCE
            for point in triangle
        )

    @staticmethod
    def _detect_roof_geometry(
        ring,
    ):
        if len(ring) <= 5:
            return "pyramid"

        return "polygonal_spire"

    @staticmethod
    def _same_xy(
        point_1,
        point_2,
    ):
        return round(
            float(point_1[0]),
            AtlasCastleRoofBuilder.POINT_PRECISION,
        ) == round(
            float(point_2[0]),
            AtlasCastleRoofBuilder.POINT_PRECISION,
        ) and round(
            float(point_1[1]),
            AtlasCastleRoofBuilder.POINT_PRECISION,
        ) == round(
            float(point_2[1]),
            AtlasCastleRoofBuilder.POINT_PRECISION,
        )

    @staticmethod
    def _same_point(
        point_1,
        point_2,
    ):
        return AtlasCastleRoofBuilder._same_xy(
            point_1,
            point_2,
        ) and round(
            float(point_1[2]),
            AtlasCastleRoofBuilder.POINT_PRECISION,
        ) == round(
            float(point_2[2]),
            AtlasCastleRoofBuilder.POINT_PRECISION,
        )
