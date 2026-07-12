"""
ATLAS Castle Footprint Regularizer v0.1

OSM footprint geometrisinin doğrulanmış gerçek mimariyle
çeliştiği kale kuleleri için, bina mesh'i oluşturulmadan önce
kontrollü geometri düzeltmesi uygular.

Temel ilkeler:
- Ham OSM nesnesini yerinde değiştirmez
- Yalnız kale içinde sınıflandırılmış kuleleri işler
- Normal binalara ve minarelere dokunmaz
- Gerçek yuvarlak kuleleri genel olarak korur
- Landmark düzeltmeleri açık bir kayıt üzerinden uygulanır
"""

import math
import unicodedata
import warnings

from shapely.geometry import Polygon

from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)


class AtlasCastleFootprintRegularizer:
    TOWER_PROFILES = {
        "main_tower",
        "defensive_tower",
        "gate_tower",
    }

    # Gerçek mimarisi doğrulanmış landmark düzeltmeleri.
    #
    # Bu listedeki kalelerin kule footprint'leri OSM'de
    # kavisli veya gereğinden fazla noktalı görünse bile
    # köşeli kule geometrisine dönüştürülür.
    FORCE_ANGULAR_CASTLES = {
        "burg hohenzollern",
    }

    ROUND_SHAPE_VALUES = {
        "round",
        "circular",
        "circle",
        "cylindrical",
        "cylinder",
    }

    MIN_RECTANGLE_AREA_RATIO = 0.55
    MAX_RECTANGLE_AREA_RATIO = 1.75

    @staticmethod
    def prepare(
        raw_building,
        castles,
    ):
        if not raw_building:
            return raw_building

        prepared = dict(raw_building)

        prepared["tags"] = dict(
            raw_building.get(
                "tags",
                {},
            )
        )

        prepared["geometry"] = list(
            raw_building.get(
                "geometry",
                [],
            )
        )

        profile = AtlasCastleBuildingProfiler.profile(
            raw_building=prepared,
            castles=castles,
        )

        profile_name = profile.get("profile")

        if (
            not profile.get(
                "inside_castle",
                False,
            )
            or profile_name not in AtlasCastleFootprintRegularizer.TOWER_PROFILES
        ):
            return prepared

        containing_castle = AtlasCastleFootprintRegularizer._find_containing_castle(
            raw_building=prepared,
            castles=castles,
        )

        if containing_castle is None:
            return prepared

        castle_name = AtlasCastleFootprintRegularizer._normalize_text(
            containing_castle.get(
                "tags",
                {},
            ).get(
                "name",
                "",
            )
        )

        if castle_name not in AtlasCastleFootprintRegularizer.FORCE_ANGULAR_CASTLES:
            return prepared

        if AtlasCastleFootprintRegularizer._has_explicit_round_shape(prepared):
            return prepared

        regularized_geometry = (
            AtlasCastleFootprintRegularizer._build_oriented_rectangle(
                prepared.get(
                    "geometry",
                    [],
                )
            )
        )

        if regularized_geometry is None:
            return prepared

        prepared["geometry"] = regularized_geometry

        prepared["tags"]["atlas:footprint_regularized"] = "yes"

        prepared["tags"]["atlas:footprint_profile"] = "angular_tower"

        prepared["tags"]["atlas:source_point_count"] = str(
            len(
                raw_building.get(
                    "geometry",
                    [],
                )
            )
        )

        prepared["tags"]["atlas:regularized_point_count"] = str(
            len(regularized_geometry)
        )

        return prepared

    @staticmethod
    def _find_containing_castle(
        raw_building,
        castles,
    ):
        geometry = raw_building.get(
            "geometry",
            [],
        )

        building_polygon = AtlasCastleFootprintRegularizer._polygon_from_lat_lon(
            geometry
        )

        if building_polygon is None:
            return None

        representative_point = building_polygon.representative_point()

        for castle in castles:
            outer_geometries = castle.get(
                "outer_geometries",
                [],
            )

            if not outer_geometries:
                castle_geometry = castle.get(
                    "geometry",
                    [],
                )

                if castle_geometry:
                    outer_geometries = [castle_geometry]

            for outer_geometry in outer_geometries:
                castle_polygon = AtlasCastleFootprintRegularizer._polygon_from_lat_lon(
                    outer_geometry
                )

                if castle_polygon is None:
                    continue

                if castle_polygon.covers(representative_point):
                    return castle

        return None

    @staticmethod
    def _has_explicit_round_shape(
        raw_building,
    ):
        tags = raw_building.get(
            "tags",
            {},
        )

        possible_values = (
            tags.get("building:shape"),
            tags.get("shape"),
            tags.get("tower:shape"),
        )

        for value in possible_values:
            normalized = AtlasCastleFootprintRegularizer._normalize_text(value)

            if normalized in AtlasCastleFootprintRegularizer.ROUND_SHAPE_VALUES:
                return True

        return False

    @staticmethod
    def _build_oriented_rectangle(
        geometry,
    ):
        clean_geometry = AtlasCastleFootprintRegularizer._clean_lat_lon_ring(geometry)

        if len(clean_geometry) < 3:
            return None

        lat_0 = sum(point[0] for point in clean_geometry) / len(clean_geometry)

        lon_0 = sum(point[1] for point in clean_geometry) / len(clean_geometry)

        cos_latitude = math.cos(math.radians(lat_0))

        meters_per_degree_lat = 110_540.0

        meters_per_degree_lon = 111_320.0 * max(
            cos_latitude,
            1e-8,
        )

        local_points = []

        for lat, lon in clean_geometry:
            local_points.append(
                (
                    (float(lon) - lon_0) * meters_per_degree_lon,
                    (float(lat) - lat_0) * meters_per_degree_lat,
                )
            )

        polygon = Polygon(local_points)

        if polygon.is_empty:
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty or not polygon.is_valid or polygon.area <= 0.0:
            return None

        try:
            with warnings.catch_warnings():
                warnings.simplefilter(
                    "ignore",
                    RuntimeWarning,
                )

                rectangle = polygon.minimum_rotated_rectangle
        except Exception:
            return None

        if (
            rectangle is None
            or rectangle.is_empty
            or not rectangle.is_valid
            or rectangle.geom_type != "Polygon"
            or rectangle.area <= 0.0
        ):
            return None

        rectangle_coordinates = list(rectangle.exterior.coords)

        if not all(
            math.isfinite(float(x)) and math.isfinite(float(y))
            for x, y in rectangle_coordinates
        ):
            return None

        area_ratio = rectangle.area / polygon.area

        if (
            area_ratio < AtlasCastleFootprintRegularizer.MIN_RECTANGLE_AREA_RATIO
            or area_ratio > AtlasCastleFootprintRegularizer.MAX_RECTANGLE_AREA_RATIO
        ):
            return None

        rectangle_coordinates = list(rectangle.exterior.coords)

        if len(rectangle_coordinates) < 5:
            return None

        result = []

        for x, y in rectangle_coordinates[:-1]:
            lat = lat_0 + y / meters_per_degree_lat

            lon = lon_0 + x / meters_per_degree_lon

            result.append(
                (
                    lat,
                    lon,
                )
            )

        if len(result) != 4:
            return None

        result.append(result[0])

        return result

    @staticmethod
    def _clean_lat_lon_ring(
        geometry,
    ):
        clean = []

        for point in geometry:
            if point is None or len(point) < 2:
                continue

            current = (
                float(point[0]),
                float(point[1]),
            )

            if clean and current == clean[-1]:
                continue

            clean.append(current)

        if len(clean) >= 2 and clean[0] == clean[-1]:
            clean.pop()

        return clean

    @staticmethod
    def _polygon_from_lat_lon(
        geometry,
    ):
        clean_geometry = AtlasCastleFootprintRegularizer._clean_lat_lon_ring(geometry)

        if len(clean_geometry) < 3:
            return None

        coordinates = [
            (
                lon,
                lat,
            )
            for lat, lon in clean_geometry
        ]

        polygon = Polygon(coordinates)

        if polygon.is_empty:
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty or not polygon.is_valid:
            return None

        return polygon

    @staticmethod
    def _normalize_text(
        value,
    ):
        if value is None:
            return ""

        normalized = unicodedata.normalize(
            "NFKD",
            str(value),
        )

        normalized = "".join(
            character
            for character in normalized
            if not unicodedata.combining(character)
        )

        return normalized.strip().lower()
