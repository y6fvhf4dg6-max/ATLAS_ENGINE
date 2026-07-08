"""
ATLAS Engine

Atlas Height Engine v1.0
Determines usable building height for AtlasBuilding objects.
"""


class AtlasHeightEngine:
    DEFAULT_LEVEL_HEIGHT_M = 3.0

    DEFAULT_HEIGHTS = {
        "house": 6.0,
        "detached": 6.0,
        "residential": 9.0,
        "apartments": 12.0,
        "commercial": 12.0,
        "office": 18.0,
        "school": 12.0,
        "hospital": 18.0,
        "industrial": 10.0,
        "yes": 9.0,
    }

    @staticmethod
    def estimate(building):
        if building.height is not None:
            return building.height

        if building.levels is not None:
            return building.levels * AtlasHeightEngine.DEFAULT_LEVEL_HEIGHT_M

        building_type = building.building_type

        if building_type in AtlasHeightEngine.DEFAULT_HEIGHTS:
            return AtlasHeightEngine.DEFAULT_HEIGHTS[building_type]

        return 9.0
