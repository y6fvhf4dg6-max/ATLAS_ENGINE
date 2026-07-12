"""
ATLAS Coastline Water Builder v0.1

OSM natural=coastline way parçalarını bbox içinde birleştirir
ve kıyı çizgisinin sağ tarafında kalan alanı su polygonu olarak üretir.

OSM coastline yön kuralı:

    Çizgi yönünde ilerlerken kara solda, su sağdadır.

Bu sürüm yalnız geometri üretir.
Henüz STL mesh üretimi yapmaz.
"""

import math

from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import box
from shapely.ops import split


class AtlasCoastlineWaterBuilder:
    VERSION = "0.1"

    POINT_TOLERANCE = 1e-9
    PROBE_DISTANCE_RATIO = 0.002

    @staticmethod
    def build_water_polygons(
        coastlines,
        bbox,
        debug=True,
    ):
        coastlines = coastlines or []

        if not coastlines:
            return []

        merged_coordinates = (
            AtlasCoastlineWaterBuilder
            ._merge_directed_coastlines(
                coastlines
            )
        )

        if len(merged_coordinates) < 2:
            return []

        south, west, north, east = bbox

        bbox_polygon = box(
            west,
            south,
            east,
            north,
        )

        coastline_line = LineString(
            [
                (
                    lon,
                    lat,
                )
                for lat, lon
                in merged_coordinates
            ]
        )

        clipped = coastline_line.intersection(
            bbox_polygon
        )

        if clipped.is_empty:
            return []

        clipped_lines = (
            AtlasCoastlineWaterBuilder
            ._extract_line_strings(
                clipped
            )
        )

        water_polygons = []

        for clipped_line in clipped_lines:
            if clipped_line.length <= 0.0:
                continue

            polygons = list(
                split(
                    bbox_polygon,
                    clipped_line,
                ).geoms
            )

            polygons = [
                polygon
                for polygon in polygons
                if (
                    polygon.geom_type
                    == "Polygon"
                    and polygon.area > 0.0
                )
            ]

            if len(polygons) < 2:
                continue

            water_polygon = (
                AtlasCoastlineWaterBuilder
                ._select_right_side_polygon(
                    coastline=clipped_line,
                    polygons=polygons,
                    bbox_polygon=bbox_polygon,
                )
            )

            if water_polygon is not None:
                water_polygons.append(
                    water_polygon
                )

        if debug:
            AtlasCoastlineWaterBuilder._print_report(
                coastline_count=len(coastlines),
                merged_point_count=(
                    len(merged_coordinates)
                ),
                clipped_line_count=(
                    len(clipped_lines)
                ),
                water_polygons=water_polygons,
            )

        return water_polygons

    @staticmethod
    def _merge_directed_coastlines(
        coastlines,
    ):
        line_coordinates = []

        for coastline in coastlines:
            geometry = list(
                coastline.get(
                    "geometry",
                    [],
                )
            )

            if len(geometry) >= 2:
                line_coordinates.append(
                    geometry
                )

        if not line_coordinates:
            return []

        chains = []

        for coordinates in line_coordinates:
            inserted = False

            for chain in chains:
                if AtlasCoastlineWaterBuilder._same_point(
                    chain[-1],
                    coordinates[0],
                ):
                    chain.extend(
                        coordinates[1:]
                    )
                    inserted = True
                    break

                if AtlasCoastlineWaterBuilder._same_point(
                    coordinates[-1],
                    chain[0],
                ):
                    chain[:0] = coordinates[:-1]
                    inserted = True
                    break

            if not inserted:
                chains.append(
                    list(coordinates)
                )

            AtlasCoastlineWaterBuilder._join_chains(
                chains
            )

        if not chains:
            return []

        return max(
            chains,
            key=len,
        )

    @staticmethod
    def _join_chains(
        chains,
    ):
        changed = True

        while changed:
            changed = False

            for first_index in range(
                len(chains)
            ):
                if changed:
                    break

                for second_index in range(
                    first_index + 1,
                    len(chains),
                ):
                    first = chains[first_index]
                    second = chains[second_index]

                    if AtlasCoastlineWaterBuilder._same_point(
                        first[-1],
                        second[0],
                    ):
                        first.extend(
                            second[1:]
                        )
                        chains.pop(
                            second_index
                        )
                        changed = True
                        break

                    if AtlasCoastlineWaterBuilder._same_point(
                        second[-1],
                        first[0],
                    ):
                        first[:0] = second[:-1]
                        chains.pop(
                            second_index
                        )
                        changed = True
                        break

    @staticmethod
    def _same_point(
        point_a,
        point_b,
    ):
        return (
            abs(
                point_a[0]
                - point_b[0]
            )
            <= AtlasCoastlineWaterBuilder.POINT_TOLERANCE
            and abs(
                point_a[1]
                - point_b[1]
            )
            <= AtlasCoastlineWaterBuilder.POINT_TOLERANCE
        )

    @staticmethod
    def _extract_line_strings(
        geometry,
    ):
        if geometry.geom_type == "LineString":
            return [geometry]

        if geometry.geom_type == "MultiLineString":
            return [
                line
                for line in geometry.geoms
                if line.length > 0.0
            ]

        if geometry.geom_type == "GeometryCollection":
            return [
                item
                for item in geometry.geoms
                if (
                    item.geom_type
                    == "LineString"
                    and item.length > 0.0
                )
            ]

        return []

    @staticmethod
    def _select_right_side_polygon(
        coastline,
        polygons,
        bbox_polygon,
    ):
        if coastline.length <= 0.0:
            return None

        start_distance = (
            coastline.length
            * 0.45
        )

        end_distance = (
            coastline.length
            * 0.55
        )

        start_point = coastline.interpolate(
            start_distance
        )

        end_point = coastline.interpolate(
            end_distance
        )

        delta_x = (
            end_point.x
            - start_point.x
        )

        delta_y = (
            end_point.y
            - start_point.y
        )

        tangent_length = math.hypot(
            delta_x,
            delta_y,
        )

        if tangent_length <= 0.0:
            return None

        midpoint = coastline.interpolate(
            coastline.length * 0.5
        )

        right_normal_x = (
            delta_y
            / tangent_length
        )

        right_normal_y = (
            -delta_x
            / tangent_length
        )

        min_x, min_y, max_x, max_y = (
            bbox_polygon.bounds
        )

        bbox_diagonal = math.hypot(
            max_x - min_x,
            max_y - min_y,
        )

        base_probe_distance = max(
            bbox_diagonal
            * AtlasCoastlineWaterBuilder
            .PROBE_DISTANCE_RATIO,
            1e-8,
        )

        for multiplier in (
            1.0,
            2.0,
            4.0,
            8.0,
        ):
            probe_distance = (
                base_probe_distance
                * multiplier
            )

            right_probe = Point(
                midpoint.x
                + right_normal_x
                * probe_distance,
                midpoint.y
                + right_normal_y
                * probe_distance,
            )

            for polygon in polygons:
                if polygon.covers(
                    right_probe
                ):
                    return polygon

        return None

    @staticmethod
    def _print_report(
        coastline_count,
        merged_point_count,
        clipped_line_count,
        water_polygons,
    ):
        print("")
        print("=" * 70)
        print(
            "ATLAS COASTLINE WATER BUILDER "
            f"v{AtlasCoastlineWaterBuilder.VERSION}"
        )
        print("=" * 70)
        print(
            f"Input coastline records : "
            f"{coastline_count}"
        )
        print(
            f"Merged coastline points : "
            f"{merged_point_count}"
        )
        print(
            f"Clipped coastline lines : "
            f"{clipped_line_count}"
        )
        print(
            f"Water polygons          : "
            f"{len(water_polygons)}"
        )

        for index, polygon in enumerate(
            water_polygons,
            start=1,
        ):
            centroid = polygon.centroid

            print(
                f"Water polygon {index} area : "
                f"{polygon.area:.12f}"
            )
            print(
                f"Water polygon {index} center: "
                f"{centroid.x:.9f}, "
                f"{centroid.y:.9f}"
            )

        print("=" * 70)
        print("")
