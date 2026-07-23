"""
ATLAS Engine

Atlas Building Analyzer v1.2
Analyzes AtlasBuilding objects and creates a building profile.
"""

import warnings

from shapely.geometry import Polygon

from CORE.atlas_geometry import AtlasGeometry


class AtlasBuildingAnalyzer:
    @staticmethod
    def aspect_ratio(building):
        geometry = getattr(building, "geometry", None)

        if geometry and len(geometry) >= 3:
            xy_points = AtlasGeometry.latlon_to_xy(geometry)

            xs = [point[0] for point in xy_points]
            ys = [point[1] for point in xy_points]

            width = max(xs) - min(xs)
            depth = max(ys) - min(ys)
        else:
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
    def _footprint_polygon(building):
        geometry = getattr(building, "geometry", None)

        if not geometry or len(geometry) < 3:
            return None

        xy_points = AtlasGeometry.latlon_to_xy(geometry)

        if len(xy_points) > 1 and xy_points[0] == xy_points[-1]:
            xy_points = xy_points[:-1]

        if len(xy_points) < 3:
            return None

        polygon = Polygon(xy_points)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty or polygon.area <= 0.0:
            return None

        return polygon

    @staticmethod
    def _minimum_rotated_rectangle(polygon):
        with warnings.catch_warnings():
            warnings.simplefilter(
                "ignore",
                category=RuntimeWarning,
            )
            return polygon.minimum_rotated_rectangle

    @staticmethod
    def _minimum_rectangle_side_lengths(polygon):
        rectangle = (
            AtlasBuildingAnalyzer._minimum_rotated_rectangle(
                polygon
            )
        )
        coordinates = list(rectangle.exterior.coords)

        if len(coordinates) < 5:
            return None

        side_lengths = []

        for index in range(4):
            x1, y1 = coordinates[index]
            x2, y2 = coordinates[index + 1]

            length = (
                (x2 - x1) ** 2
                + (y2 - y1) ** 2
            ) ** 0.5

            if length > 0.0:
                side_lengths.append(length)

        if len(side_lengths) != 4:
            return None

        short_side = min(side_lengths)
        long_side = max(side_lengths)

        if short_side <= 0.0:
            return None

        return short_side, long_side

    @staticmethod
    def oriented_aspect_ratio(building):
        polygon = AtlasBuildingAnalyzer._footprint_polygon(building)

        if polygon is None:
            return 0.0

        side_lengths = (
            AtlasBuildingAnalyzer._minimum_rectangle_side_lengths(
                polygon
            )
        )

        if side_lengths is None:
            return 0.0

        short_side, long_side = side_lengths
        ratio = long_side / short_side

        return round(ratio, 2)

    @staticmethod
    def rectangularity(building):
        polygon = AtlasBuildingAnalyzer._footprint_polygon(building)

        if polygon is None:
            return 0.0

        rectangle = (
            AtlasBuildingAnalyzer._minimum_rotated_rectangle(
                polygon
            )
        )

        if rectangle.is_empty or rectangle.area <= 0.0:
            return 0.0

        value = polygon.area / rectangle.area
        value = min(max(value, 0.0), 1.0)

        return round(value, 4)

    @staticmethod
    def reflex_vertex_count(building):
        geometry = getattr(building, "geometry", None)

        if not geometry or len(geometry) < 4:
            return 0

        points = AtlasGeometry.latlon_to_xy(geometry)

        if len(points) > 1 and points[0] == points[-1]:
            points = points[:-1]

        if len(points) < 4:
            return 0

        signed_area = 0.0

        for index, point in enumerate(points):
            next_point = points[(index + 1) % len(points)]

            signed_area += (
                point[0] * next_point[1]
                - next_point[0] * point[1]
            )

        orientation = 1.0 if signed_area >= 0.0 else -1.0
        reflex_count = 0
        tolerance = 1e-9

        for index, current in enumerate(points):
            previous = points[index - 1]
            following = points[(index + 1) % len(points)]

            cross = (
                (current[0] - previous[0])
                * (following[1] - current[1])
                - (current[1] - previous[1])
                * (following[0] - current[0])
            )

            if cross * orientation < -tolerance:
                reflex_count += 1

        return reflex_count

    @staticmethod
    def is_concave(building):
        return AtlasBuildingAnalyzer.reflex_vertex_count(building) > 0

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

        if btype in (
            "house",
            "detached",
            "residential",
            "apartments",
        ):
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
            "aspect_ratio": (
                AtlasBuildingAnalyzer.aspect_ratio(building)
            ),
            "oriented_aspect_ratio": (
                AtlasBuildingAnalyzer.oriented_aspect_ratio(building)
            ),
            "rectangularity": (
                AtlasBuildingAnalyzer.rectangularity(building)
            ),
            "reflex_vertices": (
                AtlasBuildingAnalyzer.reflex_vertex_count(building)
            ),
            "is_concave": AtlasBuildingAnalyzer.is_concave(building),
            "category": AtlasBuildingAnalyzer.category(building),
            "print_score": AtlasBuildingAnalyzer.print_score(building),
            "tags": building.tags,
        }
