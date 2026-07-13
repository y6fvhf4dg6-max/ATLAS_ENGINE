"""
ATLAS Castle Crenellation Builder v0.1

Düz bir sur segmentinin üstünde baskıya uygun,
tekrarlanan mazgal dişleri üretir.
"""


class AtlasCastleCrenellationBuilder:
    TRIANGLES_PER_TOOTH = 12
    EPSILON = 1e-9

    @staticmethod
    def build_crenellations(
        start_left,
        start_right,
        end_left,
        end_right,
        tooth_width_mm,
        gap_width_mm,
        tooth_height_mm,
    ):
        if (
            tooth_width_mm <= 0.0
            or gap_width_mm < 0.0
            or tooth_height_mm <= 0.0
        ):
            return None

        start_center = AtlasCastleCrenellationBuilder._midpoint(
            start_left,
            start_right,
        )
        end_center = AtlasCastleCrenellationBuilder._midpoint(
            end_left,
            end_right,
        )

        dx = end_center[0] - start_center[0]
        dy = end_center[1] - start_center[1]
        dz = end_center[2] - start_center[2]

        length = (dx * dx + dy * dy + dz * dz) ** 0.5

        if length <= AtlasCastleCrenellationBuilder.EPSILON:
            return None

        pitch = tooth_width_mm + gap_width_mm

        if pitch <= AtlasCastleCrenellationBuilder.EPSILON:
            return None

        tooth_count = int(length // pitch)

        if tooth_count < 1:
            return None

        ux = dx / length
        uy = dy / length
        uz = dz / length

        triangles = []

        for tooth_index in range(tooth_count):
            start_distance = tooth_index * pitch
            end_distance = start_distance + tooth_width_mm

            if end_distance > length + AtlasCastleCrenellationBuilder.EPSILON:
                break

            ratio_start = start_distance / length
            ratio_end = end_distance / length

            base_start_left = AtlasCastleCrenellationBuilder._lerp(
                start_left,
                end_left,
                ratio_start,
            )
            base_start_right = AtlasCastleCrenellationBuilder._lerp(
                start_right,
                end_right,
                ratio_start,
            )
            base_end_left = AtlasCastleCrenellationBuilder._lerp(
                start_left,
                end_left,
                ratio_end,
            )
            base_end_right = AtlasCastleCrenellationBuilder._lerp(
                start_right,
                end_right,
                ratio_end,
            )

            top_start_left = (
                base_start_left[0],
                base_start_left[1],
                base_start_left[2] + tooth_height_mm,
            )
            top_start_right = (
                base_start_right[0],
                base_start_right[1],
                base_start_right[2] + tooth_height_mm,
            )
            top_end_left = (
                base_end_left[0],
                base_end_left[1],
                base_end_left[2] + tooth_height_mm,
            )
            top_end_right = (
                base_end_right[0],
                base_end_right[1],
                base_end_right[2] + tooth_height_mm,
            )

            AtlasCastleCrenellationBuilder._add_box_triangles(
                triangles=triangles,
                bottom_start_left=base_start_left,
                bottom_start_right=base_start_right,
                bottom_end_left=base_end_left,
                bottom_end_right=base_end_right,
                top_start_left=top_start_left,
                top_start_right=top_start_right,
                top_end_left=top_end_left,
                top_end_right=top_end_right,
            )

        if not triangles:
            return None

        actual_tooth_count = (
            len(triangles)
            // AtlasCastleCrenellationBuilder.TRIANGLES_PER_TOOTH
        )

        return {
            "type": "castle_wall_crenellations",
            "triangles": triangles,
            "tooth_count": actual_tooth_count,
            "tooth_width_mm": tooth_width_mm,
            "gap_width_mm": gap_width_mm,
            "tooth_height_mm": tooth_height_mm,
            "segment_length_mm": length,
        }

    @staticmethod
    def _midpoint(first, second):
        return (
            (first[0] + second[0]) / 2.0,
            (first[1] + second[1]) / 2.0,
            (first[2] + second[2]) / 2.0,
        )

    @staticmethod
    def _lerp(start, end, ratio):
        return (
            start[0] + (end[0] - start[0]) * ratio,
            start[1] + (end[1] - start[1]) * ratio,
            start[2] + (end[2] - start[2]) * ratio,
        )

    @staticmethod
    def _add_box_triangles(
        triangles,
        bottom_start_left,
        bottom_start_right,
        bottom_end_left,
        bottom_end_right,
        top_start_left,
        top_start_right,
        top_end_left,
        top_end_right,
    ):
        # Alt yüzey
        triangles.append(
            (
                bottom_start_left,
                bottom_end_right,
                bottom_start_right,
            )
        )
        triangles.append(
            (
                bottom_start_left,
                bottom_end_left,
                bottom_end_right,
            )
        )

        # Üst yüzey
        triangles.append(
            (
                top_start_left,
                top_start_right,
                top_end_right,
            )
        )
        triangles.append(
            (
                top_start_left,
                top_end_right,
                top_end_left,
            )
        )

        # Sol yüzey
        triangles.append(
            (
                bottom_start_left,
                top_start_left,
                top_end_left,
            )
        )
        triangles.append(
            (
                bottom_start_left,
                top_end_left,
                bottom_end_left,
            )
        )

        # Sağ yüzey
        triangles.append(
            (
                bottom_start_right,
                bottom_end_right,
                top_end_right,
            )
        )
        triangles.append(
            (
                bottom_start_right,
                top_end_right,
                top_start_right,
            )
        )

        # Baş yüzey
        triangles.append(
            (
                bottom_start_left,
                bottom_start_right,
                top_start_right,
            )
        )
        triangles.append(
            (
                bottom_start_left,
                top_start_right,
                top_start_left,
            )
        )

        # Son yüzey
        triangles.append(
            (
                bottom_end_left,
                top_end_right,
                bottom_end_right,
            )
        )
        triangles.append(
            (
                bottom_end_left,
                top_end_left,
                top_end_right,
            )
        )
