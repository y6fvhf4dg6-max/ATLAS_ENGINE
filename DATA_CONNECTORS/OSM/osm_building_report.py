"""
ATLAS Engine

OSM Building Report v1.0
Analyzes raw OSM building data.
"""


class OSMBuildingReport:
    def __init__(self, data):
        self.data = data
        self.elements = data.get("elements", [])

    def analyze(self):
        nodes = 0
        ways = 0
        relations = 0
        building_ways = 0
        height_count = 0
        levels_count = 0
        roof_count = 0

        for element in self.elements:
            element_type = element.get("type")

            if element_type == "node":
                nodes += 1

            elif element_type == "way":
                ways += 1
                tags = element.get("tags", {})

                if "building" in tags:
                    building_ways += 1

                    if "height" in tags:
                        height_count += 1

                    if "building:levels" in tags:
                        levels_count += 1

                    if "roof:shape" in tags or "roof:levels" in tags:
                        roof_count += 1

            elif element_type == "relation":
                relations += 1

        return {
            "total_elements": len(self.elements),
            "nodes": nodes,
            "ways": ways,
            "relations": relations,
            "building_ways": building_ways,
            "height_count": height_count,
            "levels_count": levels_count,
            "roof_count": roof_count,
        }

    def print_report(self):
        report = self.analyze()

        print()
        print("=" * 60)
        print("OSM BUILDING REPORT")
        print("=" * 60)
        print("Total elements  :", report["total_elements"])
        print("Nodes           :", report["nodes"])
        print("Ways            :", report["ways"])
        print("Relations       :", report["relations"])
        print("Building ways   :", report["building_ways"])
        print("Height tags     :", report["height_count"])
        print("Levels tags     :", report["levels_count"])
        print("Roof tags       :", report["roof_count"])
        print("=" * 60)

        return report
