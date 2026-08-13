from __future__ import annotations

from pathlib import Path

from CORE.atlas_premium_gift_box_mesher import (
    AtlasPremiumGiftBoxMesher,
)
from CORE.atlas_premium_gift_box_spec import (
    AtlasPremiumGiftBoxSpec,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasPremiumGiftBoxSTLExporter:
    @staticmethod
    def export(
        *,
        spec: AtlasPremiumGiftBoxSpec,
        output_directory,
        product_name: str,
    ) -> dict:
        resolved_name = str(product_name).strip()

        if not resolved_name:
            raise ValueError("product_name must not be empty")

        output_directory = Path(output_directory)
        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        base_mesh = AtlasPremiumGiftBoxMesher.build_base(
            spec=spec,
        )
        lid_mesh = AtlasPremiumGiftBoxMesher.build_lid(
            spec=spec,
        )

        base_output_path = (
            output_directory
            / f"{resolved_name}_BASE.stl"
        )
        lid_output_path = (
            output_directory
            / f"{resolved_name}_LID.stl"
        )

        AtlasSTLWriter.write(
            meshes=[base_mesh],
            output_path=base_output_path,
            solid_name="ATLAS_PREMIUM_GIFT_BOX_BASE",
        )

        AtlasSTLWriter.write(
            meshes=[lid_mesh],
            output_path=lid_output_path,
            solid_name="ATLAS_PREMIUM_GIFT_BOX_LID",
        )

        return {
            "type": "premium_gift_box_stl_package",
            "base_output_path": base_output_path,
            "lid_output_path": lid_output_path,
            "base_triangle_count": len(
                base_mesh["triangles"]
            ),
            "lid_triangle_count": len(
                lid_mesh["triangles"]
            ),
            "base_outer_width_mm": (
                spec.outer_width_mm
            ),
            "base_outer_height_mm": (
                spec.outer_height_mm
            ),
            "base_total_depth_mm": (
                spec.base_total_depth_mm
            ),
            "lid_outer_width_mm": (
                spec.lid_outer_width_mm
            ),
            "lid_outer_height_mm": (
                spec.lid_outer_height_mm
            ),
            "lid_total_depth_mm": (
                spec.lid_total_depth_mm
            ),
        }
