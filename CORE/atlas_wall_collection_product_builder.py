from __future__ import annotations

from copy import deepcopy

from CORE.atlas_label_birthday_cake_mesher import (
    AtlasLabelBirthdayCakeMesher,
)
from CORE.atlas_label_graduation_cap_mesher import (
    AtlasLabelGraduationCapMesher,
)
from CORE.atlas_label_home_mesher import AtlasLabelHomeMesher
from CORE.atlas_label_wedding_rings_mesher import (
    AtlasLabelWeddingRingsMesher,
)
from CORE.atlas_label_plate_mesher import AtlasLabelPlateMesher
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_mesher import AtlasLabelTextMesher
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_wall_frame_hanger_mesher import (
    AtlasWallFrameHangerMesher,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec


class AtlasWallCollectionProductBuilder:
    OPENING_TOLERANCE_MM = 0.001
    LABEL_FRAME_EMBED_MM = 5.0

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
        label_text_spec: AtlasLabelTextSpec | None = None,
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

        hanger_spec = AtlasWallHangerSpec.for_product_size(
            outer_width_mm=frame_spec.outer_width_mm,
            outer_height_mm=frame_spec.outer_height_mm,
            frame_width_mm=frame_spec.frame_width_mm,
            frame_depth_mm=frame_depth_mm,
        )

        label_center_y_mm = None
        label_recess_ring = None
        label_recess_depth_mm = None

        if label_plate_spec is not None:
            label_center_y_mm = (
                -(frame_spec.outer_height_mm / 2.0)
                + (frame_spec.frame_width_mm / 2.0)
            )

            label_outline = (
                AtlasLabelPlateMesher._rounded_outline(
                    width_mm=label_plate_spec.width_mm,
                    height_mm=label_plate_spec.height_mm,
                    corner_radius_mm=(
                        label_plate_spec.corner_radius_mm
                    ),
                )
            )

            label_recess_ring = tuple(
                (
                    float(x),
                    float(y) + label_center_y_mm,
                )
                for x, y in label_outline
            )
            label_recess_depth_mm = 1.0

        frame_mesh = AtlasWallFrameHangerMesher.build(
            frame_spec=frame_spec,
            hanger_spec=hanger_spec,
            frame_depth_mm=frame_depth_mm,
            front_recess_ring=label_recess_ring,
            front_recess_depth_mm=label_recess_depth_mm,
        )

        frame_meshes = [frame_mesh]

        label_plate_meshes = []
        label_text_meshes = []
        label_graduation_cap_meshes = []
        label_birthday_cake_meshes = []
        label_home_meshes = []
        label_wedding_rings_meshes = []

        if label_text_spec is not None and label_plate_spec is None:
            raise ValueError(
                "label text requires label plate"
            )

        if label_plate_spec is not None:
            if label_plate_spec.width_mm > frame_spec.inner_width_mm:
                raise ValueError(
                    "label plate width exceeds frame inner width"
                )

            if (
                label_plate_spec.height_mm
                > frame_spec.frame_width_mm
            ):
                raise ValueError(
                    "label plate height exceeds frame band"
                )

            label_plate_mesh = AtlasLabelPlateMesher.build(
                spec=label_plate_spec,
            )
            label_plate_meshes.append(
                AtlasWallCollectionProductBuilder._translate_mesh(
                    label_plate_mesh,
                    0.0,
                    label_center_y_mm,
                    (
                        float(frame_depth_mm)
                        - float(label_recess_depth_mm)
                    ),
                )
            )

            if label_text_spec is not None:
                line_gap_mm = 1.0
                total_text_height_mm = (
                    label_text_spec.primary_height_mm
                    + line_gap_mm
                    + label_text_spec.secondary_height_mm
                )

                if total_text_height_mm > label_plate_spec.height_mm:
                    raise ValueError(
                        "label text height exceeds label plate height"
                    )

                text_front_z_mm = (
                    float(frame_depth_mm)
                    - float(label_recess_depth_mm)
                    + label_plate_spec.depth_mm
                )

                primary_center_y_mm = (
                    label_center_y_mm
                    + (
                        label_text_spec.secondary_height_mm
                        + line_gap_mm
                    )
                    / 2.0
                )

                primary_mesh = AtlasLabelTextMesher.build_line(
                    text=label_text_spec.primary_text,
                    height_mm=label_text_spec.primary_height_mm,
                    depth_mm=label_text_spec.depth_mm,
                    max_width_mm=label_text_spec.max_width_mm,
                )
                label_text_meshes.append(
                    AtlasWallCollectionProductBuilder._translate_mesh(
                        primary_mesh,
                        0.0,
                        primary_center_y_mm,
                        text_front_z_mm,
                    )
                )

                if label_text_spec.secondary_text:
                    secondary_center_y_mm = (
                        label_center_y_mm
                        - (
                            label_text_spec.primary_height_mm
                            + line_gap_mm
                        )
                        / 2.0
                    )

                    secondary_mesh = AtlasLabelTextMesher.build_line(
                        text=label_text_spec.secondary_text,
                        height_mm=label_text_spec.secondary_height_mm,
                        depth_mm=label_text_spec.depth_mm,
                        max_width_mm=label_text_spec.max_width_mm,
                    )
                    label_text_meshes.append(
                        AtlasWallCollectionProductBuilder._translate_mesh(
                            secondary_mesh,
                            0.0,
                            secondary_center_y_mm,
                            text_front_z_mm,
                        )
                    )

                if label_text_spec.birthday_cake:
                    cake_width_mm = 8.0
                    cake_height_mm = 7.0
                    cake_right_margin_mm = 3.0
                    cake_center_x_mm = (
                        (label_plate_spec.width_mm / 2.0)
                        - cake_right_margin_mm
                        - (cake_width_mm / 2.0)
                    )

                    cake_mesh = AtlasLabelBirthdayCakeMesher.build(
                        width_mm=cake_width_mm,
                        height_mm=cake_height_mm,
                        depth_mm=label_text_spec.depth_mm,
                    )
                    label_birthday_cake_meshes.append(
                        AtlasWallCollectionProductBuilder._translate_mesh(
                            cake_mesh,
                            cake_center_x_mm,
                            label_center_y_mm,
                            text_front_z_mm,
                        )
                    )

                if label_text_spec.home:
                    home_width_mm = 7.0
                    home_height_mm = 6.0
                    home_text_gap_mm = 3.0

                    text_meshes_for_symbol = [
                        primary_mesh,
                    ]

                    if label_text_spec.secondary_text:
                        text_meshes_for_symbol.append(
                            secondary_mesh
                        )

                    text_right_x_mm = max(
                        float(point[0])
                        for text_mesh in text_meshes_for_symbol
                        for triangle in text_mesh["triangles"]
                        for point in triangle
                    )

                    home_center_x_mm = (
                        text_right_x_mm
                        + home_text_gap_mm
                        + (home_width_mm / 2.0)
                    )

                    maximum_home_center_x_mm = (
                        (label_plate_spec.width_mm / 2.0)
                        - 3.0
                        - (home_width_mm / 2.0)
                    )

                    home_center_x_mm = maximum_home_center_x_mm

                    home_mesh = AtlasLabelHomeMesher.build(
                        width_mm=home_width_mm,
                        height_mm=home_height_mm,
                        depth_mm=label_text_spec.depth_mm,
                    )
                    label_home_meshes.append(
                        AtlasWallCollectionProductBuilder._translate_mesh(
                            home_mesh,
                            home_center_x_mm,
                            label_center_y_mm,
                            text_front_z_mm,
                        )
                    )

                if label_text_spec.wedding_rings:
                    rings_width_mm = 8.0
                    rings_height_mm = 6.0
                    rings_right_margin_mm = 3.0

                    rings_center_x_mm = (
                        (label_plate_spec.width_mm / 2.0)
                        - rings_right_margin_mm
                        - (rings_width_mm / 2.0)
                    )

                    rings_mesh = AtlasLabelWeddingRingsMesher.build(
                        width_mm=rings_width_mm,
                        height_mm=rings_height_mm,
                        depth_mm=label_text_spec.depth_mm,
                    )

                    label_wedding_rings_meshes.append(
                        AtlasWallCollectionProductBuilder._translate_mesh(
                            rings_mesh,
                            rings_center_x_mm,
                            label_center_y_mm,
                            text_front_z_mm,
                        )
                    )

                if label_text_spec.graduation_cap:
                    cap_width_mm = 7.0
                    cap_height_mm = 5.0
                    cap_right_margin_mm = 3.0
                    cap_center_x_mm = (
                        (label_plate_spec.width_mm / 2.0)
                        - cap_right_margin_mm
                        - (cap_width_mm / 2.0)
                    )

                    cap_mesh = AtlasLabelGraduationCapMesher.build(
                        width_mm=cap_width_mm,
                        height_mm=cap_height_mm,
                        depth_mm=label_text_spec.depth_mm,
                    )
                    label_graduation_cap_meshes.append(
                        AtlasWallCollectionProductBuilder._translate_mesh(
                            cap_mesh,
                            cap_center_x_mm,
                            label_center_y_mm,
                            text_front_z_mm,
                        )
                    )

        meshes = [
            *frame_meshes,
            *city_meshes,
            *label_plate_meshes,
            *label_text_meshes,
            *label_graduation_cap_meshes,
            *label_birthday_cake_meshes,
            *label_home_meshes,
            *label_wedding_rings_meshes,
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
            "label_text_meshes": label_text_meshes,
            "label_graduation_cap_meshes": (
                label_graduation_cap_meshes
            ),
            "label_birthday_cake_meshes": (
                label_birthday_cake_meshes
            ),
            "label_home_meshes": (
                label_home_meshes
            ),
            "label_wedding_rings_meshes": (
                label_wedding_rings_meshes
            ),
            "meshes": meshes,
        }
