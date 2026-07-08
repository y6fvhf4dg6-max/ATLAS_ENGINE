"""
ATLAS Engine

Atlas Building Analyzer v1.0
Analyzes AtlasBuilding objects and creates a building profile.
"""


class AtlasBuildingAnalyzer:
    @staticmethod
    def aspect_ratio(building):
        bbox = building.bbox

        if bbox is None:
            return 0.0

        width = abs(bbox["east"] - bbox["west"])
        depth = abs(bbox["north"] - bbox["south"])

        if width == 0 or depth == 0:
            return 0.0

        ratio = max(width, depth) / min(width, depth)

        return round(ratio, 2)

    @staticmethod
    def category(building):
        area = building.area_m2
        ratio = AtlasBuildingAnalyzer.aspect_ratio(building)
        btype = building.building_type

        if area < 10:
            return "too_small"

        if ratio > 8:
            return "too_long"

        if area > 5000:
            return "large_complex"

        if btype in ("office", "commercial"):
            return "business"

        if btype in ("house", "detached", "residential", "apartments"):
            return "residential"

        if btype in ("school", "hospital"):
            return "public"

        if btype in ("industrial", "warehouse"):
            return "industrial"

        return "normal"

    @staticmethod
    def print_score(building):
        score = 100

        area = building.area_m2
        ratio = AtlasBuildingAnalyzer.aspect_ratio(building)

        if area < 10:
            score -= 50

        if area > 5000:
            score -= 25

        if ratio > 8:
            score -= 30

        if building.quality_score is not None:
            score = min(score, building.quality_score)

        return max(score, 0)

    @staticmethod
    def analyze(building):
        return {
            "id": building.building_id,
            "type": building.building_type,
            "area_m2": round(building.area_m2, 2),
            "perimeter_m": round(building.perimeter_m, 2),
            "height_m": building.estimated_height,
            "levels": building.levels,
            "roof": building.roof_type,
            "aspect_ratio": AtlasBuildingAnalyzer.aspect_ratio(building),
            "category": AtlasBuildingAnalyzer.category(building),
            "print_score": AtlasBuildingAnalyzer.print_score(building),
            "tags": building.tags,
        }
