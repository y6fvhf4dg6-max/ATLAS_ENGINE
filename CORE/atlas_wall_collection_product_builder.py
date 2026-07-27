from __future__ import annotations

from copy import deepcopy

from CORE.atlas_label_plate_mesher import AtlasLabelPlateMesher
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_wall_frame_mesher import AtlasWallFrameMesher
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


class AtlasWallCollectionProductBuilder:
    OPENING_TOLERANCE_MM = 0.001

    @staticmethod
    def _translate_mesh(
        mesh,
        offset_x_mm,
        offset_y_mm,
        offset_z_mm=0.0,
    ):
        translated = deepcopy(mesh)

        if "triangles" in translated:
            translated["triangles"] = [
                tuple(
                    (
                        float(x) + offset_x_mm,
                        float(y) + offset_y_mm,
                        float(z) + offset_z_mm,
                    )
                    for x, y, z in triangle
                )
                for triangle in translated["triangles"]
            ]

        return translated

    @staticmethod
    def build(
        *,
        city_result: dict,
        frame_spec: AtlasWallFrameSpec,
        frame_depth_mm: float,
        label_plate_spec: AtlasLabelPlateSpec | None = None,
    ) -> dict:
        terrain_size_x_mm = float(
            city_result["terrain_size_x_mm"]
        )
        terrain_size_y_mm = float(
            city_result["terrain_size_y_mm"]
        )

        if (
            terrain_size_x_mm
            > frame_spec.inner_width_mm
            + AtlasWallCollectionProductBuilder.OPENING_TOLERANCE_MM
        ):
            raise ValueError(
                "city terrain width exceeds frame opening"
            )

        if (
            terrain_size_y_mm
            > frame_spec.inner_height_mm
            + AtlasWallCollectionProductBuilder.OPENING_TOLERANCE_MM
        ):
            raise ValueError(
                "city terrain height exceeds frame opening"
            )

        city_offset_x_mm = -(terrain_size_x_mm / 2.0)
        city_offset_y_mm = -(terrain_size_y_mm / 2.0)

        city_meshes = []

        for meshes in city_result["mesh_groups"].values():
            for mesh in meshes:
                city_meshes.append(
                    AtlasWallCollectionProductBuilder._translate_mesh(
                        mesh,
                        city_offset_x_mm,
                        city_offset_y_mm,
                    )
                )

        frame_mesh = AtlasWallFrameMesher.build(
            spec=frame_spec,
            depth_mm=frame_depth_mm,
        )

        frame_meshes = [frame_mesh]

        label_plate_meshes = []

        if label_plate_spec is not None:
            if label_plate_spec.width_mm > frame_spec.inner_width_mm:
                raise ValueError(
                    "label plate width exceeds frame inner width"
                )

            label_center_y_mm = (
                -(frame_spec.outer_height_mm / 2.0)
                + frame_spec.frame_width_mm
                + (label_plate_spec.height_mm / 2.0)
            )

            label_plate_mesh = AtlasLabelPlateMesher.build(
                spec=label_plate_spec,
            )
            label_plate_meshes.append(
                AtlasWallCollectionProductBuilder._translate_mesh(
                    label_plate_mesh,
                    0.0,
                    label_center_y_mm,
                    float(frame_depth_mm),
                )
            )

        meshes = [
            *frame_meshes,
            *city_meshes,
            *label_plate_meshes,
        ]

        return {
            "type": "wall_collection_product",
            "outer_width_mm": frame_spec.outer_width_mm,
            "outer_height_mm": frame_spec.outer_height_mm,
            "opening_width_mm": frame_spec.inner_width_mm,
            "opening_height_mm": frame_spec.inner_height_mm,
            "frame_depth_mm": float(frame_depth_mm),
            "city_offset_x_mm": city_offset_x_mm,
            "city_offset_y_mm": city_offset_y_mm,
            "frame_meshes": frame_meshes,
            "city_meshes": city_meshes,
            "label_plate_meshes": label_plate_meshes,
            "meshes": meshes,
        }
