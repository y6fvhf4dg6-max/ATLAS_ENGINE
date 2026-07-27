from __future__ import annotations

from CORE.atlas_wall_collection_product_builder import (
    AtlasWallCollectionProductBuilder,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasWallCollectionSTLExporter:
    @staticmethod
    def export(
        *,
        city_result: dict,
        output_path,
        frame_spec: AtlasWallFrameSpec,
        frame_depth_mm: float,
    ) -> dict:
        product = AtlasWallCollectionProductBuilder.build(
            city_result=city_result,
            frame_spec=frame_spec,
            frame_depth_mm=frame_depth_mm,
        )

        AtlasSTLWriter.write(
            meshes=product["meshes"],
            output_path=output_path,
            solid_name="ATLAS_WALL_COLLECTION",
        )

        return {
            "type": product["type"],
            "output_path": output_path,
            "mesh_count": len(product["meshes"]),
            "outer_width_mm": product["outer_width_mm"],
            "outer_height_mm": product["outer_height_mm"],
            "opening_width_mm": product["opening_width_mm"],
            "opening_height_mm": product["opening_height_mm"],
            "frame_depth_mm": product["frame_depth_mm"],
            "city_offset_x_mm": product["city_offset_x_mm"],
            "city_offset_y_mm": product["city_offset_y_mm"],
        }
