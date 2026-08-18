from __future__ import annotations

from CORE.atlas_closed_cylinder_builder import (
    AtlasClosedCylinderBuilder,
)


class AtlasClassicalColumnDetailMesher:
    @classmethod
    def build(
        cls,
        *,
        center_x,
        center_y,
        shaft_base_z,
        shaft_top_z,
        base_diameter_mm,
        base_height_mm,
        capital_diameter_mm,
        capital_height_mm,
        segments=None,
        metadata=None,
    ):
        center_x = float(center_x)
        center_y = float(center_y)
        shaft_base_z = float(shaft_base_z)
        shaft_top_z = float(shaft_top_z)
        base_diameter_mm = float(base_diameter_mm)
        base_height_mm = float(base_height_mm)
        capital_diameter_mm = float(
            capital_diameter_mm
        )
        capital_height_mm = float(
            capital_height_mm
        )

        if shaft_top_z <= shaft_base_z:
            raise ValueError(
                "shaft_top_z must be greater than shaft_base_z"
            )

        for field_name, value in (
            ("base_diameter_mm", base_diameter_mm),
            ("base_height_mm", base_height_mm),
            ("capital_diameter_mm", capital_diameter_mm),
            ("capital_height_mm", capital_height_mm),
        ):
            if value <= 0.0:
                raise ValueError(
                    f"{field_name} must be greater than zero"
                )

        base_metadata = {
            "component_type": "classical_column_detail",
            "detail_role": "base",
            "source_system": "classical_column_detail_mesher",
        }
        capital_metadata = {
            "component_type": "classical_column_detail",
            "detail_role": "capital",
            "source_system": "classical_column_detail_mesher",
        }

        if metadata:
            extra = dict(metadata)
            base_metadata.update(extra)
            capital_metadata.update(extra)

        base = AtlasClosedCylinderBuilder.build(
            center_x=center_x,
            center_y=center_y,
            base_z=shaft_base_z - base_height_mm,
            radius=base_diameter_mm / 2.0,
            height=base_height_mm,
            segments=segments,
            metadata=base_metadata,
        )

        capital = AtlasClosedCylinderBuilder.build(
            center_x=center_x,
            center_y=center_y,
            base_z=shaft_top_z,
            radius=capital_diameter_mm / 2.0,
            height=capital_height_mm,
            segments=segments,
            metadata=capital_metadata,
        )

        return {
            "triangles": (
                list(base["triangles"])
                + list(capital["triangles"])
            ),
            "component_meshes": (
                base,
                capital,
            ),
            "base": base,
            "capital": capital,
            "geometry_type": (
                "classical_column_detail_system"
            ),
        }
