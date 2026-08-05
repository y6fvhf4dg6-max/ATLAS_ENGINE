"""
ATLAS Facade Panel Builder v0.1

Düz bir cephe duvarı üzerinde tekrar eden, kapalı ve
manifold kabartma paneller üretir.

Kullanım alanları:
- pencere ve kapı sembolleri
- kemer tabanları
- tarihi cephe ritimleri
- saray, tiyatro, stoa ve anıtsal yapı detayları

Bu ilk sürüm gerçek boolean boşluk açmaz.
Her panel cepheye gömülen ayrı kapalı prizma olarak üretilir.
"""


class AtlasFacadePanelBuilder:
    DEFAULT_DEPTH_MM = 0.18
    DEFAULT_EMBED_MM = 0.04

    @staticmethod
    def build_repeated_rectangles(
        wall_quad,
        column_count,
        row_count,
        panel_width_ratio=0.45,
        panel_height_ratio=0.40,
        horizontal_margin_ratio=0.08,
        vertical_margin_ratio=0.10,
        depth_mm=None,
        embed_mm=None,
        metadata=None,
    ):
        if not wall_quad or len(wall_quad) != 4:
            raise ValueError(
                "wall_quad must contain four points"
            )

        column_count = int(column_count)
        row_count = int(row_count)

        if column_count < 1:
            raise ValueError(
                "column_count must be at least one"
            )

        if row_count < 1:
            raise ValueError(
                "row_count must be at least one"
            )

        panel_width_ratio = float(
            panel_width_ratio
        )
        panel_height_ratio = float(
            panel_height_ratio
        )
        horizontal_margin_ratio = float(
            horizontal_margin_ratio
        )
        vertical_margin_ratio = float(
            vertical_margin_ratio
        )

        if not 0.0 < panel_width_ratio <= 1.0:
            raise ValueError(
                "panel_width_ratio must be in "
                "the range (0, 1]"
            )

        if not 0.0 < panel_height_ratio <= 1.0:
            raise ValueError(
                "panel_height_ratio must be in "
                "the range (0, 1]"
            )

        if depth_mm is None:
            depth_mm = (
                AtlasFacadePanelBuilder
                .DEFAULT_DEPTH_MM
            )

        if embed_mm is None:
            embed_mm = (
                AtlasFacadePanelBuilder
                .DEFAULT_EMBED_MM
            )

        depth_mm = float(depth_mm)
        embed_mm = float(embed_mm)

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        bottom_left = wall_quad[0]
        bottom_right = wall_quad[1]
        top_right = wall_quad[2]
        top_left = wall_quad[3]

        wall_u = (
            bottom_right[0] - bottom_left[0],
            bottom_right[1] - bottom_left[1],
            bottom_right[2] - bottom_left[2],
        )

        wall_v = (
            top_left[0] - bottom_left[0],
            top_left[1] - bottom_left[1],
            top_left[2] - bottom_left[2],
        )

        normal = (
            wall_u[1] * wall_v[2]
            - wall_u[2] * wall_v[1],
            wall_u[2] * wall_v[0]
            - wall_u[0] * wall_v[2],
            wall_u[0] * wall_v[1]
            - wall_u[1] * wall_v[0],
        )

        normal_length = (
            normal[0] ** 2
            + normal[1] ** 2
            + normal[2] ** 2
        ) ** 0.5

        if normal_length <= 0.0:
            raise ValueError(
                "wall_quad is degenerate"
            )

        normal = (
            normal[0] / normal_length,
            normal[1] / normal_length,
            normal[2] / normal_length,
        )

        usable_u_start = (
            horizontal_margin_ratio
        )
        usable_u_end = (
            1.0 - horizontal_margin_ratio
        )
        usable_v_start = (
            vertical_margin_ratio
        )
        usable_v_end = (
            1.0 - vertical_margin_ratio
        )

        usable_u = (
            usable_u_end - usable_u_start
        )
        usable_v = (
            usable_v_end - usable_v_start
        )

        if usable_u <= 0.0 or usable_v <= 0.0:
            raise ValueError(
                "margins leave no usable facade area"
            )

        cell_u = usable_u / column_count
        cell_v = usable_v / row_count

        panel_u = cell_u * panel_width_ratio
        panel_v = cell_v * panel_height_ratio

        component_meshes = []
        triangles = []

        for row_index in range(row_count):
            for column_index in range(
                column_count
            ):
                center_u = (
                    usable_u_start
                    + cell_u
                    * (
                        column_index
                        + 0.5
                    )
                )

                center_v = (
                    usable_v_start
                    + cell_v
                    * (
                        row_index
                        + 0.5
                    )
                )

                u_min = center_u - panel_u * 0.5
                u_max = center_u + panel_u * 0.5
                v_min = center_v - panel_v * 0.5
                v_max = center_v + panel_v * 0.5

                component_metadata = {
                    "component_type": (
                        "facade_panel"
                    ),
                    "row_index": row_index,
                    "column_index": (
                        column_index
                    ),
                    "source_system": (
                        "facade_panel_builder"
                    ),
                }

                if metadata:
                    component_metadata.update(
                        dict(metadata)
                    )

                component = (
                    AtlasFacadePanelBuilder
                    ._build_panel_prism(
                        wall_quad=wall_quad,
                        normal=normal,
                        u_min=u_min,
                        u_max=u_max,
                        v_min=v_min,
                        v_max=v_max,
                        depth_mm=depth_mm,
                        embed_mm=embed_mm,
                        metadata=(
                            component_metadata
                        ),
                    )
                )

                component_meshes.append(
                    component
                )
                triangles.extend(
                    component["triangles"]
                )

        return {
            "triangles": triangles,
            "component_meshes": (
                component_meshes
            ),
            "panel_count": len(
                component_meshes
            ),
            "column_count": column_count,
            "row_count": row_count,
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": (
                "repeated_facade_panels"
            ),
        }

    @staticmethod
    def _build_panel_prism(
        wall_quad,
        normal,
        u_min,
        u_max,
        v_min,
        v_max,
        depth_mm,
        embed_mm,
        metadata,
    ):
        bottom_left = wall_quad[0]
        bottom_right = wall_quad[1]
        top_right = wall_quad[2]
        top_left = wall_quad[3]

        def point_at(u_value, v_value, offset):
            one_minus_u = 1.0 - u_value
            one_minus_v = 1.0 - v_value

            base_point = tuple(
                (
                    bottom_left[axis]
                    * one_minus_u
                    * one_minus_v
                    + bottom_right[axis]
                    * u_value
                    * one_minus_v
                    + top_right[axis]
                    * u_value
                    * v_value
                    + top_left[axis]
                    * one_minus_u
                    * v_value
                )
                for axis in range(3)
            )

            return (
                base_point[0]
                + normal[0] * offset,
                base_point[1]
                + normal[1] * offset,
                base_point[2]
                + normal[2] * offset,
            )

        back_offset = -embed_mm
        front_offset = depth_mm - embed_mm

        back = [
            point_at(u_min, v_min, back_offset),
            point_at(u_max, v_min, back_offset),
            point_at(u_max, v_max, back_offset),
            point_at(u_min, v_max, back_offset),
        ]

        front = [
            point_at(u_min, v_min, front_offset),
            point_at(u_max, v_min, front_offset),
            point_at(u_max, v_max, front_offset),
            point_at(u_min, v_max, front_offset),
        ]

        triangles = [
            (back[0], back[2], back[1]),
            (back[0], back[3], back[2]),
            (front[0], front[1], front[2]),
            (front[0], front[2], front[3]),
            (back[0], back[1], front[1]),
            (back[0], front[1], front[0]),
            (back[1], back[2], front[2]),
            (back[1], front[2], front[1]),
            (back[2], back[3], front[3]),
            (back[2], front[3], front[2]),
            (back[3], back[0], front[0]),
            (back[3], front[0], front[3]),
        ]

        mesh = {
            "triangles": triangles,
            "back": back,
            "front": front,
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": (
                "facade_panel_prism"
            ),
        }

        mesh.update(metadata)

        return mesh


def _build_repeated_arches(
    wall_quad,
    column_count,
    row_count,
    panel_width_ratio=0.52,
    panel_height_ratio=0.62,
    arch_height_ratio=0.38,
    horizontal_margin_ratio=0.06,
    vertical_margin_ratio=0.10,
    vertical_alignment="center",
    depth_mm=None,
    embed_mm=None,
    arch_segments=6,
    metadata=None,
):
    """
    Düz cephe üzerinde tekrar eden yarım daire tepeli,
    kapalı ve manifold kemer paneller üretir.
    """
    from math import cos, pi, sin

    if not wall_quad or len(wall_quad) != 4:
        raise ValueError(
            "wall_quad must contain four points"
        )

    column_count = int(column_count)
    row_count = int(row_count)
    arch_segments = int(arch_segments)

    if column_count < 1:
        raise ValueError(
            "column_count must be at least one"
        )

    if row_count < 1:
        raise ValueError(
            "row_count must be at least one"
        )

    if arch_segments < 3:
        raise ValueError(
            "arch_segments must be at least three"
        )

    if depth_mm is None:
        depth_mm = (
            AtlasFacadePanelBuilder
            .DEFAULT_DEPTH_MM
        )

    if embed_mm is None:
        embed_mm = (
            AtlasFacadePanelBuilder
            .DEFAULT_EMBED_MM
        )

    depth_mm = float(depth_mm)
    embed_mm = float(embed_mm)

    if depth_mm <= 0.0:
        raise ValueError(
            "depth_mm must be greater than zero"
        )

    if embed_mm < 0.0:
        raise ValueError(
            "embed_mm must be non-negative"
        )

    vertical_alignment = str(
        vertical_alignment
    ).strip().lower()

    if vertical_alignment not in {
        "center",
        "bottom",
    }:
        raise ValueError(
            "vertical_alignment must be "
            "center or bottom"
        )

    bottom_left = wall_quad[0]
    bottom_right = wall_quad[1]
    top_right = wall_quad[2]
    top_left = wall_quad[3]

    wall_u = (
        bottom_right[0] - bottom_left[0],
        bottom_right[1] - bottom_left[1],
        bottom_right[2] - bottom_left[2],
    )

    wall_v = (
        top_left[0] - bottom_left[0],
        top_left[1] - bottom_left[1],
        top_left[2] - bottom_left[2],
    )

    normal = (
        wall_u[1] * wall_v[2]
        - wall_u[2] * wall_v[1],
        wall_u[2] * wall_v[0]
        - wall_u[0] * wall_v[2],
        wall_u[0] * wall_v[1]
        - wall_u[1] * wall_v[0],
    )

    normal_length = (
        normal[0] ** 2
        + normal[1] ** 2
        + normal[2] ** 2
    ) ** 0.5

    if normal_length <= 0.0:
        raise ValueError(
            "wall_quad is degenerate"
        )

    normal = tuple(
        value / normal_length
        for value in normal
    )

    usable_u = (
        1.0
        - 2.0 * horizontal_margin_ratio
    )

    usable_v = (
        1.0
        - 2.0 * vertical_margin_ratio
    )

    if usable_u <= 0.0 or usable_v <= 0.0:
        raise ValueError(
            "margins leave no usable facade area"
        )

    cell_u = usable_u / column_count
    cell_v = usable_v / row_count

    panel_width = (
        cell_u * float(panel_width_ratio)
    )

    panel_height = (
        cell_v * float(panel_height_ratio)
    )

    wall_width = (
        wall_u[0] ** 2
        + wall_u[1] ** 2
        + wall_u[2] ** 2
    ) ** 0.5

    wall_height = (
        wall_v[0] ** 2
        + wall_v[1] ** 2
        + wall_v[2] ** 2
    ) ** 0.5

    if (
        wall_width <= 0.0
        or wall_height <= 0.0
    ):
        raise ValueError(
            "wall_quad is degenerate"
        )

    physical_panel_width = (
        panel_width * wall_width
    )
    physical_panel_height = (
        panel_height * wall_height
    )

    physical_arch_height = min(
        physical_panel_width
        * 0.5
        * float(arch_height_ratio),
        physical_panel_height,
    )

    arch_height = (
        physical_arch_height
        / wall_height
    )

    straight_height = (
        panel_height - arch_height
    )

    if straight_height <= 0.0:
        raise ValueError(
            "arched panel has no straight body"
        )

    def point_at(
        u_value,
        v_value,
        offset,
    ):
        one_minus_u = 1.0 - u_value
        one_minus_v = 1.0 - v_value

        base_point = tuple(
            (
                bottom_left[axis]
                * one_minus_u
                * one_minus_v
                + bottom_right[axis]
                * u_value
                * one_minus_v
                + top_right[axis]
                * u_value
                * v_value
                + top_left[axis]
                * one_minus_u
                * v_value
            )
            for axis in range(3)
        )

        return (
            base_point[0]
            + normal[0] * offset,
            base_point[1]
            + normal[1] * offset,
            base_point[2]
            + normal[2] * offset,
        )

    component_meshes = []
    triangles = []

    for row_index in range(row_count):
        for column_index in range(
            column_count
        ):
            center_u = (
                horizontal_margin_ratio
                + cell_u
                * (column_index + 0.5)
            )

            center_v = (
                vertical_margin_ratio
                + cell_v
                * (row_index + 0.5)
            )

            if vertical_alignment == "bottom":
                center_v = (
                    panel_height * 0.5
                    + cell_v * row_index
                )

            u_min = (
                center_u - panel_width * 0.5
            )

            u_max = (
                center_u + panel_width * 0.5
            )

            v_min = (
                center_v - panel_height * 0.5
            )

            spring_v = (
                v_min + straight_height
            )

            profile = [
                (u_min, v_min),
                (u_max, v_min),
                (u_max, spring_v),
            ]

            arch_radius_u = (
                panel_width * 0.5
            )

            for segment_index in range(
                1,
                arch_segments + 1,
            ):
                angle = (
                    pi
                    * segment_index
                    / arch_segments
                )

                profile.append(
                    (
                        center_u
                        + cos(angle)
                        * arch_radius_u,
                        spring_v
                        + sin(angle)
                        * arch_height,
                    )
                )

            back_offset = -embed_mm

            front_offset = (
                depth_mm - embed_mm
            )

            back = [
                point_at(
                    u_value,
                    v_value,
                    back_offset,
                )
                for u_value, v_value in profile
            ]

            front = [
                point_at(
                    u_value,
                    v_value,
                    front_offset,
                )
                for u_value, v_value in profile
            ]

            component_triangles = []

            for index in range(
                1,
                len(profile) - 1,
            ):
                component_triangles.append(
                    (
                        back[0],
                        back[index + 1],
                        back[index],
                    )
                )

                component_triangles.append(
                    (
                        front[0],
                        front[index],
                        front[index + 1],
                    )
                )

            for index in range(len(profile)):
                next_index = (
                    index + 1
                ) % len(profile)

                component_triangles.extend(
                    [
                        (
                            back[index],
                            back[next_index],
                            front[next_index],
                        ),
                        (
                            back[index],
                            front[next_index],
                            front[index],
                        ),
                    ]
                )

            component = {
                "triangles": (
                    component_triangles
                ),
                "back": back,
                "front": front,
                "row_index": row_index,
                "column_index": (
                    column_index
                ),
                "depth_mm": depth_mm,
                "embed_mm": embed_mm,
                "arch_segments": arch_segments,
                "arch_height_ratio": float(
                    arch_height_ratio
                ),
                "physical_arch_height": (
                    physical_arch_height
                ),
                "component_type": (
                    "arched_facade_panel"
                ),
                "source_system": (
                    "facade_panel_builder"
                ),
                "geometry_type": (
                    "arched_facade_panel_prism"
                ),
            }

            if metadata:
                component.update(
                    dict(metadata)
                )

            component_meshes.append(
                component
            )

            triangles.extend(
                component_triangles
            )

    return {
        "triangles": triangles,
        "component_meshes": (
            component_meshes
        ),
        "panel_count": len(
            component_meshes
        ),
        "column_count": column_count,
        "row_count": row_count,
        "depth_mm": depth_mm,
        "embed_mm": embed_mm,
        "arch_segments": arch_segments,
        "vertical_alignment": vertical_alignment,
        "arch_height_ratio": float(
            arch_height_ratio
        ),
        "physical_arch_height": (
            physical_arch_height
        ),
        "geometry_type": (
            "repeated_arched_facade_panels"
        ),
    }


AtlasFacadePanelBuilder.build_repeated_arches = (
    staticmethod(_build_repeated_arches)
)
