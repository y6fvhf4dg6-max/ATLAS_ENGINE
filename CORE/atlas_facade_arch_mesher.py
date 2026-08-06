from __future__ import annotations

from CORE.atlas_facade_opening_layout import (
    AtlasFacadeOpeningAnalysis,
)
from CORE.atlas_facade_panel_builder import (
    AtlasFacadePanelBuilder,
)


class AtlasFacadeArchMesher:
    DEFAULT_DEPTH_MM = 0.18
    DEFAULT_EMBED_MM = 0.04
    DEFAULT_ARCH_SEGMENTS = 8
    DEFAULT_ARCH_HEIGHT_RATIO = 1.0

    @staticmethod
    def _point_at(
        wall_quad,
        u_value,
        v_value,
    ):
        bottom_left = wall_quad[0]
        bottom_right = wall_quad[1]
        top_right = wall_quad[2]
        top_left = wall_quad[3]

        one_minus_u = 1.0 - u_value
        one_minus_v = 1.0 - v_value

        return tuple(
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

    @classmethod
    def _opening_global_bounds(
        cls,
        opening,
    ):
        u_min = (
            opening.bay_u_min
            + opening.u_min
            * (
                opening.bay_u_max
                - opening.bay_u_min
            )
        )
        u_max = (
            opening.bay_u_min
            + opening.u_max
            * (
                opening.bay_u_max
                - opening.bay_u_min
            )
        )
        v_min = (
            opening.floor_v_min
            + opening.v_min
            * (
                opening.floor_v_max
                - opening.floor_v_min
            )
        )
        v_max = (
            opening.floor_v_min
            + opening.v_max
            * (
                opening.floor_v_max
                - opening.floor_v_min
            )
        )

        return (
            u_min,
            u_max,
            v_min,
            v_max,
        )

    @classmethod
    def build(
        cls,
        *,
        wall_quad,
        opening_analysis,
        depth_mm=None,
        embed_mm=None,
        arch_segments=None,
        arch_height_ratio=None,
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
            opening_analysis,
            AtlasFacadeOpeningAnalysis,
        ):
            raise TypeError(
                "opening_analysis must be an "
                "AtlasFacadeOpeningAnalysis instance"
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
        arch_segments = (
            cls.DEFAULT_ARCH_SEGMENTS
            if arch_segments is None
            else int(arch_segments)
        )
        arch_height_ratio = (
            cls.DEFAULT_ARCH_HEIGHT_RATIO
            if arch_height_ratio is None
            else float(arch_height_ratio)
        )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        if embed_mm < 0.0:
            raise ValueError(
                "embed_mm must be non-negative"
            )

        if arch_segments < 3:
            raise ValueError(
                "arch_segments must be at least three"
            )

        if arch_height_ratio <= 0.0:
            raise ValueError(
                "arch_height_ratio must be positive"
            )

        component_meshes = []
        triangles = []

        for opening in opening_analysis.openings:
            if opening.opening_kind != "arch":
                raise ValueError(
                    "facade arch mesher requires "
                    "opening_kind=arch"
                )

            (
                u_min,
                u_max,
                v_min,
                v_max,
            ) = cls._opening_global_bounds(
                opening
            )

            opening_wall_quad = (
                cls._point_at(
                    wall_quad,
                    u_min,
                    v_min,
                ),
                cls._point_at(
                    wall_quad,
                    u_max,
                    v_min,
                ),
                cls._point_at(
                    wall_quad,
                    u_max,
                    v_max,
                ),
                cls._point_at(
                    wall_quad,
                    u_min,
                    v_max,
                ),
            )

            component_metadata = {
                "component_type": "facade_arch",
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
                    "facade_arch_mesher"
                ),
            }

            if metadata:
                component_metadata.update(
                    dict(metadata)
                )

            arch_result = (
                AtlasFacadePanelBuilder
                .build_repeated_arches(
                    wall_quad=opening_wall_quad,
                    column_count=1,
                    row_count=1,
                    panel_width_ratio=1.0,
                    panel_height_ratio=1.0,
                    arch_height_ratio=(
                        arch_height_ratio
                    ),
                    horizontal_margin_ratio=0.0,
                    vertical_margin_ratio=0.0,
                    vertical_alignment="center",
                    depth_mm=depth_mm,
                    embed_mm=embed_mm,
                    arch_segments=arch_segments,
                    metadata=(
                        component_metadata
                    ),
                )
            )

            component = (
                arch_result[
                    "component_meshes"
                ][0]
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
            "arch_count": len(
                component_meshes
            ),
            "depth_mm": depth_mm,
            "embed_mm": embed_mm,
            "arch_segments": arch_segments,
            "arch_height_ratio": (
                arch_height_ratio
            ),
            "geometry_type": (
                "facade_arch_system"
            ),
        }
