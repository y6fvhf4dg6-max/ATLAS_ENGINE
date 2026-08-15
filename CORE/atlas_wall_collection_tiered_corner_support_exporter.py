from __future__ import annotations

from pathlib import Path

from CORE.atlas_wall_collection_tiered_corner_support_mesher import (
    AtlasWallCollectionTieredCornerSupportMesher,
)
from CORE.atlas_wall_collection_tiered_corner_support_spec import (
    AtlasWallCollectionTieredCornerSupportSpec,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasWallCollectionTieredCornerSupportExporter:
    @staticmethod
    def export_universal_module(
        *,
        spec: AtlasWallCollectionTieredCornerSupportSpec,
        output_directory,
    ) -> dict:
        if spec.product_capacity_mm is None:
            raise ValueError(
                "universal module requires product_capacity_mm"
            )

        output_directory = Path(output_directory)
        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        mesh = (
            AtlasWallCollectionTieredCornerSupportMesher
            .build_universal_support(spec=spec)
        )
        capacity_label = int(
            round(spec.product_capacity_mm)
        )
        output_path = (
            output_directory
            / (
                "ATLAS_TIER_CORNER_SUPPORT_"
                f"{capacity_label}MM.stl"
            )
        )

        AtlasSTLWriter.write(
            meshes=[mesh],
            output_path=output_path,
            solid_name=(
                "ATLAS_TIER_CORNER_SUPPORT_"
                f"{capacity_label}MM"
            ),
        )

        return {
            "type": (
                "wall_collection_universal_tiered_"
                "corner_support_master"
            ),
            "output_path": output_path,
            "master_part_count": 1,
            "required_quantity_per_level": 4,
            "product_capacity_mm": (
                spec.product_capacity_mm
            ),
            "next_plate_base_z_mm": (
                spec.next_plate_base_z_mm
            ),
            "total_height_mm": spec.total_height_mm,
            "triangle_count": len(mesh["triangles"]),
        }

    @staticmethod
    def export(
        *,
        spec: AtlasWallCollectionTieredCornerSupportSpec,
        output_directory,
        product_name: str,
        product_width_mm: float,
        product_height_mm: float,
    ) -> dict:
        product_name = str(product_name).strip()

        if not product_name:
            raise ValueError("product_name must not be empty")

        output_directory = Path(output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

        corner_meshes = (
            AtlasWallCollectionTieredCornerSupportMesher.build_set(
                spec=spec,
                product_width_mm=product_width_mm,
                product_height_mm=product_height_mm,
            )
        )
        output_path = (
            output_directory
            / f"{product_name}_TIER_SUPPORT_SET.stl"
        )

        AtlasSTLWriter.write(
            meshes=list(corner_meshes.values()),
            output_path=output_path,
            solid_name=(
                "ATLAS_WALL_COLLECTION_TIER_SUPPORT_SET"
            ),
        )

        return {
            "type": (
                "wall_collection_tiered_corner_support_package"
            ),
            "output_path": output_path,
            "part_count": len(corner_meshes),
            "corners": tuple(corner_meshes),
            "product_width_mm": float(product_width_mm),
            "product_height_mm": float(product_height_mm),
            "next_plate_base_z_mm": spec.next_plate_base_z_mm,
            "total_height_mm": spec.total_height_mm,
            "triangle_count": sum(
                len(mesh["triangles"])
                for mesh in corner_meshes.values()
            ),
        }
