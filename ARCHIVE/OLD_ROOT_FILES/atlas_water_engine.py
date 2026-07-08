"""
ATLAS Engine 2.0

Module : Water Engine
Version: 1.2

Purpose:
Create simple water meshes from local OSM water data.
"""

from shapely.geometry import LineString, Polygon, MultiPolygon

from atlas_extrusion import extrude_mesh
from atlas_geometry import resolve_node_coordinates
from atlas_mesh_builder import triangulate_polygon
from atlas_model_space import coordinates_to_model_points


WATER_HEIGHT_MM = 0.80
WATER_TERRAIN_OFFSET_MM = 0.60

WATERWAY_WIDTHS_MM = {
    "river": 2.5,
    "canal": 1.8,
    "stream": 0.8,
    "ditch": 0.5,
}


class AtlasWaterEngine:

    def __init__(self, context):
        self.context = context
        self.valid_count = 0
        self.skipped_count = 0

    def sample_terrain_height(self, x, y):
        if self.context.terrain_sampler is None:
            return 0.0

        return self.context.terrain_sampler.get_height(x, y)

    def place_mesh_on_terrain(self, points_3d):
        placed_points = []

        for x, y, z in points_3d:
            terrain_z = self.sample_terrain_height(x, y)

            placed_points.append(
                (
                    x,
                    y,
                    terrain_z + WATER_TERRAIN_OFFSET_MM + z
                )
            )

        return placed_points

    def get_model_points(self, element):
        coordinates = resolve_node_coordinates(
            element["nodes"],
            self.context.node_lookup_water
        )

        return coordinates_to_model_points(
            coordinates,
            self.context.bounds,
            self.context.model_size_mm
        )

    def water_width_mm(self, tags):
        waterway = tags.get("waterway")

        if waterway in WATERWAY_WIDTHS_MM:
            return WATERWAY_WIDTHS_MM[waterway]

        return 1.2

    def line_to_polygons(self, model_points, width_mm):
        if len(model_points) < 2:
            return []

        line = LineString(model_points)

        if line.length <= 0:
            return []

        water_shape = line.buffer(
            width_mm / 2,
            cap_style=2,
            join_style=2
        )

        if water_shape.is_empty:
            return []

        if isinstance(water_shape, Polygon):
            return [water_shape]

        if isinstance(water_shape, MultiPolygon):
            return list(water_shape.geoms)

        return []

    def polygon_to_model_points(self, polygon):
        points = list(polygon.exterior.coords)

        if len(points) > 1 and points[0] == points[-1]:
            points = points[:-1]

        return points

    def add_water_polygon(self, polygon):
        model_points = self.polygon_to_model_points(polygon)

        if len(model_points) < 3:
            return False

        polygon, vertices, triangles = triangulate_polygon(
            model_points
        )

        points_3d, faces = extrude_mesh(
            vertices,
            triangles,
            WATER_HEIGHT_MM
        )

        points_3d = self.place_mesh_on_terrain(points_3d)

        self.context.scene.add_mesh(
            points_3d,
            faces,
            layer_name="water"
        )

        return True

    def build(self):
        print()
        print("=" * 60)
        print("ATLAS WATER ENGINE v1.2")
        print("=" * 60)

        if self.context.osm_water_data is None:
            print("Water data yok. Water Engine atlandı.")
            print("=" * 60)
            return

        if self.context.node_lookup_water is None:
            print("Water node lookup yok. Water Engine atlandı.")
            print("=" * 60)
            return

        water_elements = self.context.osm_water_data.get("elements", [])

        print("Su öğesi:", len(water_elements))

        for element in water_elements:
            try:
                tags = element.get("tags", {})
                model_points = self.get_model_points(element)

                waterway = tags.get("waterway")
                is_line_water = waterway in ["river", "stream", "canal", "ditch"]

                if is_line_water:
                    width = self.water_width_mm(tags)

                    water_polygons = self.line_to_polygons(
                        model_points,
                        width
                    )
                else:
                    if len(model_points) < 3:
                        self.skipped_count += 1
                        continue

                    water_polygons = [
                        Polygon(model_points)
                    ]

                if not water_polygons:
                    self.skipped_count += 1
                    continue

                added_any = False

                for water_polygon in water_polygons:
                    if water_polygon.is_empty:
                        continue

                    if not water_polygon.is_valid:
                        continue

                    if water_polygon.area <= 0:
                        continue

                    if self.add_water_polygon(water_polygon):
                        added_any = True

                if added_any:
                    self.valid_count += 1

                    print(
                        "OK:",
                        self.valid_count,
                        "| OSM:",
                        element.get("id"),
                        "| waterway:",
                        tags.get("waterway"),
                        "| water:",
                        tags.get("water"),
                        "| name:",
                        tags.get("name")
                    )
                else:
                    self.skipped_count += 1

            except Exception as error:
                self.skipped_count += 1
                print("Atlandı:", element.get("id"), "|", error)

        print()
        print("Water Engine özeti")
        print("------------------")
        print("Geçerli su :", self.valid_count)
        print("Atlanan su :", self.skipped_count)
        print("=" * 60)