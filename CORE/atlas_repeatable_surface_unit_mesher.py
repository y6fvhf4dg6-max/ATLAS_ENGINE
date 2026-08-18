from __future__ import annotations

from CORE.atlas_geometric_ornament_mesher import (
    AtlasGeometricOrnamentMesher,
)


class AtlasRepeatableSurfaceUnitMesher:
    ALLOWED_UNIT_KINDS = {
        "brick",
        "stone_block",
        "roof_tile",
        "generic",
    }

    @classmethod
    def build(
        cls,
        *,
        center_x,
        center_y,
        base_z,
        width_mm,
        height_mm,
        depth_mm,
        unit_kind,
        metadata=None,
    ):
        center_x = float(center_x)
        center_y = float(center_y)
        base_z = float(base_z)
        width_mm = float(width_mm)
        height_mm = float(height_mm)
        depth_mm = float(depth_mm)
        unit_kind = str(unit_kind).strip().lower()

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

        if unit_kind not in cls.ALLOWED_UNIT_KINDS:
            raise ValueError(
                "unsupported unit_kind"
            )

        half_width = width_mm / 2.0
        half_height = height_mm / 2.0

        result_metadata = {
            "component_type": "repeatable_surface_unit",
            "unit_kind": unit_kind,
            "source_system": "repeatable_surface_unit_mesher",
            "geometry_type": "rectangular_surface_unit",
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
                    center_y - half_height,
                ),
                (
                    center_x + half_width,
                    center_y - half_height,
                ),
                (
                    center_x + half_width,
                    center_y + half_height,
                ),
                (
                    center_x - half_width,
                    center_y + half_height,
                ),
            ),
            base_z=base_z,
            depth_mm=depth_mm,
            metadata=result_metadata,
        )
