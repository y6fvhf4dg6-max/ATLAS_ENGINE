from __future__ import annotations

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from CORE.atlas_label_text_mesher import AtlasLabelTextMesher


class AtlasLabelBabyStrollerMesher:
    EPSILON = 1e-9

    @classmethod
    def build(
        cls,
        *,
        width_mm: float,
        height_mm: float,
        depth_mm: float,
    ) -> dict:
        width_mm = float(width_mm)
        height_mm = float(height_mm)
        depth_mm = float(depth_mm)

        if width_mm <= 0.0:
            raise ValueError("width_mm must be positive")
        if height_mm <= 0.0:
            raise ValueError("height_mm must be positive")
        if depth_mm <= 0.0:
            raise ValueError("depth_mm must be positive")

        # Main bassinet/body. Broad geometry is intentional:
        # the icon must remain readable at label scale.
        body = Polygon(
            (
                (-2.55, 0.25),
                (1.85, 0.25),
                (1.55, -0.75),
                (1.05, -1.25),
                (0.35, -1.52),
                (-0.65, -1.52),
                (-1.45, -1.25),
                (-2.05, -0.75),
                (-2.40, -0.20),
            )
        )

        # Raised hood/canopy on the rear half.
        canopy = Polygon(
            (
                (-2.30, 0.38),
                (-2.12, 1.18),
                (-1.72, 1.78),
                (-1.10, 2.12),
                (-0.38, 2.20),
                (-0.48, 0.38),
            )
        )

        # Strong diagonal canopy support.
        canopy_support = Polygon(
            (
                (-1.72, 1.72),
                (-1.55, 1.84),
                (-0.55, 0.38),
                (-0.80, 0.38),
            )
        )

        # Handle rises toward the front/right.
        handle = Polygon(
            (
                (1.55, 0.18),
                (2.55, 1.05),
                (2.72, 0.88),
                (1.78, 0.02),
            )
        )

        handle_grip = Point(2.66, 1.00).buffer(
            0.24,
            quad_segs=20,
        )

        # Two large, simple wheels.
        rear_wheel = Point(-1.25, -2.05).buffer(
            0.58,
            quad_segs=24,
        )
        front_wheel = Point(0.85, -2.05).buffer(
            0.58,
            quad_segs=24,
        )

        geometry = unary_union(
            (
                body,
                canopy,
                canopy_support,
                handle,
                handle_grip,
                rear_wheel,
                front_wheel,
            )
        )

        if not geometry.is_valid:
            geometry = geometry.buffer(0)

        if geometry.is_empty:
            raise ValueError(
                "baby stroller produced no printable geometry"
            )

        min_x, min_y, max_x, max_y = geometry.bounds
        source_width = max_x - min_x
        source_height = max_y - min_y

        if (
            source_width <= cls.EPSILON
            or source_height <= cls.EPSILON
        ):
            raise ValueError(
                "baby stroller geometry has invalid bounds"
            )

        uniform_scale = min(
            width_mm / source_width,
            height_mm / source_height,
        )

        from shapely.affinity import scale, translate

        geometry = scale(
            geometry,
            xfact=uniform_scale,
            yfact=uniform_scale,
            origin=(0.0, 0.0),
        )

        min_x, min_y, max_x, max_y = geometry.bounds

        geometry = translate(
            geometry,
            xoff=-((min_x + max_x) / 2.0),
            yoff=-((min_y + max_y) / 2.0),
        )

        triangles = []

        for polygon in AtlasLabelTextMesher._iter_polygons(
            geometry
        ):
            triangles.extend(
                AtlasLabelTextMesher._extrude_polygon(
                    polygon=polygon,
                    depth_mm=depth_mm,
                )
            )

        return {
            "type": "label_baby_stroller",
            "width_mm": width_mm,
            "height_mm": height_mm,
            "depth_mm": depth_mm,
            "triangles": triangles,
        }
