from __future__ import annotations

from CORE.atlas_facade_cornice_layout import (
    AtlasFacadeCorniceAnalysis,
)
from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadeCorniceMesher:
    DEFAULT_BAND_HEIGHT_MM = 0.40
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
        cornice_analysis,
        band_height_mm=None,
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
            cornice_analysis,
            AtlasFacadeCorniceAnalysis,
        ):
            raise TypeError(
                "cornice_analysis must be an "
                "AtlasFacadeCorniceAnalysis instance"
            )

        band_height_mm = (
            cls.DEFAULT_BAND_HEIGHT_MM
            if band_height_mm is None
            else float(band_height_mm)
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

        if band_height_mm <= 0.0:
            raise ValueError(
                "band_height_mm must be greater than zero"
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

        for cornice in (
            cornice_analysis.cornices
        ):
            if cornice.cornice_kind == "top_cornice":
                band_min_z = max(
                    wall_min_z,
                    cornice.z - band_height_mm,
                )
                band_max_z = min(
                    wall_max_z,
                    cornice.z,
                )
            else:
                half_band = (
                    band_height_mm / 2.0
                )
                band_min_z = max(
                    wall_min_z,
                    cornice.z - half_band,
                )
                band_max_z = min(
                    wall_max_z,
                    cornice.z + half_band,
                )

            if band_max_z <= band_min_z:
                raise ValueError(
                    "cornice band has no measurable height"
                )

            v_min = (
                band_min_z - wall_min_z
            ) / wall_height
            v_max = (
                band_max_z - wall_min_z
            ) / wall_height

            component_metadata = {
                "component_type": "facade_cornice",
                "cornice_index": (
                    cornice.cornice_index
                ),
                "boundary_level_index": (
                    cornice.boundary_level_index
                ),
                "cornice_kind": (
                    cornice.cornice_kind
                ),
                "cornice_z": cornice.z,
                "band_height_mm": (
                    band_height_mm
                ),
                "source_system": (
                    "facade_cornice_mesher"
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
                    u_min=cornice.u_min,
                    u_max=cornice.u_max,
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
            "cornice_count": len(
                component_meshes
            ),
            "band_height_mm": (
                band_height_mm
            ),
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "geometry_type": (
                "facade_cornice_system"
            ),
        }
