from __future__ import annotations

import mapbox_earcut
import numpy as np
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from shapely.affinity import scale, translate
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.geometry.polygon import orient


class AtlasLabelTextMesher:
    FONT_FAMILY = "DejaVu Sans"
    FONT_WEIGHT = "bold"
    EPSILON = 1e-9

    @classmethod
    def build_line(
        cls,
        *,
        text: str,
        height_mm: float,
        depth_mm: float,
        max_width_mm: float,
    ) -> dict:
        clean_text = str(text).strip()
        height_mm = float(height_mm)
        depth_mm = float(depth_mm)
        max_width_mm = float(max_width_mm)

        if not clean_text:
            raise ValueError("text must not be empty")
        if height_mm <= 0.0:
            raise ValueError("height_mm must be positive")
        if depth_mm <= 0.0:
            raise ValueError("depth_mm must be positive")
        if max_width_mm <= 0.0:
            raise ValueError("max_width_mm must be positive")

        font = FontProperties(
            family=cls.FONT_FAMILY,
            weight=cls.FONT_WEIGHT,
        )
        text_path = TextPath(
            (0.0, 0.0),
            clean_text,
            size=10.0,
            prop=font,
            usetex=False,
        )

        geometry = cls._path_geometry(text_path)

        if geometry.is_empty:
            raise ValueError("text produced no printable geometry")

        min_x, min_y, max_x, max_y = geometry.bounds
        source_width = max_x - min_x
        source_height = max_y - min_y

        if source_width <= cls.EPSILON or source_height <= cls.EPSILON:
            raise ValueError("text geometry has invalid bounds")

        uniform_scale = min(
            height_mm / source_height,
            max_width_mm / source_width,
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

        for polygon in cls._iter_polygons(geometry):
            triangles.extend(
                cls._extrude_polygon(
                    polygon=polygon,
                    depth_mm=depth_mm,
                )
            )

        return {
            "type": "label_text",
            "text": clean_text,
            "font_family": cls.FONT_FAMILY,
            "font_weight": cls.FONT_WEIGHT,
            "height_mm": height_mm,
            "depth_mm": depth_mm,
            "max_width_mm": max_width_mm,
            "triangles": triangles,
        }

    @classmethod
    def _path_geometry(cls, text_path: TextPath):
        geometry = GeometryCollection()

        for coordinates in text_path.to_polygons():
            if len(coordinates) < 3:
                continue

            polygon = Polygon(coordinates)

            if polygon.is_empty or polygon.area <= cls.EPSILON:
                continue

            if not polygon.is_valid:
                polygon = polygon.buffer(0)

            if polygon.is_empty:
                continue

            geometry = geometry.symmetric_difference(polygon)

        if not geometry.is_valid:
            geometry = geometry.buffer(0)

        return geometry

    @staticmethod
    def _iter_polygons(geometry):
        if isinstance(geometry, Polygon):
            yield geometry
            return

        if isinstance(geometry, MultiPolygon):
            yield from geometry.geoms
            return

        if hasattr(geometry, "geoms"):
            for item in geometry.geoms:
                yield from AtlasLabelTextMesher._iter_polygons(item)

    @classmethod
    def _extrude_polygon(
        cls,
        *,
        polygon: Polygon,
        depth_mm: float,
    ) -> list:
        polygon = orient(polygon, sign=1.0)

        rings = [
            cls._clean_ring(polygon.exterior.coords),
            *(
                cls._clean_ring(interior.coords)
                for interior in polygon.interiors
            ),
        ]
        rings = [ring for ring in rings if len(ring) >= 3]

        if not rings:
            return []

        vertices_2d = []
        ring_end_indices = []
        running_total = 0

        for ring in rings:
            vertices_2d.extend(ring)
            running_total += len(ring)
            ring_end_indices.append(running_total)

        indices = mapbox_earcut.triangulate_float64(
            np.asarray(vertices_2d, dtype=np.float64),
            np.asarray(ring_end_indices, dtype=np.uint32),
        )

        triangles = []

        for index in range(0, len(indices), 3):
            a = vertices_2d[int(indices[index])]
            b = vertices_2d[int(indices[index + 1])]
            c = vertices_2d[int(indices[index + 2])]

            bottom_a = (a[0], a[1], 0.0)
            bottom_b = (b[0], b[1], 0.0)
            bottom_c = (c[0], c[1], 0.0)

            top_a = (a[0], a[1], depth_mm)
            top_b = (b[0], b[1], depth_mm)
            top_c = (c[0], c[1], depth_mm)

            triangles.append((bottom_a, bottom_c, bottom_b))
            triangles.append((top_a, top_b, top_c))

        for ring in rings:
            for index, current in enumerate(ring):
                following = ring[(index + 1) % len(ring)]

                bottom_current = (current[0], current[1], 0.0)
                bottom_following = (following[0], following[1], 0.0)
                top_current = (current[0], current[1], depth_mm)
                top_following = (following[0], following[1], depth_mm)

                triangles.extend(
                    (
                        (
                            bottom_current,
                            bottom_following,
                            top_following,
                        ),
                        (
                            bottom_current,
                            top_following,
                            top_current,
                        ),
                    )
                )

        return triangles

    @staticmethod
    def _clean_ring(coordinates) -> list:
        ring = []

        for coordinate in coordinates:
            point = (
                float(coordinate[0]),
                float(coordinate[1]),
            )

            if not ring or point != ring[-1]:
                ring.append(point)

        if len(ring) > 1 and ring[0] == ring[-1]:
            ring.pop()

        return ring
