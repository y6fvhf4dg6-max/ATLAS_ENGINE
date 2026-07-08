"""
ATLAS Engine

OSM Building Parser v1.1
Converts raw OSM Overpass data into clean AtlasBuilding objects.
"""

from CORE.atlas_building import AtlasBuilding


class OSMBuildingParser:
    def __init__(self, data):
        self.data = data
        self.elements = data.get("elements", [])
        self.nodes = {}

    def index_nodes(self):
        for element in self.elements:
            if element.get("type") == "node":
                self.nodes[element["id"]] = (
                    element["lat"],
                    element["lon"],
                )

    def clean_geometry(self, geometry):
        clean = []

        for point in geometry:
            if not clean or point != clean[-1]:
                clean.append(point)

        if len(clean) > 1 and clean[0] == clean[-1]:
            clean.pop()

        return clean

    def parse(self):
        self.index_nodes()

        buildings = []

        for element in self.elements:
            if element.get("type") != "way":
                continue

            tags = element.get("tags", {})

            if "building" not in tags:
                continue

            geometry = []

            for node_id in element.get("nodes", []):
                point = self.nodes.get(node_id)

                if point is not None:
                    geometry.append(point)

            geometry = self.clean_geometry(geometry)

            if len(geometry) < 3:
                continue

            building = AtlasBuilding(
                building_id=element["id"],
                source="OSM",
                geometry=geometry,
                tags=tags,
            )

            buildings.append(building)

        return buildings
