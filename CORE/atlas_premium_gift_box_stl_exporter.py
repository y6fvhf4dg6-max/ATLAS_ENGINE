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
        middle_module_capacities_mm=(),
        personalization_lines=(),
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

        resolved_capacities = tuple(
            spec.validate_middle_module_capacity(
                capacity_mm
            )
            for capacity_mm in middle_module_capacities_mm
        )
        middle_module_meshes = tuple(
            AtlasPremiumGiftBoxMesher.build_middle_module(
                spec=spec,
                product_capacity_mm=capacity_mm,
            )
            for capacity_mm in resolved_capacities
        )

        if personalization_lines:
            resolved_personalization_lines = (
                spec.validate_personalization_lines(
                    personalization_lines
                )
            )
            personalization_plate_mesh = (
                AtlasPremiumGiftBoxMesher.build_personalization_plate(
                    spec=spec,
                )
            )
            personalization_text_meshes = tuple(
                AtlasPremiumGiftBoxMesher.build_personalization_text(
                    spec=spec,
                    lines=resolved_personalization_lines,
                )
            )
        else:
            resolved_personalization_lines = ()
            personalization_plate_mesh = None
            personalization_text_meshes = ()

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

        middle_module_output_paths = []

        for index, (
            capacity_mm,
            module_mesh,
        ) in enumerate(
            zip(
                resolved_capacities,
                middle_module_meshes,
            ),
            start=1,
        ):
            capacity_label = int(round(capacity_mm))
            module_output_path = (
                output_directory
                / (
                    f"{resolved_name}_MIDDLE_"
                    f"{capacity_label}MM_{index:02d}.stl"
                )
            )

            AtlasSTLWriter.write(
                meshes=[module_mesh],
                output_path=module_output_path,
                solid_name=(
                    "ATLAS_PREMIUM_GIFT_BOX_"
                    f"MIDDLE_{capacity_label}MM"
                ),
            )
            middle_module_output_paths.append(
                module_output_path
            )

        personalization_plate_output_path = None
        personalization_text_output_path = None

        if personalization_plate_mesh is not None:
            personalization_plate_output_path = (
                output_directory
                / (
                    f"{resolved_name}_"
                    "PERSONALIZATION_PLATE.stl"
                )
            )
            personalization_text_output_path = (
                output_directory
                / (
                    f"{resolved_name}_"
                    "PERSONALIZATION_TEXT.stl"
                )
            )

            AtlasSTLWriter.write(
                meshes=[personalization_plate_mesh],
                output_path=(
                    personalization_plate_output_path
                ),
                solid_name=(
                    "ATLAS_PREMIUM_GIFT_BOX_"
                    "PERSONALIZATION_PLATE"
                ),
            )
            AtlasSTLWriter.write(
                meshes=list(personalization_text_meshes),
                output_path=(
                    personalization_text_output_path
                ),
                solid_name=(
                    "ATLAS_PREMIUM_GIFT_BOX_"
                    "PERSONALIZATION_TEXT"
                ),
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
            "middle_module_capacities_mm": (
                resolved_capacities
            ),
            "middle_module_output_paths": tuple(
                middle_module_output_paths
            ),
            "middle_module_triangle_counts": tuple(
                len(mesh["triangles"])
                for mesh in middle_module_meshes
            ),
            "personalization_lines": (
                resolved_personalization_lines
            ),
            "personalization_plate_output_path": (
                personalization_plate_output_path
            ),
            "personalization_text_output_path": (
                personalization_text_output_path
            ),
            "personalization_plate_triangle_count": (
                len(personalization_plate_mesh["triangles"])
                if personalization_plate_mesh is not None
                else 0
            ),
            "personalization_text_triangle_count": sum(
                len(mesh["triangles"])
                for mesh in personalization_text_meshes
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
