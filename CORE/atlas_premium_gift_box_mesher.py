from __future__ import annotations

from CORE.atlas_castle_shell_triangulator import (
    AtlasCastleShellTriangulator,
)
from CORE.atlas_label_plate_mesher import AtlasLabelPlateMesher
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_mesher import AtlasLabelTextMesher
from CORE.atlas_premium_gift_box_spec import AtlasPremiumGiftBoxSpec


class AtlasPremiumGiftBoxMesher:
    CONNECTOR_INSET_PER_SIDE_MM = 1.0

    @classmethod
    def build_base(
        cls,
        *,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> dict:
        outer_x = spec.outer_width_mm / 2.0
        outer_y = spec.outer_height_mm / 2.0
        inner_x = spec.inner_width_mm / 2.0
        inner_y = spec.inner_height_mm / 2.0

        male_outer_x = (
            cls._male_connector_outer_width_mm(spec) / 2.0
        )
        male_outer_y = (
            cls._male_connector_outer_height_mm(spec) / 2.0
        )

        z_bottom = 0.0
        z_floor = spec.floor_thickness_mm
        z_top = spec.base_total_depth_mm
        z_body_top = z_top - spec.connector_engagement_mm

        outer_sections = (
            cls._ring(
                half_x=outer_x,
                half_y=outer_y,
                z_mm=z_bottom,
            ),
            cls._ring(
                half_x=outer_x,
                half_y=outer_y,
                z_mm=z_body_top,
            ),
            cls._ring(
                half_x=male_outer_x,
                half_y=male_outer_y,
                z_mm=z_body_top,
            ),
            cls._ring(
                half_x=male_outer_x,
                half_y=male_outer_y,
                z_mm=z_top,
            ),
        )
        inner_floor = cls._ring(
            half_x=inner_x,
            half_y=inner_y,
            z_mm=z_floor,
        )
        inner_top = cls._ring(
            half_x=inner_x,
            half_y=inner_y,
            z_mm=z_top,
        )

        triangles = []
        triangles.extend(
            cls._rectangle_face(outer_sections[0])
        )

        for lower, upper in zip(
            outer_sections,
            outer_sections[1:],
        ):
            triangles.extend(
                cls._wall_faces(lower, upper)
            )

        triangles.extend(
            cls._rectangle_face(inner_floor)
        )
        triangles.extend(
            cls._wall_faces(inner_floor, inner_top)
        )
        triangles.extend(
            cls._ring_face(
                outer_ring=outer_sections[-1],
                inner_ring=inner_top,
            )
        )

        return {
            "type": "premium_gift_box_base",
            "outer_width_mm": spec.outer_width_mm,
            "outer_height_mm": spec.outer_height_mm,
            "inner_width_mm": spec.inner_width_mm,
            "inner_height_mm": spec.inner_height_mm,
            "total_depth_mm": spec.base_total_depth_mm,
            "wall_thickness_mm": spec.wall_thickness_mm,
            "floor_thickness_mm": spec.floor_thickness_mm,
            "top_connector": "male",
            "connector_engagement_mm": (
                spec.connector_engagement_mm
            ),
            "male_connector_outer_width_mm": (
                cls._male_connector_outer_width_mm(spec)
            ),
            "male_connector_outer_height_mm": (
                cls._male_connector_outer_height_mm(spec)
            ),
            "triangles": triangles,
        }

    @classmethod
    def build_middle_module(
        cls,
        *,
        spec: AtlasPremiumGiftBoxSpec,
        product_capacity_mm: float,
    ) -> dict:
        product_capacity_mm = (
            spec.validate_middle_module_capacity(
                product_capacity_mm
            )
        )
        usable_height_mm = (
            spec.middle_module_usable_height_mm(
                product_capacity_mm
            )
        )

        outer_x = spec.outer_width_mm / 2.0
        outer_y = spec.outer_height_mm / 2.0
        inner_x = spec.inner_width_mm / 2.0
        inner_y = spec.inner_height_mm / 2.0

        male_width = cls._male_connector_outer_width_mm(spec)
        male_height = cls._male_connector_outer_height_mm(spec)
        female_width = (
            male_width
            + 2.0 * spec.connector_clearance_per_side_mm
        )
        female_height = (
            male_height
            + 2.0 * spec.connector_clearance_per_side_mm
        )

        male_outer_x = male_width / 2.0
        male_outer_y = male_height / 2.0
        female_inner_x = female_width / 2.0
        female_inner_y = female_height / 2.0

        z_bottom = 0.0
        z_recess_top = spec.connector_recess_depth_mm
        z_body_top = usable_height_mm
        z_total = (
            z_body_top
            + spec.connector_engagement_mm
        )

        sections = (
            (
                z_bottom,
                outer_x,
                outer_y,
                female_inner_x,
                female_inner_y,
            ),
            (
                z_recess_top,
                outer_x,
                outer_y,
                female_inner_x,
                female_inner_y,
            ),
            (
                z_recess_top,
                outer_x,
                outer_y,
                inner_x,
                inner_y,
            ),
            (
                z_body_top,
                outer_x,
                outer_y,
                inner_x,
                inner_y,
            ),
            (
                z_body_top,
                male_outer_x,
                male_outer_y,
                inner_x,
                inner_y,
            ),
            (
                z_total,
                male_outer_x,
                male_outer_y,
                inner_x,
                inner_y,
            ),
        )

        triangles = cls._loft_rectangular_tube(
            sections=sections,
        )

        return {
            "type": "premium_gift_box_middle_module",
            "product_capacity_mm": product_capacity_mm,
            "usable_height_mm": usable_height_mm,
            "total_height_mm": z_total,
            "outer_width_mm": spec.outer_width_mm,
            "outer_height_mm": spec.outer_height_mm,
            "inner_width_mm": spec.inner_width_mm,
            "inner_height_mm": spec.inner_height_mm,
            "bottom_connector": "female",
            "top_connector": "male",
            "connector_engagement_mm": (
                spec.connector_engagement_mm
            ),
            "connector_recess_depth_mm": (
                spec.connector_recess_depth_mm
            ),
            "male_connector_outer_width_mm": male_width,
            "male_connector_outer_height_mm": male_height,
            "female_connector_inner_width_mm": female_width,
            "female_connector_inner_height_mm": female_height,
            "triangles": triangles,
        }

    @classmethod
    def build_lid(
        cls,
        *,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> dict:
        outer_x = spec.lid_outer_width_mm / 2.0
        outer_y = spec.lid_outer_height_mm / 2.0
        wide_inner_x = spec.lid_inner_width_mm / 2.0
        wide_inner_y = spec.lid_inner_height_mm / 2.0

        male_width = cls._male_connector_outer_width_mm(spec)
        male_height = cls._male_connector_outer_height_mm(spec)
        female_width = (
            male_width
            + 2.0 * spec.connector_clearance_per_side_mm
        )
        female_height = (
            male_height
            + 2.0 * spec.connector_clearance_per_side_mm
        )
        female_inner_x = female_width / 2.0
        female_inner_y = female_height / 2.0

        z_bottom = 0.0
        z_ceiling = spec.lid_overlap_mm
        z_recess_bottom = (
            z_ceiling
            - spec.connector_recess_depth_mm
        )
        z_top = spec.lid_total_depth_mm

        outer_bottom = cls._ring(
            half_x=outer_x,
            half_y=outer_y,
            z_mm=z_bottom,
        )
        outer_top = cls._ring(
            half_x=outer_x,
            half_y=outer_y,
            z_mm=z_top,
        )

        inner_sections = (
            cls._ring(
                half_x=wide_inner_x,
                half_y=wide_inner_y,
                z_mm=z_bottom,
            ),
            cls._ring(
                half_x=wide_inner_x,
                half_y=wide_inner_y,
                z_mm=z_recess_bottom,
            ),
            cls._ring(
                half_x=female_inner_x,
                half_y=female_inner_y,
                z_mm=z_recess_bottom,
            ),
            cls._ring(
                half_x=female_inner_x,
                half_y=female_inner_y,
                z_mm=z_ceiling,
            ),
        )

        recess_width_mm, recess_height_mm = (
            spec.personalization_recess_size_mm
        )
        recess_outline = AtlasLabelPlateMesher._rounded_outline(
            width_mm=recess_width_mm,
            height_mm=recess_height_mm,
            corner_radius_mm=2.0,
        )
        recess_floor_z = (
            z_top
            - spec.personalization_recess_depth_mm
        )
        outer_top_outline = tuple(
            (float(x), float(y))
            for x, y, _ in outer_top
        )
        top_surface_triangles = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=outer_top_outline,
                inner_rings=[recess_outline],
            )
        )
        recess_floor_triangles = (
            AtlasCastleShellTriangulator.triangulate(
                outer_ring=recess_outline,
            )
        )

        if not top_surface_triangles or not recess_floor_triangles:
            raise ValueError(
                "personalization recess triangulation failed"
            )

        triangles = []
        triangles.extend(
            cls._lift_triangles_2d(
                top_surface_triangles,
                z_mm=z_top,
            )
        )
        triangles.extend(
            cls._lift_triangles_2d(
                recess_floor_triangles,
                z_mm=recess_floor_z,
                reverse=True,
            )
        )
        triangles.extend(
            cls._outline_wall_faces(
                outline=recess_outline,
                bottom_z_mm=recess_floor_z,
                top_z_mm=z_top,
            )
        )
        triangles.extend(
            cls._wall_faces(outer_bottom, outer_top)
        )

        for lower, upper in zip(
            inner_sections,
            inner_sections[1:],
        ):
            triangles.extend(
                cls._wall_faces(lower, upper)
            )

        triangles.extend(
            cls._rectangle_face(inner_sections[-1])
        )
        triangles.extend(
            cls._ring_face(
                outer_ring=outer_bottom,
                inner_ring=inner_sections[0],
            )
        )

        return {
            "type": "premium_gift_box_lid",
            "outer_width_mm": spec.lid_outer_width_mm,
            "outer_height_mm": spec.lid_outer_height_mm,
            "inner_width_mm": spec.lid_inner_width_mm,
            "inner_height_mm": spec.lid_inner_height_mm,
            "total_depth_mm": spec.lid_total_depth_mm,
            "wall_thickness_mm": spec.lid_wall_thickness_mm,
            "top_thickness_mm": spec.lid_top_thickness_mm,
            "overlap_mm": spec.lid_overlap_mm,
            "bottom_connector": "female",
            "connector_recess_depth_mm": (
                spec.connector_recess_depth_mm
            ),
            "female_connector_inner_width_mm": female_width,
            "female_connector_inner_height_mm": female_height,
            "personalization_recess_depth_mm": (
                spec.personalization_recess_depth_mm
            ),
            "personalization_recess_size_mm": (
                spec.personalization_recess_size_mm
            ),
            "triangles": triangles,
        }

    @classmethod
    def build_personalization_plate(
        cls,
        *,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> dict:
        width_mm, height_mm = (
            spec.personalization_plate_size_mm
        )
        plate = AtlasLabelPlateMesher.build(
            spec=AtlasLabelPlateSpec(
                width_mm=width_mm,
                height_mm=height_mm,
                depth_mm=(
                    spec.personalization_plate_thickness_mm
                ),
                corner_radius_mm=2.0,
            )
        )

        plate["type"] = (
            "premium_gift_box_personalization_plate"
        )
        plate["fit_system"] = "removable_recess_insert"
        plate["fit_clearance_per_side_mm"] = (
            spec.personalization_fit_clearance_per_side_mm
        )

        return plate

    @classmethod
    def build_personalization_text(
        cls,
        *,
        spec: AtlasPremiumGiftBoxSpec,
        lines,
    ) -> list:
        lines = spec.validate_personalization_lines(lines)
        plate_width_mm, plate_height_mm = (
            spec.personalization_plate_size_mm
        )
        max_width_mm = plate_width_mm - 8.0

        if len(lines) == 1:
            layout = (
                (
                    lines[0],
                    min(7.0, plate_height_mm * 0.30),
                    0.0,
                ),
            )
        else:
            layout = (
                (
                    lines[0],
                    min(6.0, plate_height_mm * 0.24),
                    plate_height_mm * 0.16,
                ),
                (
                    lines[1],
                    min(4.5, plate_height_mm * 0.18),
                    -plate_height_mm * 0.16,
                ),
            )

        meshes = []

        for line_index, (
            line,
            height_mm,
            offset_y_mm,
        ) in enumerate(layout):
            mesh = AtlasLabelTextMesher.build_line(
                text=line,
                height_mm=height_mm,
                depth_mm=spec.personalization_text_depth_mm,
                max_width_mm=max_width_mm,
            )
            mesh["type"] = (
                "premium_gift_box_personalization_text"
            )
            mesh["line_index"] = line_index
            mesh["triangles"] = cls._translate_triangles(
                mesh["triangles"],
                offset_y_mm=offset_y_mm,
                offset_z_mm=(
                    spec.personalization_plate_thickness_mm
                ),
            )
            meshes.append(mesh)

        return meshes

    @staticmethod
    def _translate_triangles(
        triangles: list,
        *,
        offset_x_mm: float = 0.0,
        offset_y_mm: float = 0.0,
        offset_z_mm: float = 0.0,
    ) -> list:
        return [
            tuple(
                (
                    float(x) + offset_x_mm,
                    float(y) + offset_y_mm,
                    float(z) + offset_z_mm,
                )
                for x, y, z in triangle
            )
            for triangle in triangles
        ]

    @staticmethod
    def _lift_triangles_2d(
        triangles_2d,
        *,
        z_mm: float,
        reverse: bool = False,
    ) -> list:
        result = []

        for triangle in triangles_2d:
            lifted = tuple(
                (float(x), float(y), float(z_mm))
                for x, y in triangle
            )

            if reverse:
                lifted = (
                    lifted[0],
                    lifted[2],
                    lifted[1],
                )

            result.append(lifted)

        return result

    @staticmethod
    def _outline_wall_faces(
        *,
        outline,
        bottom_z_mm: float,
        top_z_mm: float,
    ) -> list:
        triangles = []

        for index in range(len(outline)):
            next_index = (index + 1) % len(outline)
            x1, y1 = outline[index]
            x2, y2 = outline[next_index]

            bottom_1 = (float(x1), float(y1), bottom_z_mm)
            bottom_2 = (float(x2), float(y2), bottom_z_mm)
            top_1 = (float(x1), float(y1), top_z_mm)
            top_2 = (float(x2), float(y2), top_z_mm)

            triangles.extend(
                (
                    (bottom_1, bottom_2, top_2),
                    (bottom_1, top_2, top_1),
                )
            )

        return triangles

    @classmethod
    def _male_connector_outer_width_mm(
        cls,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> float:
        return (
            spec.outer_width_mm
            - 2.0 * cls.CONNECTOR_INSET_PER_SIDE_MM
        )

    @classmethod
    def _male_connector_outer_height_mm(
        cls,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> float:
        return (
            spec.outer_height_mm
            - 2.0 * cls.CONNECTOR_INSET_PER_SIDE_MM
        )

    @classmethod
    def _loft_rectangular_tube(
        cls,
        *,
        sections: tuple,
    ) -> list:
        rings = []

        for (
            z_mm,
            outer_x,
            outer_y,
            inner_x,
            inner_y,
        ) in sections:
            rings.append(
                (
                    cls._ring(
                        half_x=outer_x,
                        half_y=outer_y,
                        z_mm=z_mm,
                    ),
                    cls._ring(
                        half_x=inner_x,
                        half_y=inner_y,
                        z_mm=z_mm,
                    ),
                )
            )

        triangles = []
        triangles.extend(
            cls._ring_face(
                outer_ring=rings[0][0],
                inner_ring=rings[0][1],
            )
        )

        for lower, upper in zip(rings, rings[1:]):
            if lower[0] != upper[0]:
                triangles.extend(
                    cls._wall_faces(
                        lower[0],
                        upper[0],
                    )
                )

            if lower[1] != upper[1]:
                triangles.extend(
                    cls._wall_faces(
                        lower[1],
                        upper[1],
                    )
                )

        triangles.extend(
            cls._ring_face(
                outer_ring=rings[-1][0],
                inner_ring=rings[-1][1],
            )
        )

        return triangles

    @staticmethod
    def _ring(
        *,
        half_x: float,
        half_y: float,
        z_mm: float,
    ) -> tuple:
        return (
            (-half_x, -half_y, z_mm),
            (half_x, -half_y, z_mm),
            (half_x, half_y, z_mm),
            (-half_x, half_y, z_mm),
        )

    @staticmethod
    def _rectangle_face(ring: tuple) -> list:
        return [
            (ring[0], ring[1], ring[2]),
            (ring[0], ring[2], ring[3]),
        ]

    @staticmethod
    def _wall_faces(
        lower_ring: tuple,
        upper_ring: tuple,
    ) -> list:
        triangles = []

        for index in range(4):
            next_index = (index + 1) % 4

            triangles.extend(
                (
                    (
                        lower_ring[index],
                        lower_ring[next_index],
                        upper_ring[next_index],
                    ),
                    (
                        lower_ring[index],
                        upper_ring[next_index],
                        upper_ring[index],
                    ),
                )
            )

        return triangles

    @staticmethod
    def _ring_face(
        *,
        outer_ring: tuple,
        inner_ring: tuple,
    ) -> list:
        triangles = []

        for index in range(4):
            next_index = (index + 1) % 4

            triangles.extend(
                (
                    (
                        outer_ring[index],
                        outer_ring[next_index],
                        inner_ring[next_index],
                    ),
                    (
                        outer_ring[index],
                        inner_ring[next_index],
                        inner_ring[index],
                    ),
                )
            )

        return triangles
