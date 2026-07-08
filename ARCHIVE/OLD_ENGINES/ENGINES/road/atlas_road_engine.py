from shapely.geometry import LineString, Polygon, MultiPolygon

from atlas_extrusion import extrude_mesh
from atlas_geometry import resolve_node_coordinates
from atlas_mesh_builder import triangulate_polygon
from atlas_model_space import coordinates_to_model_points


MAX_ROADS = 120
ROAD_HEIGHT_MM = 0.45
ROAD_TERRAIN_OFFSET_MM = 0.55


ROAD_WIDTHS_MM = {
    "motorway": 3.2,
    "trunk": 2.8,
    "primary": 2.4,
    "secondary": 2.0,
    "tertiary": 1.7,
    "residential": 1.3,
    "unclassified": 1.2,
    "service": 0.9,
    "living_street": 1.0,
    "pedestrian": 1.1,
    "footway": 0.85,
    "cycleway": 0.85,
    "path": 0.75,
    "steps": 0.85,
}


LOW_DETAIL_SKIP_TYPES = {
    "footway",
    "cycleway",
    "path",
    "steps",
}


class AtlasRoadEngine:

    def __init__(self, context):
        self.context = context

    def is_road_way(self, element):
        return (
            element.get("type") == "way"
            and "tags" in element
            and "highway" in element["tags"]
            and "nodes" in element
        )

    def road_type(self, element):
        return element["tags"].get("highway", "unknown")

    def should_skip_road(self, highway_type):
        detail_engine = getattr(self.context, "detail_engine", None)

        if detail_engine is None:
            return False

        if highway_type in LOW_DETAIL_SKIP_TYPES:
            return not detail_engine.should_show_footways()

        return False

    def road_width_mm(self, highway_type):
        width = ROAD_WIDTHS_MM.get(highway_type, 0.9)

        detail_engine = getattr(self.context, "detail_engine", None)

        if detail_engine is not None:
            minimum_width = max(
                0.75,
                detail_engine.real_m_to_model_mm(
                    detail_engine.minimum_road_width_m()
                )
            )

            width = max(width, minimum_width)

        return round(width, 2)

    def road_to_model_points(self, element):
        coordinates = resolve_node_coordinates(
            element["nodes"],
            self.context.node_lookup_roads
        )

        return coordinates_to_model_points(
            coordinates,
            self.context.bounds,
            self.context.model_size_mm
        )

    def road_points_to_polygons(self, model_points, width_mm):
        if len(model_points) < 2:
            return []

        line = LineString(model_points)

        if line.length <= 0:
            return []

        road_shape = line.buffer(
            width_mm / 2,
            cap_style=2,
            join_style=2
        )

        if road_shape.is_empty:
            return []

        if isinstance(road_shape, Polygon):
            return [road_shape]

        if isinstance(road_shape, MultiPolygon):
            return list(road_shape.geoms)

        return []

    def polygon_to_model_points(self, polygon):
        points = list(polygon.exterior.coords)

        if len(points) > 1 and points[0] == points[-1]:
            points = points[:-1]

        return points

    def place_mesh_on_terrain(self, points_3d):
        placed_points = []

        for x, y, z in points_3d:
            if self.context.terrain_sampler is None:
                terrain_z = 0.0
            else:
                terrain_z = self.context.terrain_sampler.get_height(x, y)

            placed_points.append(
                (
                    x,
                    y,
                    terrain_z + ROAD_TERRAIN_OFFSET_MM + z
                )
            )

        return placed_points

    def build(self):
        print()
        print("=" * 60)
        print("ATLAS ROAD ENGINE v2.0 - ADAPTIVE ROAD WIDTH")
        print("=" * 60)

        if self.context.osm_road_data is None:
            raise ValueError("Context içinde OSM yol verisi yok.")

        if self.context.node_lookup_roads is None:
            raise ValueError("Context içinde yol node lookup yok.")

        if self.context.scene is None:
            raise ValueError("Context içinde Scene Engine yok.")

        skipped_by_detail = 0

        for element in self.context.osm_road_data["elements"]:

            if not self.is_road_way(element):
                continue

            self.context.road_checked_count += 1

            if self.context.road_valid_count >= MAX_ROADS:
                break

            try:
                highway = self.road_type(element)

                if self.should_skip_road(highway):
                    skipped_by_detail += 1
                    self.context.road_skipped_count += 1
                    continue

                width = self.road_width_mm(highway)

                model_points = self.road_to_model_points(element)

                road_polygons = self.road_points_to_polygons(
                    model_points,
                    width
                )

                if not road_polygons:
                    self.context.road_skipped_count += 1
                    continue

                for road_polygon in road_polygons:
                    road_model_points = self.polygon_to_model_points(
                        road_polygon
                    )

                    polygon, vertices, triangles = triangulate_polygon(
                        road_model_points
                    )

                    points_3d, faces = extrude_mesh(
                        vertices,
                        triangles,
                        ROAD_HEIGHT_MM
                    )

                    points_3d = self.place_mesh_on_terrain(points_3d)

                    self.context.scene.add_mesh(
                        points_3d,
                        faces,
                        layer_name="roads"
                    )

                self.context.road_valid_count += 1

                print(
                    "OK:",
                    self.context.road_valid_count,
                    "| OSM:",
                    element["id"],
                    "| Tür:",
                    highway,
                    "| Genişlik:",
                    width,
                    "mm"
                )

            except Exception as error:
                self.context.road_skipped_count += 1
                print("Atlandı:", element.get("id"), "|", error)

        print()
        print("Road Engine özeti")
        print("-----------------")
        print("Denenen yol       :", self.context.road_checked_count)
        print("Geçerli yol       :", self.context.road_valid_count)
        print("Atlanan yol       :", self.context.road_skipped_count)
        print("Detaydan elenen   :", skipped_by_detail)
        print("=" * 60)