from __future__ import annotations

from shapely.affinity import scale, translate
from shapely.geometry import Polygon
from shapely.ops import unary_union

from CORE.atlas_label_text_mesher import AtlasLabelTextMesher


class AtlasLabelHomeMesher:
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

        body = Polygon(
            (
                (-2.8, -2.4),
                (2.8, -2.4),
                (2.8, 0.7),
                (-2.8, 0.7),
            )
        )

        roof = Polygon(
            (
                (-3.5, 0.5),
                (0.0, 3.0),
                (3.5, 0.5),
            )
        )

        chimney = Polygon(
            (
                (1.65, 1.15),
                (2.25, 1.15),
                (2.25, 2.45),
                (1.65, 2.45),
            )
        )

        door = Polygon(
            (
                (-0.55, -2.4),
                (0.55, -2.4),
                (0.55, -0.55),
                (-0.55, -0.55),
            )
        )

        geometry = unary_union(
            (
                body,
                roof,
                chimney,
            )
        ).difference(door)

        if not geometry.is_valid:
            geometry = geometry.buffer(0)

        if geometry.is_empty:
            raise ValueError(
                "home symbol produced no printable geometry"
            )

        min_x, min_y, max_x, max_y = geometry.bounds
        source_width = max_x - min_x
        source_height = max_y - min_y

        if (
            source_width <= cls.EPSILON
            or source_height <= cls.EPSILON
        ):
            raise ValueError(
                "home symbol geometry has invalid bounds"
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
            "type": "label_home",
            "width_mm": width_mm,
            "height_mm": height_mm,
            "depth_mm": depth_mm,
            "triangles": triangles,
        }
