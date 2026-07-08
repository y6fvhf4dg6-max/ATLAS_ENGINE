"""
ATLAS Engine

Atlas Building Quality Engine v1.0
Calculates quality score for AtlasBuilding objects.
"""


class AtlasBuildingQuality:
    @staticmethod
    def calculate(building):
        score = 0

        # Geometry exists
        if building.geometry and building.point_count >= 3:
            score += 25

        # Area exists
        if building.area_m2 and building.area_m2 > 0:
            score += 20

        # Perimeter exists
        if building.perimeter_m and building.perimeter_m > 0:
            score += 10

        # Height exists
        if building.height is not None:
            score += 20

        # Levels exist
        if building.levels is not None:
            score += 10

        # Roof exists
        if building.roof_type is not None:
            score += 10

        # Source bonus
        if building.source == "OSM":
            score += 5

        return min(score, 100)
