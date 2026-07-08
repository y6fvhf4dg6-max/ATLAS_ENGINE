"""
ATLAS Engine 2.0

Module : Local OSM
Version: 1.2

Purpose:
Read buildings, roads and water features from local Geofabrik PBF files.
Output format is compatible with ATLAS engines.
"""

import osmium


PBF_PATH = "DATA/OSM/hessen-latest.osm.pbf"


WATER_TAGS = {
    "natural": {"water", "bay"},
    "water": {"lake", "pond", "reservoir", "river", "basin"},
    "waterway": {"river", "stream", "canal", "ditch"},
    "landuse": {"reservoir"},
}


class AtlasLocalOSMHandler(osmium.SimpleHandler):

    def __init__(self, bbox):
        super().__init__()

        self.bbox = bbox
        self.buildings = []
        self.roads = []
        self.water = []

    def is_inside_bbox(self, lon, lat):
        return (
            self.bbox["west"] <= lon <= self.bbox["east"]
            and self.bbox["south"] <= lat <= self.bbox["north"]
        )

    def is_water(self, tags):
        for key, values in WATER_TAGS.items():
            if key in tags and tags[key] in values:
                return True

        return False

    def way(self, way):
        try:
            tags = dict(way.tags)

            is_building = "building" in tags
            is_road = "highway" in tags
            is_water = self.is_water(tags)

            if not is_building and not is_road and not is_water:
                return

            coords = []

            for node in way.nodes:
                if not node.location.valid():
                    continue

                lon = node.location.lon
                lat = node.location.lat
                coords.append((lat, lon))

            if len(coords) < 2:
                return

            inside = any(
                self.is_inside_bbox(lon, lat)
                for lat, lon in coords
            )

            if not inside:
                return

            item = {
                "type": "way",
                "id": way.id,
                "tags": tags,
                "coords": coords,
            }

            if is_building:
                self.buildings.append(item)

            if is_road:
                self.roads.append(item)

            if is_water:
                self.water.append(item)

        except Exception:
            return


def read_local_osm_bbox(bbox, pbf_path=PBF_PATH):
    handler = AtlasLocalOSMHandler(bbox)

    print("Local PBF okunuyor:", pbf_path)

    handler.apply_file(
        pbf_path,
        locations=True
    )

    return handler.buildings, handler.roads, handler.water


def convert_items_to_old_osm_format(items):
    elements = []
    node_lookup = {}
    node_id = 1

    for item in items:
        node_ids = []

        for lat, lon in item["coords"]:
            node_lookup[node_id] = {
                "lat": lat,
                "lon": lon,
            }

            node_ids.append(node_id)
            node_id += 1

        elements.append(
            {
                "type": "way",
                "id": item["id"],
                "tags": item["tags"],
                "nodes": node_ids,
            }
        )

    return {
        "elements": elements
    }, node_lookup


def get_buildings_and_lookup(bbox):
    buildings, _, _ = read_local_osm_bbox(bbox)

    print("Local bina sayısı:", len(buildings))

    return convert_items_to_old_osm_format(buildings)


def get_roads_and_lookup(bbox):
    _, roads, _ = read_local_osm_bbox(bbox)

    print("Local yol sayısı:", len(roads))

    return convert_items_to_old_osm_format(roads)


def get_water_and_lookup(bbox):
    _, _, water = read_local_osm_bbox(bbox)

    print("Local su öğesi sayısı:", len(water))

    return convert_items_to_old_osm_format(water)

def get_buildings_and_lookup_from_items(buildings):
    print("Cache bina sayısı:", len(buildings))
    return convert_items_to_old_osm_format(buildings)


def get_roads_and_lookup_from_items(roads):
    print("Cache yol sayısı:", len(roads))
    return convert_items_to_old_osm_format(roads)


def get_water_and_lookup_from_items(water):
    print("Cache su öğesi sayısı:", len(water))
    return convert_items_to_old_osm_format(water)