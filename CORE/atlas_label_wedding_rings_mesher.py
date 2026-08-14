from __future__ import annotations

from shapely.affinity import scale, translate
from shapely.geometry import Point
from shapely.ops import unary_union

from CORE.atlas_label_text_mesher import AtlasLabelTextMesher


class AtlasLabelWeddingRingsMesher:
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

        outer_radius = 2.4
        inner_radius = 1.45
        center_offset = 1.6

        left_ring = (
            Point(-center_offset, 0.0)
            .buffer(outer_radius, quad_segs=24)
            .difference(
                Point(-center_offset, 0.0).buffer(
                    inner_radius,
                    quad_segs=24,
                )
            )
        )

        right_ring = (
            Point(center_offset, 0.0)
            .buffer(outer_radius, quad_segs=24)
            .difference(
                Point(center_offset, 0.0).buffer(
                    inner_radius,
                    quad_segs=24,
                )
            )
        )

        geometry = unary_union(
            (
                left_ring,
                right_ring,
            )
        )

        if not geometry.is_valid:
            geometry = geometry.buffer(0)

        if geometry.is_empty:
            raise ValueError(
                "wedding rings produced no printable geometry"
            )

        min_x, min_y, max_x, max_y = geometry.bounds

        source_width = max_x - min_x
        source_height = max_y - min_y

        if (
            source_width <= cls.EPSILON
            or source_height <= cls.EPSILON
        ):
            raise ValueError(
                "wedding rings geometry has invalid bounds"
            )

        uniform_scale = min(
            width_mm / source_width,
            height_mm / source_height,
        )

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
            "type": "label_wedding_rings",
            "width_mm": width_mm,
            "height_mm": height_mm,
            "depth_mm": depth_mm,
            "triangles": triangles,
        }
