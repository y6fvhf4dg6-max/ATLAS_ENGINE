from __future__ import annotations

import math

from CORE.atlas_geometric_ornament_mesher import (
    AtlasGeometricOrnamentMesher,
)


class AtlasFloralOrnamentMesher:
    @classmethod
    def build(
        cls,
        *,
        center_x,
        center_y,
        outer_diameter_mm,
        inner_ratio,
        petal_count,
        base_z,
        depth_mm,
        metadata=None,
    ):
        center_x = float(center_x)
        center_y = float(center_y)
        outer_diameter_mm = float(
            outer_diameter_mm
        )
        inner_ratio = float(inner_ratio)

        if outer_diameter_mm <= 0.0:
            raise ValueError(
                "outer_diameter_mm must be greater than zero"
            )

        if not 0.0 < inner_ratio < 1.0:
            raise ValueError(
                "inner_ratio must satisfy 0 < ratio < 1"
            )

        if (
            isinstance(petal_count, bool)
            or not isinstance(petal_count, int)
            or petal_count < 3
        ):
            raise ValueError(
                "petal_count must be an integer of at least three"
            )

        outer_radius = (
            outer_diameter_mm / 2.0
        )
        inner_radius = (
            outer_radius * inner_ratio
        )

        point_count = petal_count * 2

        outline_points = tuple(
            (
                center_x
                + math.cos(
                    2.0
                    * math.pi
                    * index
                    / point_count
                )
                * (
                    outer_radius
                    if index % 2 == 0
                    else inner_radius
                ),
                center_y
                + math.sin(
                    2.0
                    * math.pi
                    * index
                    / point_count
                )
                * (
                    outer_radius
                    if index % 2 == 0
                    else inner_radius
                ),
            )
            for index in range(
                point_count
            )
        )

        result_metadata = {
            "component_type": "floral_ornament",
            "source_system": "floral_ornament_mesher",
            "geometry_type": "floral_ornament_prism",
            "petal_count": petal_count,
            "outer_diameter_mm": outer_diameter_mm,
            "inner_ratio": inner_ratio,
        }

        if metadata:
            result_metadata.update(
                dict(metadata)
            )

        return AtlasGeometricOrnamentMesher.build(
            outline_points=outline_points,
            base_z=base_z,
            depth_mm=depth_mm,
            metadata=result_metadata,
        )
