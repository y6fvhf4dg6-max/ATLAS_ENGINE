from __future__ import annotations

from CORE.atlas_facade_opening_layout import (
    AtlasFacadeOpeningAnalysis,
)
from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadePortalSurroundMesher:
    DEFAULT_SURROUND_WIDTH_RATIO = 0.12
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
        opening_analysis,
        surround_width_ratio=None,
        depth_mm=None,
        embed_mm=None,
        metadata=None,
    ):
        if not wall_quad or len(wall_quad) != 4:
            raise ValueError(
                "wall_quad must contain four points"
            )

        if not isinstance(
            opening_analysis,
            AtlasFacadeOpeningAnalysis,
        ):
            raise TypeError(
                "opening_analysis must be an "
                "AtlasFacadeOpeningAnalysis instance"
            )

        surround_width_ratio = (
            cls.DEFAULT_SURROUND_WIDTH_RATIO
            if surround_width_ratio is None
            else float(surround_width_ratio)
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

        if not 0.0 < surround_width_ratio < 0.5:
            raise ValueError(
                "surround_width_ratio must satisfy "
                "0 < ratio < 0.5"
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        normal = cls._wall_normal(wall_quad)

        component_meshes = []
        triangles = []

        for opening in opening_analysis.openings:
            opening_u_min = (
                opening.bay_u_min
                + opening.u_min
                * (
                    opening.bay_u_max
                    - opening.bay_u_min
                )
            )
            opening_u_max = (
                opening.bay_u_min
                + opening.u_max
                * (
                    opening.bay_u_max
                    - opening.bay_u_min
                )
            )
            opening_v_min = (
                opening.floor_v_min
                + opening.v_min
                * (
                    opening.floor_v_max
                    - opening.floor_v_min
                )
            )
            opening_v_max = (
                opening.floor_v_min
                + opening.v_max
                * (
                    opening.floor_v_max
                    - opening.floor_v_min
                )
            )

            opening_u_span = (
                opening_u_max - opening_u_min
            )
            opening_v_span = (
                opening_v_max - opening_v_min
            )

            jamb_width = (
                opening_u_span
                * surround_width_ratio
            )
            lintel_height = (
                opening_v_span
                * surround_width_ratio
            )

            parts = (
                (
                    "left_jamb",
                    opening_u_min,
                    opening_u_min + jamb_width,
                    opening_v_min,
                    opening_v_max,
                ),
                (
                    "right_jamb",
                    opening_u_max - jamb_width,
                    opening_u_max,
                    opening_v_min,
                    opening_v_max,
                ),
                (
                    "lintel",
                    opening_u_min + jamb_width,
                    opening_u_max - jamb_width,
                    opening_v_max - lintel_height,
                    opening_v_max,
                ),
            )

            for (
                surround_part,
                u_min,
                u_max,
                v_min,
                v_max,
            ) in parts:
                component_metadata = {
                    "component_type": (
                        "facade_portal_surround"
                    ),
                    "surround_part": surround_part,
                    "opening_kind": (
                        opening.opening_kind
                    ),
                    "level_index": (
                        opening.level_index
                    ),
                    "bay_index": (
                        opening.bay_index
                    ),
                    "opening_index": (
                        opening.opening_index
                    ),
                    "region_name": (
                        opening.region_name
                    ),
                    "source_system": (
                        "facade_portal_surround_mesher"
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
                        metadata=component_metadata,
                    )
                )

                component_meshes.append(component)
                triangles.extend(
                    component["triangles"]
                )

        return {
            "triangles": triangles,
            "component_meshes": component_meshes,
            "portal_count": (
                opening_analysis.opening_count
            ),
            "surround_width_ratio": (
                surround_width_ratio
            ),
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": (
                "facade_portal_surround_system"
            ),
        }
