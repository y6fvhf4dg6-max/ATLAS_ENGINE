class AtlasLiedbergGateTowerCapBuilder:
    SCHLOSS_LIEDBERG_SOURCE_ID = 143975871

    CAP_HEIGHT_MM = 1.80
    TOP_WIDTH_RATIO = 0.58

    @staticmethod
    def build(gate_tower_mesh):
        if not gate_tower_mesh:
            return None

        try:
            source_id = int(
                gate_tower_mesh.get("source_id")
            )
        except (TypeError, ValueError):
            return None

        if (
            source_id
            != AtlasLiedbergGateTowerCapBuilder
            .SCHLOSS_LIEDBERG_SOURCE_ID
        ):
            return None

        if (
            gate_tower_mesh.get("type")
            != "liedberg_gate_tower"
        ):
            return None

        bottom = list(
            gate_tower_mesh.get("top", [])
        )

        if len(bottom) != 4:
            return None

        base_z = float(
            gate_tower_mesh.get(
                "top_z",
                bottom[0][2],
            )
        )
        top_z = (
            base_z
            + AtlasLiedbergGateTowerCapBuilder
            .CAP_HEIGHT_MM
        )

        center_x = sum(
            point[0] for point in bottom
        ) / 4.0
        center_y = sum(
            point[1] for point in bottom
        ) / 4.0

        ratio = (
            AtlasLiedbergGateTowerCapBuilder
            .TOP_WIDTH_RATIO
        )

        top = [
            (
                center_x
                + (point[0] - center_x) * ratio,
                center_y
                + (point[1] - center_y) * ratio,
                top_z,
            )
            for point in bottom
        ]

        triangles = (
            AtlasLiedbergGateTowerCapBuilder
            ._build_closed_frustum_triangles(
                bottom=bottom,
                top=top,
            )
        )

        return {
            "type": "liedberg_gate_tower_cap",
            "source_id": source_id,
            "architectural_role": (
                "gate_tower_transition_cap"
            ),
            "placement_mode": (
                "castle_roof_component"
            ),
            "base_z": base_z,
            "top_z": top_z,
            "height_mm": (
                AtlasLiedbergGateTowerCapBuilder
                .CAP_HEIGHT_MM
            ),
            "top_width_ratio": ratio,
            "bottom": bottom,
            "top": top,
            "walls": triangles[4:],
            "triangles": triangles,
        }

    @staticmethod
    def _build_closed_frustum_triangles(
        bottom,
        top,
    ):
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
