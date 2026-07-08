# CORE/atlas_surface_composer.py

from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles


class AtlasSurfaceComposer:
    """
    ATLAS Surface Composer v0.3
    Shapely Edition

    Görev:
    Base plate üst yüzeyi ile road polygonlarını tek yüzey mantığında birleştirir.

    Bu sürüm:
    - Base top surface = base rectangle - road union
    - Road floor surface = road union
    - Road side walls = road boundary
    """

    BASE_BOTTOM_Z = 0.00
    BASE_TOP_Z = 0.80
    ROAD_LEVEL_Z = 0.62

    @staticmethod
    def compose(base_plate, road_polygons=None, debug=True):
        if road_polygons is None:
            road_polygons = []

        base_bounds = AtlasSurfaceComposer._get_mesh_xy_bounds(base_plate)

        if not base_bounds:
            return base_plate

        road_polygons = AtlasSurfaceComposer._align_road_polygons_to_base(
            road_polygons,
            base_bounds,
        )

        mesh = AtlasSurfaceComposer._build_composed_surface(
            base_bounds,
            road_polygons,
        )

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS SURFACE COMPOSER REPORT")
            print("=" * 60)
            print(f"Base plate type : {base_plate.get('type', 'unknown')}")
            print(f"Road polygons   : {len(road_polygons)}")
            print(f"Triangles       : {len(mesh.get('triangles', []))}")
            print("Status          : shapely_surface_composition")
            print("=" * 60)
            print("")

        return mesh

    @staticmethod
    def _build_composed_surface(base_bounds, road_polygons):
        base_polygon = Polygon(
            [
                (base_bounds["min_x"], base_bounds["min_y"]),
                (base_bounds["max_x"], base_bounds["min_y"]),
                (base_bounds["max_x"], base_bounds["max_y"]),
                (base_bounds["min_x"], base_bounds["max_y"]),
            ]
        )

        road_shapes = []

        for road_polygon in road_polygons:
            points = road_polygon.get("points", [])

            if len(points) < 3:
                continue

            shape = Polygon(points)

            if shape.is_empty:
                continue

            if not shape.is_valid:
                shape = shape.buffer(0)

            if shape.is_empty:
                continue

            shape = shape.intersection(base_polygon)

            if not shape.is_empty:
                road_shapes.append(shape)

        if road_shapes:
            road_union = unary_union(road_shapes)
            base_top_shape = base_polygon.difference(road_union)
        else:
            road_union = None
            base_top_shape = base_polygon

        triangles = []
        bottom = []
        top = []
        walls = []

        AtlasSurfaceComposer._add_bottom_box(
            triangles=triangles,
            bottom=bottom,
            top=top,
            walls=walls,
            base_bounds=base_bounds,
        )

        AtlasSurfaceComposer._add_surface_shape(
            shape=base_top_shape,
            z=AtlasSurfaceComposer.BASE_TOP_Z,
            triangles=triangles,
        )

        if road_union is not None and not road_union.is_empty:
            AtlasSurfaceComposer._add_surface_shape(
                shape=road_union,
                z=AtlasSurfaceComposer.ROAD_LEVEL_Z,
                triangles=triangles,
            )

            AtlasSurfaceComposer._add_road_walls(
                shape=road_union,
                top_z=AtlasSurfaceComposer.BASE_TOP_Z,
                bottom_z=AtlasSurfaceComposer.ROAD_LEVEL_Z,
                triangles=triangles,
                walls=walls,
            )
            triangles = AtlasSurfaceComposer._snap_triangles(triangles)
            bottom = AtlasSurfaceComposer._snap_points(bottom)
            top = AtlasSurfaceComposer._snap_points(top)
            walls = AtlasSurfaceComposer._snap_walls(walls)

            return {
                "bottom": bottom,
                "top": top,
                "walls": walls,
                "triangles": triangles,
                "type": "composed_surface",
            }

    @staticmethod
    def _add_bottom_box(triangles, bottom, top, walls, base_bounds):
        min_x = base_bounds["min_x"]
        max_x = base_bounds["max_x"]
        min_y = base_bounds["min_y"]
        max_y = base_bounds["max_y"]

        z0 = AtlasSurfaceComposer.BASE_BOTTOM_Z
        z1 = AtlasSurfaceComposer.BASE_TOP_Z

        b = [
            (min_x, min_y, z0),
            (max_x, min_y, z0),
            (max_x, max_y, z0),
            (min_x, max_y, z0),
        ]

        t = [
            (min_x, min_y, z1),
            (max_x, min_y, z1),
            (max_x, max_y, z1),
            (min_x, max_y, z1),
        ]

        bottom.extend(b)
        top.extend(t)

        triangles.append((b[2], b[1], b[0]))
        triangles.append((b[3], b[2], b[0]))

        for i in range(4):
            j = (i + 1) % 4
            wall = (b[i], b[j], t[j], t[i])
            walls.append(wall)
            triangles.append((b[i], b[j], t[j]))
            triangles.append((b[i], t[j], t[i]))

    @staticmethod
    def _add_surface_shape(shape, z, triangles):
        for poly in AtlasSurfaceComposer._iter_polygons(shape):
            tris = constrained_delaunay_triangles(poly).geoms

            for tri in tris:
                centroid = tri.centroid

                if not poly.contains(centroid) and not poly.touches(centroid):
                    continue

                coords = list(tri.exterior.coords)

                if len(coords) < 4:
                    continue

                p1 = coords[0]
                p2 = coords[1]
                p3 = coords[2]

                triangles.append(
                    (
                        (p1[0], p1[1], z),
                        (p2[0], p2[1], z),
                        (p3[0], p3[1], z),
                    )
                )

    @staticmethod
    def _add_road_walls(shape, top_z, bottom_z, triangles, walls):
        for poly in AtlasSurfaceComposer._iter_polygons(shape):
            AtlasSurfaceComposer._add_wall_ring(
                coords=list(poly.exterior.coords),
                top_z=top_z,
                bottom_z=bottom_z,
                triangles=triangles,
                walls=walls,
            )

            for interior in poly.interiors:
                AtlasSurfaceComposer._add_wall_ring(
                    coords=list(interior.coords),
                    top_z=top_z,
                    bottom_z=bottom_z,
                    triangles=triangles,
                    walls=walls,
                )

    @staticmethod
    def _add_wall_ring(coords, top_z, bottom_z, triangles, walls):
        if len(coords) < 2:
            return

        for index in range(len(coords) - 1):
            p1 = coords[index]
            p2 = coords[index + 1]

            b1 = (p1[0], p1[1], bottom_z)
            b2 = (p2[0], p2[1], bottom_z)
            t1 = (p1[0], p1[1], top_z)
            t2 = (p2[0], p2[1], top_z)

            wall = (b1, b2, t2, t1)
            walls.append(wall)

            triangles.append((b1, b2, t2))
            triangles.append((b1, t2, t1))

    @staticmethod
    def _iter_polygons(shape):
        if shape.is_empty:
            return []

        if shape.geom_type == "Polygon":
            return [shape]

        if shape.geom_type == "MultiPolygon":
            return list(shape.geoms)

        return []

    @staticmethod
    def _align_road_polygons_to_base(road_polygons, base_bounds):
        road_bounds = AtlasSurfaceComposer._get_road_polygon_bounds(road_polygons)

        if not road_bounds:
            return road_polygons

        offset_x = base_bounds["min_x"] - road_bounds["min_x"]
        offset_y = base_bounds["min_y"] - road_bounds["min_y"]

        shifted = []

        for polygon in road_polygons:
            new_polygon = dict(polygon)
            new_points = []

            for x, y in polygon.get("points", []):
                new_points.append((x + offset_x, y + offset_y))

            new_polygon["points"] = new_points
            shifted.append(new_polygon)

        return shifted

    @staticmethod
    def _get_mesh_xy_bounds(mesh):
        points = []

        points.extend(mesh.get("bottom", []))
        points.extend(mesh.get("top", []))

        for triangle in mesh.get("triangles", []):
            points.extend(triangle)

        if not points:
            return None

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }

    @staticmethod
    def _get_road_polygon_bounds(road_polygons):
        points = []

        for polygon in road_polygons:
            points.extend(polygon.get("points", []))

        if not points:
            return None

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }

    @staticmethod
    def _snap_value(value, precision=6):
        return round(value, precision)

    @staticmethod
    def _snap_point(point):
        return (
            AtlasSurfaceComposer._snap_value(point[0]),
            AtlasSurfaceComposer._snap_value(point[1]),
            AtlasSurfaceComposer._snap_value(point[2]),
        )

    @staticmethod
    def _snap_points(points):
        return [AtlasSurfaceComposer._snap_point(point) for point in points]

    @staticmethod
    def _snap_triangles(triangles):
        return [
            (
                AtlasSurfaceComposer._snap_point(triangle[0]),
                AtlasSurfaceComposer._snap_point(triangle[1]),
                AtlasSurfaceComposer._snap_point(triangle[2]),
            )
            for triangle in triangles
        ]

    @staticmethod
    def _snap_walls(walls):
        return [
            (
                AtlasSurfaceComposer._snap_point(wall[0]),
                AtlasSurfaceComposer._snap_point(wall[1]),
                AtlasSurfaceComposer._snap_point(wall[2]),
                AtlasSurfaceComposer._snap_point(wall[3]),
            )
            for wall in walls
        ]

    @staticmethod
    def _add_base_hole_walls(shape, top_z, bottom_z, triangles, walls):
        for poly in AtlasSurfaceComposer._iter_polygons(shape):
            for interior in poly.interiors:
                AtlasSurfaceComposer._add_wall_ring(
                    coords=list(interior.coords),
                    top_z=top_z,
                    bottom_z=bottom_z,
                    triangles=triangles,
                    walls=walls,
                )
