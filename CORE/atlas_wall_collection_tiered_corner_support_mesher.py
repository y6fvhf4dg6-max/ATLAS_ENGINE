from __future__ import annotations

import math

from CORE.atlas_wall_collection_tiered_corner_support_spec import (
    AtlasWallCollectionTieredCornerSupportSpec,
)


class AtlasWallCollectionTieredCornerSupportMesher:
    CORNERS = (
        "lower_left",
        "lower_right",
        "upper_right",
        "upper_left",
    )

    @classmethod
    def build_set(
        cls,
        *,
        spec: AtlasWallCollectionTieredCornerSupportSpec,
        product_width_mm: float,
        product_height_mm: float,
    ) -> dict:
        product_width_mm = float(product_width_mm)
        product_height_mm = float(product_height_mm)

        for name, value in (
            ("product_width_mm", product_width_mm),
            ("product_height_mm", product_height_mm),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive")

        half_width = product_width_mm / 2.0
        half_height = product_height_mm / 2.0
        placements = {
            "lower_left": (-half_width, -half_height, 1.0, 1.0),
            "lower_right": (half_width, -half_height, -1.0, 1.0),
            "upper_right": (half_width, half_height, -1.0, -1.0),
            "upper_left": (-half_width, half_height, 1.0, -1.0),
        }

        local_triangles = cls._build_local_triangles(spec=spec)
        meshes = {}

        for corner in cls.CORNERS:
            anchor_x, anchor_y, direction_x, direction_y = placements[corner]
            triangles = cls._transform_triangles(
                local_triangles,
                anchor_x=anchor_x,
                anchor_y=anchor_y,
                direction_x=direction_x,
                direction_y=direction_y,
            )
            meshes[corner] = {
                "type": "wall_collection_tiered_corner_support",
                "corner": corner,
                "product_corner_anchor_mm": (anchor_x, anchor_y),
                "frame_contact_width_mm": spec.corner_engagement_mm,
                "next_plate_base_z_mm": spec.next_plate_base_z_mm,
                "total_height_mm": spec.total_height_mm,
                "triangles": triangles,
            }

        return meshes

    @classmethod
    def build_universal_support(
        cls,
        *,
        spec: AtlasWallCollectionTieredCornerSupportSpec,
    ) -> dict:
        if spec.product_capacity_mm is None:
            raise ValueError(
                "universal support requires product_capacity_mm"
            )

        triangles = (
            cls._build_universal_local_triangles(
                spec=spec,
            )
        )

        return {
            "type": (
                "wall_collection_universal_"
                "tiered_corner_support"
            ),
            "product_capacity_mm": (
                spec.product_capacity_mm
            ),
            "frame_contact_width_mm": (
                spec.corner_engagement_mm
            ),
            "next_plate_base_z_mm": (
                spec.next_plate_base_z_mm
            ),
            "total_height_mm": spec.total_height_mm,
            "required_quantity_per_level": 4,
            "triangles": triangles,
        }

    @classmethod
    def _build_universal_local_triangles(
        cls,
        *,
        spec: AtlasWallCollectionTieredCornerSupportSpec,
    ) -> list:
        return cls._build_local_triangles(spec=spec)

    @classmethod
    def _build_local_triangles(
        cls,
        *,
        spec: AtlasWallCollectionTieredCornerSupportSpec,
    ) -> list:
        clearance = spec.xy_fit_clearance_mm
        wall = spec.wall_thickness_mm
        engagement = spec.corner_engagement_mm
        total_height = spec.total_height_mm
        shelf_top = spec.next_plate_base_z_mm
        shelf_bottom = shelf_top - spec.shelf_thickness_mm

        boxes = (
            (
                -clearance - wall,
                -clearance,
                -clearance - wall,
                engagement,
                0.0,
                total_height,
            ),
            (
                -clearance - wall,
                engagement,
                -clearance - wall,
                -clearance,
                0.0,
                total_height,
            ),
            (
                -clearance,
                engagement,
                -clearance,
                engagement,
                shelf_bottom,
                shelf_top,
            ),
        )

        return cls._union_box_surface(boxes)

    @staticmethod
    def _union_box_surface(boxes: tuple) -> list:
        x_values = sorted({value for box in boxes for value in box[:2]})
        y_values = sorted({value for box in boxes for value in box[2:4]})
        z_values = sorted({value for box in boxes for value in box[4:6]})

        occupied = set()

        for x_index in range(len(x_values) - 1):
            center_x = (x_values[x_index] + x_values[x_index + 1]) / 2.0
            for y_index in range(len(y_values) - 1):
                center_y = (y_values[y_index] + y_values[y_index + 1]) / 2.0
                for z_index in range(len(z_values) - 1):
                    center_z = (z_values[z_index] + z_values[z_index + 1]) / 2.0
                    if any(
                        x0 < center_x < x1
                        and y0 < center_y < y1
                        and z0 < center_z < z1
                        for x0, x1, y0, y1, z0, z1 in boxes
                    ):
                        occupied.add((x_index, y_index, z_index))

        triangles = []
        directions = (
            (-1, 0, 0),
            (1, 0, 0),
            (0, -1, 0),
            (0, 1, 0),
            (0, 0, -1),
            (0, 0, 1),
        )

        for cell in sorted(occupied):
            x_index, y_index, z_index = cell
            bounds = (
                x_values[x_index],
                x_values[x_index + 1],
                y_values[y_index],
                y_values[y_index + 1],
                z_values[z_index],
                z_values[z_index + 1],
            )
            for direction in directions:
                neighbor = tuple(
                    cell[index] + direction[index]
                    for index in range(3)
                )
                if neighbor in occupied:
                    continue
                first, second, third, fourth = (
                    AtlasWallCollectionTieredCornerSupportMesher._face_points(
                        bounds,
                        direction,
                    )
                )
                triangles.extend(
                    (
                        (first, second, third),
                        (first, third, fourth),
                    )
                )

        return triangles

    @staticmethod
    def _face_points(bounds: tuple, direction: tuple) -> tuple:
        x0, x1, y0, y1, z0, z1 = bounds
        faces = {
            (-1, 0, 0): (
                (x0, y0, z0), (x0, y0, z1),
                (x0, y1, z1), (x0, y1, z0),
            ),
            (1, 0, 0): (
                (x1, y0, z0), (x1, y1, z0),
                (x1, y1, z1), (x1, y0, z1),
            ),
            (0, -1, 0): (
                (x0, y0, z0), (x1, y0, z0),
                (x1, y0, z1), (x0, y0, z1),
            ),
            (0, 1, 0): (
                (x0, y1, z0), (x0, y1, z1),
                (x1, y1, z1), (x1, y1, z0),
            ),
            (0, 0, -1): (
                (x0, y0, z0), (x0, y1, z0),
                (x1, y1, z0), (x1, y0, z0),
            ),
            (0, 0, 1): (
                (x0, y0, z1), (x1, y0, z1),
                (x1, y1, z1), (x0, y1, z1),
            ),
        }
        return faces[direction]

    @staticmethod
    def _transform_triangles(
        triangles: list,
        *,
        anchor_x: float,
        anchor_y: float,
        direction_x: float,
        direction_y: float,
    ) -> list:
        transformed = []
        reverse = direction_x * direction_y < 0.0

        for triangle in triangles:
            points = tuple(
                (
                    anchor_x + direction_x * float(x),
                    anchor_y + direction_y * float(y),
                    float(z),
                )
                for x, y, z in triangle
            )
            if reverse:
                points = (points[0], points[2], points[1])
            transformed.append(points)

        return transformed
