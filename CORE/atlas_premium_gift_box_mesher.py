from __future__ import annotations

from CORE.atlas_premium_gift_box_spec import AtlasPremiumGiftBoxSpec


class AtlasPremiumGiftBoxMesher:
    @staticmethod
    def build_base(
        *,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> dict:
        outer_x = spec.outer_width_mm / 2.0
        outer_y = spec.outer_height_mm / 2.0
        inner_x = spec.inner_width_mm / 2.0
        inner_y = spec.inner_height_mm / 2.0

        z_bottom = 0.0
        z_floor = spec.floor_thickness_mm
        z_top = spec.base_total_depth_mm

        outer_bottom = AtlasPremiumGiftBoxMesher._ring(
            half_x=outer_x,
            half_y=outer_y,
            z_mm=z_bottom,
        )
        outer_top = AtlasPremiumGiftBoxMesher._ring(
            half_x=outer_x,
            half_y=outer_y,
            z_mm=z_top,
        )
        inner_floor = AtlasPremiumGiftBoxMesher._ring(
            half_x=inner_x,
            half_y=inner_y,
            z_mm=z_floor,
        )
        inner_top = AtlasPremiumGiftBoxMesher._ring(
            half_x=inner_x,
            half_y=inner_y,
            z_mm=z_top,
        )

        triangles = []

        triangles.extend(
            AtlasPremiumGiftBoxMesher._rectangle_face(
                outer_bottom,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._wall_faces(
                outer_bottom,
                outer_top,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._rectangle_face(
                inner_floor,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._wall_faces(
                inner_floor,
                inner_top,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._ring_face(
                outer_ring=outer_top,
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
            "triangles": triangles,
        }

    @staticmethod
    def build_lid(
        *,
        spec: AtlasPremiumGiftBoxSpec,
    ) -> dict:
        outer_x = spec.lid_outer_width_mm / 2.0
        outer_y = spec.lid_outer_height_mm / 2.0
        inner_x = spec.lid_inner_width_mm / 2.0
        inner_y = spec.lid_inner_height_mm / 2.0

        z_bottom = 0.0
        z_ceiling = spec.lid_overlap_mm
        z_top = spec.lid_total_depth_mm

        outer_bottom = AtlasPremiumGiftBoxMesher._ring(
            half_x=outer_x,
            half_y=outer_y,
            z_mm=z_bottom,
        )
        outer_top = AtlasPremiumGiftBoxMesher._ring(
            half_x=outer_x,
            half_y=outer_y,
            z_mm=z_top,
        )
        inner_bottom = AtlasPremiumGiftBoxMesher._ring(
            half_x=inner_x,
            half_y=inner_y,
            z_mm=z_bottom,
        )
        inner_ceiling = AtlasPremiumGiftBoxMesher._ring(
            half_x=inner_x,
            half_y=inner_y,
            z_mm=z_ceiling,
        )

        triangles = []

        triangles.extend(
            AtlasPremiumGiftBoxMesher._rectangle_face(
                outer_top,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._wall_faces(
                outer_bottom,
                outer_top,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._rectangle_face(
                inner_ceiling,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._wall_faces(
                inner_bottom,
                inner_ceiling,
            )
        )
        triangles.extend(
            AtlasPremiumGiftBoxMesher._ring_face(
                outer_ring=outer_bottom,
                inner_ring=inner_bottom,
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
            "triangles": triangles,
        }

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
