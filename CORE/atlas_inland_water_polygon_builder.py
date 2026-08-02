"""
ATLAS Inland Water Polygon Builder v0.1

Kapalı OSM iç su geometrilerini geçerli ve bbox ile kırpılmış
Shapely Polygon nesnelerine dönüştürür.
"""

from shapely.geometry import Polygon
from shapely.geometry import box
from shapely.ops import unary_union


class AtlasInlandWaterPolygonBuilder:
    VERSION = "0.1"

    @staticmethod
    def build_polygons(
        waters,
        bbox,
        debug=True,
    ):
        waters = waters or []

        south, west, north, east = bbox
        bbox_polygon = box(
            west,
            south,
            east,
            north,
        )

        polygons = []
        skipped = 0

        for water in waters:
            geometry = list(
                water.get(
                    "geometry",
                    (),
                )
            )

            if len(geometry) < 3:
                skipped += 1
                continue

            tags = dict(
                water.get(
                    "tags",
                    {},
                )
            )

            if not AtlasInlandWaterPolygonBuilder._is_surface_water(
                tags
            ):
                skipped += 1
                continue

            polygon = Polygon(
                [
                    (
                        lon,
                        lat,
                    )
                    for lat, lon in geometry
                ]
            )

            if not polygon.is_valid:
                polygon = polygon.buffer(0)

            if (
                polygon.is_empty
                or not polygon.is_valid
                or polygon.geom_type != "Polygon"
                or polygon.area <= 0.0
            ):
                skipped += 1
                continue

            clipped = polygon.intersection(
                bbox_polygon
            )

            if clipped.is_empty:
                skipped += 1
                continue

            if clipped.geom_type == "Polygon":
                if clipped.area > 0.0:
                    polygons.append(clipped)
                else:
                    skipped += 1
                continue

            if clipped.geom_type == "MultiPolygon":
                accepted = [
                    item
                    for item in clipped.geoms
                    if item.area > 0.0
                ]
                polygons.extend(accepted)
                if not accepted:
                    skipped += 1
                continue

            skipped += 1

        if debug:
            print("")
            print("=" * 70)
            print(
                "ATLAS INLAND WATER POLYGON BUILDER "
                f"v{AtlasInlandWaterPolygonBuilder.VERSION}"
            )
            print("=" * 70)
            print(f"Input waters        : {len(waters)}")
            print(f"Accepted polygons   : {len(polygons)}")
            print(f"Skipped geometries  : {skipped}")
            print("=" * 70)
            print("")

        polygons = (
            AtlasInlandWaterPolygonBuilder
            ._merge_overlapping_polygons(
                polygons
            )
        )

        return polygons

    @staticmethod
    def _merge_overlapping_polygons(
        polygons,
    ):
        if not polygons:
            return []

        merged = unary_union(
            polygons
        )

        if merged.is_empty:
            return []

        if merged.geom_type == "Polygon":
            return [merged]

        if merged.geom_type == "MultiPolygon":
            return [
                polygon
                for polygon in merged.geoms
                if (
                    not polygon.is_empty
                    and polygon.is_valid
                    and polygon.area > 0.0
                )
            ]

        if merged.geom_type == "GeometryCollection":
            return [
                polygon
                for polygon in merged.geoms
                if (
                    polygon.geom_type == "Polygon"
                    and not polygon.is_empty
                    and polygon.is_valid
                    and polygon.area > 0.0
                )
            ]

        return []

    @staticmethod
    def _is_surface_water(tags):
        if tags.get("natural") == "water":
            return True

        if tags.get("water") in {
            "lake",
            "pond",
            "reservoir",
            "river",
            "canal",
            "basin",
            "lagoon",
        }:
            return True

        if tags.get("waterway") == "riverbank":
            return True

        if tags.get("landuse") == "reservoir":
            return True

        return False
