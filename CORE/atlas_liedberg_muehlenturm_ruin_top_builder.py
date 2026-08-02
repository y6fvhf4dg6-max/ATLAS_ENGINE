class AtlasLiedbergMuehlenturmRuinTopBuilder:
    MUEHLENTURM_LANDMARK_ID = 143975860

    RADIUS_SCALE = 1.12
    WALL_THICKNESS_MM = 0.35
    BOTTOM_THICKNESS_MM = 0.35

    TOP_OFFSETS_MM = (
        -0.04,
        -0.10,
        -0.18,
        -0.24,
        -0.28,
        -0.24,
        -0.16,
        -0.08,
    )

    @staticmethod
    def apply(tower_mesh):
        if not tower_mesh:
            return tower_mesh

        try:
            landmark_id = int(
                tower_mesh.get("landmark_id")
            )
        except (TypeError, ValueError):
            return tower_mesh

        if (
            landmark_id
            != AtlasLiedbergMuehlenturmRuinTopBuilder
            .MUEHLENTURM_LANDMARK_ID
        ):
            return tower_mesh

        original_bottom = list(
            tower_mesh.get("bottom", [])
        )
        original_top = list(
            tower_mesh.get("top", [])
        )

        if (
            len(original_bottom) < 3
            or len(original_bottom) != len(original_top)
        ):
            return tower_mesh

        center_x = sum(
            point[0] for point in original_top
        ) / len(original_top)
        center_y = sum(
            point[1] for point in original_top
        ) / len(original_top)

        outer_bottom = []
        outer_top = []

        for index, (bottom_point, top_point) in enumerate(
            zip(original_bottom, original_top)
        ):
            scaled_bottom = (
                AtlasLiedbergMuehlenturmRuinTopBuilder
                ._scale_point_xy(
                    point=bottom_point,
                    center_x=center_x,
                    center_y=center_y,
                )
            )
            scaled_top = (
                AtlasLiedbergMuehlenturmRuinTopBuilder
                ._scale_point_xy(
                    point=top_point,
                    center_x=center_x,
                    center_y=center_y,
                )
            )

            offset = (
                AtlasLiedbergMuehlenturmRuinTopBuilder
                .TOP_OFFSETS_MM[
                    index
                    % len(
                        AtlasLiedbergMuehlenturmRuinTopBuilder
                        .TOP_OFFSETS_MM
                    )
                ]
            )

            outer_bottom.append(scaled_bottom)
            outer_top.append(
                (
                    scaled_top[0],
                    scaled_top[1],
                    float(top_point[2]) + offset,
                )
            )

        inner_bottom = [
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._inset_point(
                point=point,
                center_x=center_x,
                center_y=center_y,
                z=(
                    float(point[2])
                    + AtlasLiedbergMuehlenturmRuinTopBuilder
                    .BOTTOM_THICKNESS_MM
                ),
            )
            for point in outer_bottom
        ]

        inner_top = [
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._inset_point(
                point=point,
                center_x=center_x,
                center_y=center_y,
                z=float(point[2]),
            )
            for point in outer_top
        ]

        outer_walls = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._build_ring_walls(
                lower=outer_bottom,
                upper=outer_top,
                inward=False,
            )
        )
        inner_walls = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._build_ring_walls(
                lower=inner_bottom,
                upper=inner_top,
                inward=True,
            )
        )
        rim_triangles = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._build_annulus(
                outer=outer_top,
                inner=inner_top,
                upward=True,
            )
        )
        outer_bottom_triangles = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._build_fan(
                ring=outer_bottom,
                upward=False,
            )
        )
        inner_floor_triangles = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            ._build_fan(
                ring=inner_bottom,
                upward=True,
            )
        )

        triangles = [
            *outer_walls,
            *inner_walls,
            *rim_triangles,
            *outer_bottom_triangles,
            *inner_floor_triangles,
        ]

        tower_mesh["bottom"] = outer_bottom
        tower_mesh["top"] = outer_top
        tower_mesh["walls"] = [
            *outer_walls,
            *inner_walls,
        ]
        tower_mesh["triangles"] = triangles

        tower_mesh["architectural_role"] = (
            "muehlenturm_ruin_body"
        )
        tower_mesh["radius_scale"] = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            .RADIUS_SCALE
        )
        tower_mesh["wall_thickness_mm"] = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            .WALL_THICKNESS_MM
        )
        tower_mesh["muehlenturm_body_scaled"] = True
        tower_mesh[
            "muehlenturm_ruin_top_applied"
        ] = True
        tower_mesh["muehlenturm_open_top"] = True
        tower_mesh["muehlenturm_hollow_body"] = True
        tower_mesh["muehlenturm_top_cap_triangles"] = []

        return tower_mesh

    @staticmethod
    def _scale_point_xy(
        *,
        point,
        center_x,
        center_y,
    ):
        scale = (
            AtlasLiedbergMuehlenturmRuinTopBuilder
            .RADIUS_SCALE
        )

        return (
            center_x
            + (float(point[0]) - center_x) * scale,
            center_y
            + (float(point[1]) - center_y) * scale,
            float(point[2]),
        )

    @staticmethod
    def _inset_point(
        *,
        point,
        center_x,
        center_y,
        z,
    ):
        dx = float(point[0]) - center_x
        dy = float(point[1]) - center_y
        radius = (dx * dx + dy * dy) ** 0.5

        if radius <= 1e-9:
            return (
                float(point[0]),
                float(point[1]),
                float(z),
            )

        inner_radius = max(
            0.10,
            radius
            - AtlasLiedbergMuehlenturmRuinTopBuilder
            .WALL_THICKNESS_MM,
        )
        ratio = inner_radius / radius

        return (
            center_x + dx * ratio,
            center_y + dy * ratio,
            float(z),
        )

    @staticmethod
    def _build_ring_walls(
        *,
        lower,
        upper,
        inward,
    ):
        triangles = []
        count = len(lower)

        for index in range(count):
            next_index = (index + 1) % count

            b0 = lower[index]
            b1 = lower[next_index]
            t0 = upper[index]
            t1 = upper[next_index]

            if inward:
                triangles.extend(
                    [
                        (b0, t1, b1),
                        (b0, t0, t1),
                    ]
                )
            else:
                triangles.extend(
                    [
                        (b0, b1, t1),
                        (b0, t1, t0),
                    ]
                )

        return triangles

    @staticmethod
    def _build_annulus(
        *,
        outer,
        inner,
        upward,
    ):
        triangles = []
        count = len(outer)

        for index in range(count):
            next_index = (index + 1) % count

            o0 = outer[index]
            o1 = outer[next_index]
            i0 = inner[index]
            i1 = inner[next_index]

            if upward:
                triangles.extend(
                    [
                        (o0, o1, i1),
                        (o0, i1, i0),
                    ]
                )
            else:
                triangles.extend(
                    [
                        (o0, i1, o1),
                        (o0, i0, i1),
                    ]
                )

        return triangles

    @staticmethod
    def _build_fan(
        *,
        ring,
        upward,
    ):
        center = (
            sum(point[0] for point in ring) / len(ring),
            sum(point[1] for point in ring) / len(ring),
            sum(point[2] for point in ring) / len(ring),
        )

        triangles = []

        for index in range(len(ring)):
            next_index = (index + 1) % len(ring)

            if upward:
                triangles.append(
                    (
                        center,
                        ring[index],
                        ring[next_index],
                    )
                )
            else:
                triangles.append(
                    (
                        center,
                        ring[next_index],
                        ring[index],
                    )
                )

        return triangles
