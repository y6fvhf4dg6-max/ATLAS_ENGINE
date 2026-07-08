"""
ATLAS Engine 2.0

Module : Landmark Context
Version: 1.0

Purpose:
Detect landmarks inside current OSM building data and create
protected landmark zones.

Landmark zones allow ATLAS to preserve small but important
buildings around cathedrals, churches, palaces, castles, museums
and other culturally important structures.
"""

from shapely.geometry import Point

from atlas_geometry import resolve_node_coordinates
from atlas_model_space import coordinates_to_model_points
from atlas_tag_analyzer import (
    get_landmark_score,
    is_landmark,
    landmark_category,
)


DEFAULT_PROTECTION_RADIUS_MM = 28.0

CATEGORY_RADIUS_MM = {
    "christian_religious": 35.0,
    "mosque": 35.0,
    "historic_power": 35.0,
    "museum": 28.0,
    "civic": 28.0,
    "landmark": 25.0,
}


class AtlasLandmarkContext:

    def __init__(self, bounds, model_size_mm, node_lookup):
        self.bounds = bounds
        self.model_size_mm = model_size_mm
        self.node_lookup = node_lookup
        self.landmarks = []

    def element_to_model_points(self, element):
        coordinates = resolve_node_coordinates(
            element["nodes"],
            self.node_lookup
        )

        if len(coordinates) > 1 and coordinates[0] == coordinates[-1]:
            coordinates = coordinates[:-1]

        return coordinates_to_model_points(
            coordinates,
            self.bounds,
            self.model_size_mm
        )

    def polygon_centroid(self, model_points):
        if len(model_points) < 3:
            return None

        xs = [p[0] for p in model_points]
        ys = [p[1] for p in model_points]

        return (
            sum(xs) / len(xs),
            sum(ys) / len(ys)
        )

    def protection_radius_mm(self, category):
        return CATEGORY_RADIUS_MM.get(
            category,
            DEFAULT_PROTECTION_RADIUS_MM
        )

    def build_from_osm(self, osm_building_data):
        print()
        print("=" * 60)
        print("ATLAS LANDMARK CONTEXT v1.0")
        print("=" * 60)

        self.landmarks = []

        elements = osm_building_data.get("elements", [])

        for element in elements:
            tags = element.get("tags", {})

            if not is_landmark(tags):
                continue

            if "nodes" not in element:
                continue

            try:
                model_points = self.element_to_model_points(element)
                centroid = self.polygon_centroid(model_points)

                if centroid is None:
                    continue

                category = landmark_category(tags)
                radius = self.protection_radius_mm(category)

                landmark = {
                    "osm_id": element.get("id"),
                    "name": tags.get("name"),
                    "category": category,
                    "score": get_landmark_score(tags),
                    "center": centroid,
                    "radius_mm": radius,
                    "tags": tags,
                }

                self.landmarks.append(landmark)

                print(
                    "LANDMARK ZONE:",
                    "| OSM:", landmark["osm_id"],
                    "| Name:", landmark["name"],
                    "| Category:", landmark["category"],
                    "| Score:", landmark["score"],
                    "| Center:", (
                        round(centroid[0], 2),
                        round(centroid[1], 2)
                    ),
                    "| Radius:", radius,
                    "mm"
                )

            except Exception as error:
                print("Landmark zone atlandı:", element.get("id"), "|", error)

        print()
        print("Landmark zone sayısı:", len(self.landmarks))
        print("=" * 60)

    def is_point_inside_landmark_zone(self, x, y):
        point = Point(x, y)

        for landmark in self.landmarks:
            cx, cy = landmark["center"]
            center = Point(cx, cy)

            if point.distance(center) <= landmark["radius_mm"]:
                return True

        return False

    def nearest_landmark(self, x, y):
        if not self.landmarks:
            return None

        point = Point(x, y)

        nearest = None
        nearest_distance = None

        for landmark in self.landmarks:
            cx, cy = landmark["center"]
            center = Point(cx, cy)
            distance = point.distance(center)

            if nearest is None or distance < nearest_distance:
                nearest = landmark
                nearest_distance = distance

        return nearest