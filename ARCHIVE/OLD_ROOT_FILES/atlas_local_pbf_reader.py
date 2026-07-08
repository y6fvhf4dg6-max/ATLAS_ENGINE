"""
ATLAS Engine 2.0

Module : Local PBF Reader
Version: 1.0

Purpose:
Read local .osm.pbf files with pyosmium/osmium and extract OSM ways
inside a bounding box without Overpass.
"""

import osmium

from atlas_bbox_engine import create_bbox


PBF_PATH = "DATA/OSM/hessen-latest.osm.pbf"


class AtlasPBFHandler(osmium.SimpleHandler):

    def __init__(self, bbox):
        super().__init__()

        self.bbox = bbox
        self.buildings = []
        self.roads = []

    def node_in_bbox(self, node):
        lon = node.location.lon
        lat = node.location.lat

        return (
            self.bbox["west"] <= lon <= self.bbox["east"]
            and self.bbox["south"] <= lat <= self.bbox["north"]
        )

    def way(self, way):
        try:
            tags = dict(way.tags)

            has_building = "building" in tags
            has_highway = "highway" in tags

            if not has_building and not has_highway:
                return

            coords = []

            for node in way.nodes:
                if not node.location.valid():
                    continue

                lon = node.location.lon
                lat = node.location.lat

                coords.append((lon, lat))

            if not coords:
                return

            inside = any(
                self.bbox["west"] <= lon <= self.bbox["east"]
                and self.bbox["south"] <= lat <= self.bbox["north"]
                for lon, lat in coords
            )

            if not inside:
                return

            item = {
                "id": way.id,
                "tags": tags,
                "nodes": coords,
            }

            if has_building:
                self.buildings.append(item)

            if has_highway:
                self.roads.append(item)

        except Exception:
            return


def read_pbf_bbox(pbf_path, bbox):
    handler = AtlasPBFHandler(bbox)

    print("PBF okunuyor:", pbf_path)
    handler.apply_file(
        pbf_path,
        locations=True
    )

    return handler.buildings, handler.roads


def main():
    print("=" * 60)
    print("ATLAS LOCAL PBF READER v1.0")
    print("=" * 60)

    latitude = 50.1104684
    longitude = 8.6816587
    size_m = 1000

    bbox = create_bbox(
        latitude,
        longitude,
        size_m
    )

    print("BBOX:", bbox)
    print()

    buildings, roads = read_pbf_bbox(
        PBF_PATH,
        bbox
    )

    print()
    print("Bulunan bina:", len(buildings))
    print("Bulunan yol :", len(roads))

    if buildings:
        print()
        print("İlk bina:")
        print(buildings[0])

    if roads:
        print()
        print("İlk yol:")
        print(roads[0])

    print("=" * 60)


if __name__ == "__main__":
    main()