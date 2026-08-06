from __future__ import annotations

from CORE.atlas_facade_bay_analyzer import (
    AtlasFacadeBayAnalysis,
)
from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadePanelLayoutMesher:
    DEFAULT_HORIZONTAL_MARGIN_RATIO = 0.12
    DEFAULT_VERTICAL_MARGIN_RATIO = 0.15
    DEFAULT_DEPTH_MM = (
        AtlasFacadePanelBuilder.DEFAULT_DEPTH_MM
    )
    DEFAULT_EMBED_MM = (
        AtlasFacadePanelBuilder.DEFAULT_EMBED_MM
    )

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
        z_values = tuple(
            float(point[2])
            for point in wall_quad
        )

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
        bay_analysis,
        horizontal_margin_ratio=None,
        vertical_margin_ratio=None,
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
            bay_analysis,
            AtlasFacadeBayAnalysis,
        ):
            raise TypeError(
                "bay_analysis must be an "
                "AtlasFacadeBayAnalysis instance"
            )

        horizontal_margin_ratio = (
            cls.DEFAULT_HORIZONTAL_MARGIN_RATIO
            if horizontal_margin_ratio is None
            else float(horizontal_margin_ratio)
        )
        vertical_margin_ratio = (
            cls.DEFAULT_VERTICAL_MARGIN_RATIO
            if vertical_margin_ratio is None
            else float(vertical_margin_ratio)
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

        if not (
            0.0
            <= horizontal_margin_ratio
            < 0.5
        ):
            raise ValueError(
                "horizontal_margin_ratio must be "
                "in the range [0, 0.5)"
            )

        if not (
            0.0
            <= vertical_margin_ratio
            < 0.5
        ):
            raise ValueError(
                "vertical_margin_ratio must be "
                "in the range [0, 0.5)"
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

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

        for bay in bay_analysis.bays:
            bay_width = (
                bay.u_max - bay.u_min
            )
            bay_height = (
                bay.max_z - bay.min_z
            )

            u_margin = (
                bay_width
                * horizontal_margin_ratio
            )
            z_margin = (
                bay_height
                * vertical_margin_ratio
            )

            u_min = (
                bay.u_min + u_margin
            )
            u_max = (
                bay.u_max - u_margin
            )
            panel_min_z = (
                bay.min_z + z_margin
            )
            panel_max_z = (
                bay.max_z - z_margin
            )

            if (
                u_max <= u_min
                or panel_max_z <= panel_min_z
            ):
                raise ValueError(
                    "panel margins leave no usable bay area"
                )

            v_min = (
                panel_min_z - wall_min_z
            ) / wall_height
            v_max = (
                panel_max_z - wall_min_z
            ) / wall_height

            if (
                v_min < 0.0
                or v_max > 1.0
            ):
                raise ValueError(
                    "bay vertical bounds fall outside wall_quad"
                )

            component_metadata = {
                "component_type": (
                    "facade_panel"
                ),
                "level_index": (
                    bay.level_index
                ),
                "bay_index": (
                    bay.bay_index
                ),
                "region_name": (
                    bay.region_name
                ),
                "bay_u_min": (
                    bay.u_min
                ),
                "bay_u_max": (
                    bay.u_max
                ),
                "bay_min_z": (
                    bay.min_z
                ),
                "bay_max_z": (
                    bay.max_z
                ),
                "horizontal_margin_ratio": (
                    horizontal_margin_ratio
                ),
                "vertical_margin_ratio": (
                    vertical_margin_ratio
                ),
                "source_system": (
                    "facade_panel_layout_mesher"
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
            "level_count": (
                bay_analysis.level_count
            ),
            "bay_count": (
                bay_analysis.bay_count
            ),
            "horizontal_margin_ratio": (
                horizontal_margin_ratio
            ),
            "vertical_margin_ratio": (
                vertical_margin_ratio
            ),
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": (
                "facade_panel_layout_system"
            ),
        }
