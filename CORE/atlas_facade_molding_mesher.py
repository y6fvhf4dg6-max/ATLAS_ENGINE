from __future__ import annotations

from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadeMoldingMesher:
    DEFAULT_HEIGHT_RATIO = 0.08
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
        center_v,
        height_ratio=None,
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
        center_v = float(center_v)
        height_ratio = (
            cls.DEFAULT_HEIGHT_RATIO
            if height_ratio is None
            else float(height_ratio)
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

        if not 0.0 <= u_min < u_max <= 1.0:
            raise ValueError(
                "horizontal bounds must satisfy "
                "0 <= u_min < u_max <= 1"
            )

        if not 0.0 <= center_v <= 1.0:
            raise ValueError(
                "center_v must satisfy 0 <= center_v <= 1"
            )

        if not 0.0 < height_ratio <= 1.0:
            raise ValueError(
                "height_ratio must satisfy 0 < ratio <= 1"
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        half_height = height_ratio / 2.0
        v_min = center_v - half_height
        v_max = center_v + half_height

        if v_min < 0.0 or v_max > 1.0:
            raise ValueError(
                "molding vertical bounds exceed wall"
            )

        component_metadata = {
            "component_type": "facade_molding",
            "molding_profile": "rectangular_band",
            "source_system": "facade_molding_mesher",
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
            "molding_count": 1,
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": "facade_molding_system",
        }
