"""
ATLAS Engine

Atlas Local Map Clipper v1.0
Selects nearby buildings and trees around a local center point.
"""

import math


class AtlasLocalMapClipper:
    @staticmethod
    def distance(lat1, lon1, lat2, lon2):
        lat_m = (lat1 - lat2) * 111_320
        lon_m = (lon1 - lon2) * 111_320 * math.cos(math.radians(lat2))

        return math.sqrt((lat_m**2) + (lon_m**2))

    @staticmethod
    def building_center(building):
        geometry = building["geometry"]

        lat = sum(p[0] for p in geometry) / len(geometry)
        lon = sum(p[1] for p in geometry) / len(geometry)

        return lat, lon

    @staticmethod
    def clip(data, center_lat, center_lon, building_count=30, tree_count=30):
        buildings = data.get("buildings", [])
        trees = data.get("trees", [])

        ranked_buildings = []

        for building in buildings:
            b_lat, b_lon = AtlasLocalMapClipper.building_center(building)
            d = AtlasLocalMapClipper.distance(
                center_lat,
                center_lon,
                b_lat,
                b_lon,
            )

            ranked_buildings.append((d, building))

        ranked_buildings.sort(key=lambda item: item[0])

        selected_buildings = [item[1] for item in ranked_buildings[:building_count]]

        ranked_trees = []

        for tree in trees:
            d = AtlasLocalMapClipper.distance(
                center_lat,
                center_lon,
                tree["lat"],
                tree["lon"],
            )

            ranked_trees.append((d, tree))

        ranked_trees.sort(key=lambda item: item[0])

        selected_trees = [item[1] for item in ranked_trees[:tree_count]]

        return {
            "buildings": selected_buildings,
            "trees": selected_trees,
        }
