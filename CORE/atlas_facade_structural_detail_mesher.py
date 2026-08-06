from __future__ import annotations

from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)
from CORE.atlas_facade_structural_detail_layout import (
    AtlasFacadeStructuralDetailAnalysis,
)


class AtlasFacadeStructuralDetailMesher:
    DEFAULT_DEPTH_MM = 0.24
    DEFAULT_EMBED_MM = 0.04

    @staticmethod
    def _wall_normal(
        wall_quad,
    ):
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
            wall_u[1] * wall_v[2]
            - wall_u[2] * wall_v[1],
            wall_u[2] * wall_v[0]
            - wall_u[0] * wall_v[2],
            wall_u[0] * wall_v[1]
            - wall_u[1] * wall_v[0],
        )

        length = (
            normal[0] ** 2
            + normal[1] ** 2
            + normal[2] ** 2
        ) ** 0.5

        if length <= 0.0:
            raise ValueError(
                "wall_quad is degenerate"
            )

        return (
            normal[0] / length,
            normal[1] / length,
            normal[2] / length,
        )

    @staticmethod
    def _wall_vertical_bounds(
        wall_quad,
    ):
        z_values = [
            float(point[2])
            for point in wall_quad
        ]

        min_z = min(z_values)
        max_z = max(z_values)

        if max_z <= min_z:
            raise ValueError(
                "wall_quad must have measurable height"
            )

        return min_z, max_z

    @classmethod
    def build(
        cls,
        *,
        wall_quad,
        detail_analysis,
        depth_mm=None,
        embed_mm=None,
        metadata=None,
    ):
        if (
            not wall_quad
            or len(wall_quad) != 4
        ):
            raise ValueError(
                "wall_quad must contain four points"
            )

        if not isinstance(
            detail_analysis,
            AtlasFacadeStructuralDetailAnalysis,
        ):
            raise TypeError(
                "detail_analysis must be an "
                "AtlasFacadeStructuralDetailAnalysis instance"
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

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        if detail_analysis.action == "omit":
            return {
                "triangles": [],
                "component_meshes": [],
                "detail_count": 0,
                "detail_kind": (
                    detail_analysis.detail_kind
                ),
                "depth_mm": depth_mm,
                "embed_mm": embed_mm,
                "geometry_type": (
                    "facade_structural_detail_system"
                ),
            }

        normal = cls._wall_normal(
            wall_quad
        )
        wall_min_z, wall_max_z = (
            cls._wall_vertical_bounds(
                wall_quad
            )
        )
        wall_height = (
            wall_max_z - wall_min_z
        )

        component_meshes = []
        triangles = []

        for detail in detail_analysis.details:
            half_width_ratio = (
                detail.resolved_size_mm
                / 2.0
            )

            bottom_left = wall_quad[0]
            bottom_right = wall_quad[1]

            wall_width = (
                (
                    bottom_right[0]
                    - bottom_left[0]
                ) ** 2
                + (
                    bottom_right[1]
                    - bottom_left[1]
                ) ** 2
                + (
                    bottom_right[2]
                    - bottom_left[2]
                ) ** 2
            ) ** 0.5

            if wall_width <= 0.0:
                raise ValueError(
                    "wall_quad must have measurable width"
                )

            half_width_ratio = (
                half_width_ratio
                / wall_width
            )

            u_min = max(
                0.0,
                detail.u_center
                - half_width_ratio,
            )
            u_max = min(
                1.0,
                detail.u_center
                + half_width_ratio,
            )

            if u_max <= u_min:
                raise ValueError(
                    "resolved structural detail has no width"
                )

            v_min = (
                detail.min_z
                - wall_min_z
            ) / wall_height
            v_max = (
                detail.max_z
                - wall_min_z
            ) / wall_height

            component_metadata = {
                "component_type": (
                    "facade_structural_detail"
                ),
                "detail_kind": (
                    detail.detail_kind
                ),
                "detail_index": (
                    detail.detail_index
                ),
                "action": detail.action,
                "resolved_size_mm": (
                    detail.resolved_size_mm
                ),
                "scaled_size_mm": (
                    detail.scaled_size_mm
                ),
                "minimum_printable_mm": (
                    detail.minimum_printable_mm
                ),
                "scale_factor": (
                    detail.scale_factor
                ),
                "source_system": (
                    "facade_structural_detail_mesher"
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
            "detail_count": len(
                component_meshes
            ),
            "detail_kind": (
                detail_analysis.detail_kind
            ),
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": (
                "facade_structural_detail_system"
            ),
        }
