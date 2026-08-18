from __future__ import annotations

from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadePilasterMesher:
    DEFAULT_WIDTH_RATIO = 0.12
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
        center_u,
        width_ratio=None,
        v_min=0.0,
        v_max=1.0,
        depth_mm=None,
        embed_mm=None,
        metadata=None,
    ):
        if not wall_quad or len(wall_quad) != 4:
            raise ValueError(
                "wall_quad must contain four points"
            )

        center_u = float(center_u)
        width_ratio = (
            cls.DEFAULT_WIDTH_RATIO
            if width_ratio is None
            else float(width_ratio)
        )
        v_min = float(v_min)
        v_max = float(v_max)
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

        if not 0.0 <= center_u <= 1.0:
            raise ValueError(
                "center_u must be in the range [0, 1]"
            )

        if not 0.0 < width_ratio <= 1.0:
            raise ValueError(
                "width_ratio must be in the range (0, 1]"
            )

        if not 0.0 <= v_min < v_max <= 1.0:
            raise ValueError(
                "vertical bounds must satisfy "
                "0 <= v_min < v_max <= 1"
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        half_width = width_ratio * 0.5
        u_min = center_u - half_width
        u_max = center_u + half_width

        if u_min < 0.0 or u_max > 1.0:
            raise ValueError(
                "pilaster exceeds facade horizontal bounds"
            )

        component_metadata = {
            "component_type": "facade_pilaster",
            "source_system": "facade_pilaster_mesher",
        }

        if metadata:
            component_metadata.update(
                dict(metadata)
            )

        component = (
            AtlasFacadePanelBuilder
            ._build_panel_prism(
                wall_quad=wall_quad,
                normal=cls._wall_normal(wall_quad),
                u_min=u_min,
                u_max=u_max,
                v_min=v_min,
                v_max=v_max,
                depth_mm=depth_mm,
                embed_mm=embed_mm,
                metadata=component_metadata,
            )
        )

        return {
            "triangles": component["triangles"],
            "component_meshes": (component,),
            "pilaster_count": 1,
            "center_u": center_u,
            "width_ratio": width_ratio,
            "v_min": v_min,
            "v_max": v_max,
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": "facade_pilaster_system",
        }
