from __future__ import annotations

from shapely.affinity import scale, translate
from shapely.geometry import Polygon
from shapely.ops import unary_union

from CORE.atlas_label_text_mesher import AtlasLabelTextMesher


class AtlasLabelGraduationCapMesher:
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

        mortarboard = Polygon(
            (
                (-3.5, 1.0),
                (0.0, 2.5),
                (3.5, 1.0),
                (0.0, -0.5),
            )
        )

        crown = Polygon(
            (
                (-2.15, 0.15),
                (2.15, 0.15),
                (1.75, -1.45),
                (0.0, -2.0),
                (-1.75, -1.45),
            )
        )

        tassel = Polygon(
            (
                (2.25, 0.95),
                (2.55, 0.95),
                (2.55, -1.55),
                (2.95, -2.5),
                (2.15, -2.5),
                (2.35, -1.55),
            )
        )

        geometry = unary_union(
            (
                mortarboard,
                crown,
                tassel,
            )
        )

        if not geometry.is_valid:
            geometry = geometry.buffer(0)

        if geometry.is_empty:
            raise ValueError(
                "graduation cap produced no printable geometry"
            )

        min_x, min_y, max_x, max_y = geometry.bounds
        source_width = max_x - min_x
        source_height = max_y - min_y

        if (
            source_width <= cls.EPSILON
            or source_height <= cls.EPSILON
        ):
            raise ValueError(
                "graduation cap geometry has invalid bounds"
            )

        geometry = scale(
            geometry,
            xfact=width_mm / source_width,
            yfact=height_mm / source_height,
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
            "type": "label_graduation_cap",
            "width_mm": width_mm,
            "height_mm": height_mm,
            "depth_mm": depth_mm,
            "triangles": triangles,
        }
