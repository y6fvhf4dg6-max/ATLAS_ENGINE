from __future__ import annotations

from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadeTraceryMesher:
    DEFAULT_MULLION_WIDTH_RATIO = 0.08
    DEFAULT_TRANSOM_HEIGHT_RATIO = 0.08
    DEFAULT_DEPTH_MM = 0.18
    DEFAULT_EMBED_MM = 0.04

    @staticmethod
    def _wall_normal(wall_quad):
        bottom_left = wall_quad[0]
        bottom_right = wall_quad[1]
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
            wall_u[1] * wall_v[2] - wall_u[2] * wall_v[1],
            wall_u[2] * wall_v[0] - wall_u[0] * wall_v[2],
            wall_u[0] * wall_v[1] - wall_u[1] * wall_v[0],
        )

        length = (
            normal[0] ** 2
            + normal[1] ** 2
            + normal[2] ** 2
        ) ** 0.5

        if length <= 0.0:
            raise ValueError("wall_quad is degenerate")

        return (
            normal[0] / length,
            normal[1] / length,
            normal[2] / length,
        )

    @classmethod
    def build(
        cls,
        *,
        wall_quad,
        u_min,
        u_max,
        v_min,
        v_max,
        mullion_width_ratio=None,
        transom_height_ratio=None,
        depth_mm=None,
        embed_mm=None,
        metadata=None,
    ):
        if not wall_quad or len(wall_quad) != 4:
            raise ValueError(
                "wall_quad must contain four points"
            )

        u_min = float(u_min)
        u_max = float(u_max)
        v_min = float(v_min)
        v_max = float(v_max)

        if not 0.0 <= u_min < u_max <= 1.0:
            raise ValueError(
                "horizontal bounds must satisfy "
                "0 <= u_min < u_max <= 1"
            )

        if not 0.0 <= v_min < v_max <= 1.0:
            raise ValueError(
                "vertical bounds must satisfy "
                "0 <= v_min < v_max <= 1"
            )

        mullion_width_ratio = (
            cls.DEFAULT_MULLION_WIDTH_RATIO
            if mullion_width_ratio is None
            else float(mullion_width_ratio)
        )
        transom_height_ratio = (
            cls.DEFAULT_TRANSOM_HEIGHT_RATIO
            if transom_height_ratio is None
            else float(transom_height_ratio)
        )
        depth_mm = (
            cls.DEFAULT_DEPTH_MM
            if depth_mm is None
            else float(depth_mm)
        )
        embed_mm = (
            cls.DEFAULT_EMBED_MM
            if embed_mm is None
            else float(embed_mm)
        )

        if not 0.0 < mullion_width_ratio < 1.0:
            raise ValueError(
                "mullion_width_ratio must satisfy "
                "0 < ratio < 1"
            )

        if not 0.0 < transom_height_ratio < 1.0:
            raise ValueError(
                "transom_height_ratio must satisfy "
                "0 < ratio < 1"
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        u_span = u_max - u_min
        v_span = v_max - v_min

        center_u = (u_min + u_max) / 2.0
        center_v = (v_min + v_max) / 2.0

        mullion_half_width = (
            u_span * mullion_width_ratio / 2.0
        )
        transom_half_height = (
            v_span * transom_height_ratio / 2.0
        )

        parts = (
            (
                "mullion",
                center_u - mullion_half_width,
                center_u + mullion_half_width,
                v_min,
                v_max,
            ),
            (
                "transom",
                u_min,
                u_max,
                center_v - transom_half_height,
                center_v + transom_half_height,
            ),
        )

        normal = cls._wall_normal(wall_quad)

        component_meshes = []
        triangles = []

        for (
            tracery_part,
            part_u_min,
            part_u_max,
            part_v_min,
            part_v_max,
        ) in parts:
            component_metadata = {
                "component_type": "facade_tracery",
                "tracery_part": tracery_part,
                "source_system": "facade_tracery_mesher",
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
                    u_min=part_u_min,
                    u_max=part_u_max,
                    v_min=part_v_min,
                    v_max=part_v_max,
                    depth_mm=depth_mm,
                    embed_mm=embed_mm,
                    metadata=component_metadata,
                )
            )

            component_meshes.append(component)
            triangles.extend(
                component["triangles"]
            )

        return {
            "triangles": triangles,
            "component_meshes": tuple(component_meshes),
            "tracery_count": len(component_meshes),
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": "facade_tracery_system",
        }
