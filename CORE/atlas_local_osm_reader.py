# CORE/atlas_local_osm_reader.py

"""
ATLAS Engine

Atlas Local OSM Reader v1.1
Reads local .osm.pbf files without Overpass API.

Supported objects:
- buildings
- trees
- roads
- pedestrian paths
"""

import osmium


class AtlasLocalOSMReader(osmium.SimpleHandler):
    def __init__(self, bbox):
        super().__init__()

        self.south, self.west, self.north, self.east = bbox

        self.buildings = []
        self.trees = []
        self.roads = []
        self.pedestrian_paths = []

    def inside_bbox(self, lat, lon):
        return self.south <= lat <= self.north and self.west <= lon <= self.east

    def node(self, n):
        if not n.location.valid():
            return

        lat = n.location.lat
        lon = n.location.lon

        if not self.inside_bbox(lat, lon):
            return

        tags = dict(n.tags)

        if tags.get("natural") == "tree":
            self.trees.append(
                {
                    "id": n.id,
                    "lat": lat,
                    "lon": lon,
                    "tags": tags,
                }
            )

    def way(self, w):
        tags = dict(w.tags)

        if "building" in tags:
            self._read_building(w, tags)
            return

        if "highway" in tags:
            self._read_highway(w, tags)
            return

    def _read_building(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 4:
            return

        if not self._all_points_inside_bbox(geometry):
            return

        if geometry[0] == geometry[-1]:
            geometry.pop()

        self.buildings.append(
            {
                "id": w.id,
                "geometry": geometry,
                "tags": tags,
            }
        )

    def _read_highway(self, w, tags):
        geometry = self._extract_way_geometry(w)

        if len(geometry) < 2:
            return

        if not self._any_point_inside_bbox(geometry):
            return

        road_type = tags.get("highway")

        item = {
            "id": w.id,
            "geometry": geometry,
            "tags": tags,
            "road_type": road_type,
        }

        if self._is_pedestrian_path(tags):
            self.pedestrian_paths.append(item)
        elif self._is_vehicle_road(tags):
            self.roads.append(item)

    def _extract_way_geometry(self, way):
        geometry = []

        for node in way.nodes:
            if not node.location.valid():
                continue

            lat = node.location.lat
            lon = node.location.lon

            geometry.append((lat, lon))

        return geometry

    def _all_points_inside_bbox(self, geometry):
        for lat, lon in geometry:
            if not self.inside_bbox(lat, lon):
                return False

        return True

    def _any_point_inside_bbox(self, geometry):
        for lat, lon in geometry:
            if self.inside_bbox(lat, lon):
                return True

        return False

    @staticmethod
    def _is_pedestrian_path(tags):
        highway = tags.get("highway")

        pedestrian_types = {
            "footway",
            "path",
            "pedestrian",
            "steps",
            "cycleway",
            "bridleway",
        }

        if highway in pedestrian_types:
            return True

        if tags.get("foot") in {"yes", "designated"}:
            return True

        return False

    @staticmethod
    def _is_vehicle_road(tags):
        highway = tags.get("highway")

        vehicle_types = {
            "motorway",
            "trunk",
            "primary",
            "secondary",
            "tertiary",
            "unclassified",
            "residential",
            "service",
            "living_street",
            "road",
        }

        return highway in vehicle_types

    @staticmethod
    def read(pbf_path, bbox):
        reader = AtlasLocalOSMReader(bbox)
        reader.apply_file(pbf_path, locations=True)

        return {
            "buildings": reader.buildings,
            "trees": reader.trees,
            "roads": reader.roads,
            "pedestrian_paths": reader.pedestrian_paths,
        }
