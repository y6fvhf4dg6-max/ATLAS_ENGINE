from __future__ import annotations

import math

from CORE.atlas_terrain_contour_band_builder import (
    AtlasTerrainContourBandBuilder,
)
from CORE.atlas_linear_infrastructure_resolver import (
    AtlasLinearInfrastructureResolver,
)


class AtlasLinearInfrastructureGeometryBuilder:
    @classmethod
    def build_product_footprint(
        cls,
        *,
        item,
        coordinate_engine,
        profile,
    ):
        geometry = item.get(
            "geometry",
            [],
        )

        if len(geometry) < 2:
            return []

        points = coordinate_engine.geometry_to_stl_mm(
            geometry
        )

        if len(points) < 2:
            return []

        return cls.build_from_source(
            tags=item.get("tags", {}),
            points=points,
            physical_width_mm=(
                profile.physical_width_mm
            ),
        )

    @classmethod
    def build_from_source(
        cls,
        *,
        tags,
        points,
        physical_width_mm,
    ):
        is_closed = (
            len(points) >= 3
            and points[0] == points[-1]
        )

        geometry_kind = (
            AtlasLinearInfrastructureResolver
            .resolve_geometry_kind(
                tags=tags,
                is_closed=is_closed,
            )
        )

        if geometry_kind == "linear_strip":
            return cls.build_linear_strip(
                points=points,
                physical_width_mm=physical_width_mm,
            )

        if geometry_kind == "area_strip":
            return cls.build_area_strip(
                points=points,
            )

        return []

    @staticmethod
    def build_area_strip(
        *,
        points,
    ):
        if len(points) < 4:
            return []

        if points[0] != points[-1]:
            return []

        return list(points)

    @staticmethod
    def build_linear_strip(
        *,
        points,
        physical_width_mm,
    ):
        physical_width_mm = float(
            physical_width_mm
        )

        if (
            not math.isfinite(physical_width_mm)
            or physical_width_mm <= 0.0
        ):
            raise ValueError(
                "physical_width_mm must be finite "
                "and greater than zero"
            )

        if len(points) < 2:
            return []

        return AtlasTerrainContourBandBuilder.build_band(
            polyline=points,
            half_width_mm=(
                physical_width_mm / 2.0
            ),
        )
