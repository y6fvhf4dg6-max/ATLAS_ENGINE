from __future__ import annotations

from CORE.atlas_geometric_ornament_mesher import (
    AtlasGeometricOrnamentMesher,
)


class AtlasTympanumMesher:
    @classmethod
    def build(
        cls,
        *,
        center_x,
        base_z,
        width_mm,
        height_mm,
        depth_mm,
        metadata=None,
    ):
        center_x = float(center_x)
        base_z = float(base_z)
        width_mm = float(width_mm)
        height_mm = float(height_mm)
        depth_mm = float(depth_mm)

        if width_mm <= 0.0:
            raise ValueError(
                "width_mm must be greater than zero"
            )

        if height_mm <= 0.0:
            raise ValueError(
                "height_mm must be greater than zero"
            )

        if depth_mm <= 0.0:
            raise ValueError(
                "depth_mm must be greater than zero"
            )

        half_width = width_mm / 2.0

        result_metadata = {
            "component_type": "tympanum",
            "source_system": "tympanum_mesher",
            "geometry_type": "tympanum_prism",
            "width_mm": width_mm,
            "height_mm": height_mm,
        }

        if metadata:
            result_metadata.update(
                dict(metadata)
            )

        return AtlasGeometricOrnamentMesher.build(
            outline_points=(
                (
                    center_x - half_width,
                    base_z,
                ),
                (
                    center_x + half_width,
                    base_z,
                ),
                (
                    center_x,
                    base_z + height_mm,
                ),
            ),
            base_z=0.0,
            depth_mm=depth_mm,
            metadata=result_metadata,
        )
