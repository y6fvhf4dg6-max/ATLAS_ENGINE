import math


class AtlasLiedbergGateTowerBuilder:
    SCHLOSS_LIEDBERG_SOURCE_ID = 143975871
    TARGET_ROOF_PIECE_INDEX = 2

    MIN_TOWER_HEIGHT_MM = 3.0
    WIDTH_FACTOR = 1.10
    DEPTH_FACTOR = 0.88

    @staticmethod
    def build(castle_mesh):
        if not castle_mesh:
            return None

        try:
            source_id = int(castle_mesh.get("source_id"))
        except (TypeError, ValueError):
            return None

        if source_id != AtlasLiedbergGateTowerBuilder.SCHLOSS_LIEDBERG_SOURCE_ID:
            return None

        roof_record = AtlasLiedbergGateTowerBuilder._find_target_roof_record(
            castle_mesh.get("multi_gable_roof_records", [])
        )

        if roof_record is None:
            return None

        ridge_start = roof_record.get("ridge_start")
        ridge_end = roof_record.get("ridge_end")

        if (
            not ridge_start
            or not ridge_end
            or len(ridge_start) < 2
            or len(ridge_end) < 2
        ):
            return None

        center_x = (float(ridge_start[0]) + float(ridge_end[0])) / 2.0
        center_y = (float(ridge_start[1]) + float(ridge_end[1])) / 2.0

        dx = float(ridge_end[0]) - float(ridge_start[0])
        dy = float(ridge_end[1]) - float(ridge_start[1])
        length = math.hypot(dx, dy)

        if length <= 1e-9:
            return None

        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux

        width_mm = max(
            2.10,
            float(roof_record.get("short_side_mm", 2.10))
            * AtlasLiedbergGateTowerBuilder.WIDTH_FACTOR,
        )
        depth_mm = max(
            2.30,
            float(roof_record.get("long_side_mm", 2.30))
            * AtlasLiedbergGateTowerBuilder.DEPTH_FACTOR,
        )

        half_width = width_mm / 2.0
        half_depth = depth_mm / 2.0

        footprint_xy = [
            (
                center_x - ux * half_depth - px * half_width,
                center_y - uy * half_depth - py * half_width,
            ),
            (
                center_x + ux * half_depth - px * half_width,
                center_y + uy * half_depth - py * half_width,
            ),
            (
                center_x + ux * half_depth + px * half_width,
                center_y + uy * half_depth + py * half_width,
            ),
            (
                center_x - ux * half_depth + px * half_width,
                center_y - uy * half_depth + py * half_width,
            ),
        ]

        body_top_z = float(castle_mesh.get("body_top_z", 0.0))
        roof_top_z = float(castle_mesh.get("roof_top_z", body_top_z))

        base_z = body_top_z
        height_mm = max(
            AtlasLiedbergGateTowerBuilder.MIN_TOWER_HEIGHT_MM,
            roof_top_z - body_top_z + 1.20,
        )
        top_z = base_z + height_mm

        bottom = [
            (x, y, base_z)
            for x, y in footprint_xy
        ]
        top = [
            (x, y, top_z)
            for x, y in footprint_xy
        ]

        triangles = AtlasLiedbergGateTowerBuilder._build_closed_box_triangles(
            bottom=bottom,
            top=top,
        )

        return {
            "type": "liedberg_gate_tower",
            "source_id": source_id,
            "architectural_role": "gate_tower_body",
            "placement_mode": "castle_roof_component",
            "base_z": base_z,
            "top_z": top_z,
            "height_mm": height_mm,
            "width_mm": width_mm,
            "depth_mm": depth_mm,
            "bottom": bottom,
            "top": top,
            "walls": triangles[4:],
            "triangles": triangles,
        }

    @staticmethod
    def _find_target_roof_record(records):
        for record in records or []:
            if (
                int(record.get("piece_index", -1))
                == AtlasLiedbergGateTowerBuilder.TARGET_ROOF_PIECE_INDEX
            ):
                return record

        return None

    @staticmethod
    def _build_closed_box_triangles(bottom, top):
        b0, b1, b2, b3 = bottom
        t0, t1, t2, t3 = top

        return [
            (b0, b2, b1),
            (b0, b3, b2),
            (t0, t1, t2),
            (t0, t2, t3),
            (b0, b1, t1),
            (b0, t1, t0),
            (b1, b2, t2),
            (b1, t2, t1),
            (b2, b3, t3),
            (b2, t3, t2),
            (b3, b0, t0),
            (b3, t0, t3),
        ]
