"""
ATLAS Engine

Atlas Building Model v1.2
Represents one building inside ATLAS.
"""

from CORE.atlas_geometry import AtlasGeometry
from CORE.atlas_building_quality import AtlasBuildingQuality
from CORE.atlas_height_engine import AtlasHeightEngine


class AtlasBuilding:
    def __init__(self, building_id, source, geometry, tags):
        self.building_id = building_id
        self.source = source
        self.geometry = geometry
        self.tags = tags

        self.building_type = self.tags.get("building")
        self.height = self.parse_height()
        self.levels = self.parse_levels()
        self.roof_type = self.tags.get("roof:shape")

        self.centroid = self.calculate_centroid()
        self.bbox = self.calculate_bbox()
        self.point_count = len(self.geometry)
        self.area_m2 = AtlasGeometry.polygon_area_m2(self.geometry)
        self.perimeter_m = AtlasGeometry.polygon_perimeter_m(self.geometry)
        self.quality_score = AtlasBuildingQuality.calculate(self)
        self.estimated_height = AtlasHeightEngine.estimate(self)

    def parse_height(self):
        height_value = self.tags.get("height")

        if height_value is None:
            return None

        try:
            return float(str(height_value).replace("m", "").strip())
        except ValueError:
            return None

    def parse_levels(self):
        levels_value = self.tags.get("building:levels")

        if levels_value is None:
            return None

        try:
            return int(float(levels_value))
        except ValueError:
            return None

    def calculate_centroid(self):
        if not self.geometry:
            return None

        lat_sum = 0
        lon_sum = 0

        for lat, lon in self.geometry:
            lat_sum += lat
            lon_sum += lon

        return (
            lat_sum / len(self.geometry),
            lon_sum / len(self.geometry),
        )

    def calculate_bbox(self):
        if not self.geometry:
            return None

        lats = [point[0] for point in self.geometry]
        lons = [point[1] for point in self.geometry]

        return {
            "south": min(lats),
            "north": max(lats),
            "west": min(lons),
            "east": max(lons),
        }

    def summary(self):
        return {
            "id": self.building_id,
            "source": self.source,
            "points": self.point_count,
            "area_m2": round(self.area_m2, 2),
            "perimeter_m": round(self.perimeter_m, 2),
            "quality": self.quality_score,
            "estimated_height": self.estimated_height,
            "centroid": self.centroid,
            "bbox": self.bbox,
            "building": self.building_type,
            "height": self.height,
            "levels": self.levels,
            "roof": self.roof_type,
        }
