"""
ATLAS Ancient Theatre Geometry Profiler v0.1

Antik tiyatro footprint'inden kimlikten bağımsız yerel eksen ve temel
mimari bölge oranlarını çıkarır.

Bu modül mesh üretmez.
"""

from math import atan2
from math import degrees
from math import hypot

from pyproj import Transformer
from shapely.geometry import Polygon


class AtlasAncientTheatreGeometryProfiler:
    PARALLEL_TOLERANCE_DEGREES = 3.0
    MIN_STAGE_EDGE_LENGTH_M = 5.0

    DEFAULT_ORCHESTRA_DEPTH_RATIO = 0.22
    DEFAULT_STAGE_DEPTH_RATIO = 0.16
    DEFAULT_CAVEA_INNER_DEPTH_RATIO = 0.26

    @staticmethod
    def profile(raw_building):
        geometry = raw_building.get(
            "geometry",
            [],
        )

        if len(geometry) < 4:
            return {
                "valid": False,
                "reason": "insufficient_geometry",
            }

        polygon = (
            AtlasAncientTheatreGeometryProfiler
            ._to_metric_polygon(geometry)
        )

        if polygon is None or polygon.is_empty:
            return {
                "valid": False,
                "reason": "invalid_polygon",
            }

        boundary = list(
            polygon.exterior.coords
        )

        edges = (
            AtlasAncientTheatreGeometryProfiler
            ._build_edges(boundary)
        )

        if not edges:
            return {
                "valid": False,
                "reason": "no_boundary_edges",
            }

        anchor = max(
            edges,
            key=lambda item: item["length_m"],
        )

        stage_edges = [
            edge
            for edge in edges
            if (
                AtlasAncientTheatreGeometryProfiler
                ._parallel_difference(
                    edge["angle_degrees"],
                    anchor["angle_degrees"],
                )
                <= AtlasAncientTheatreGeometryProfiler
                .PARALLEL_TOLERANCE_DEGREES
            )
            and (
                edge["length_m"]
                >= AtlasAncientTheatreGeometryProfiler
                .MIN_STAGE_EDGE_LENGTH_M
            )
        ]

        if not stage_edges:
            return {
                "valid": False,
                "reason": "stage_front_not_found",
            }

        stage_length_m = sum(
            edge["length_m"]
            for edge in stage_edges
        )

        stage_mid_x = sum(
            edge["midpoint"][0]
            * edge["length_m"]
            for edge in stage_edges
        ) / stage_length_m

        stage_mid_y = sum(
            edge["midpoint"][1]
            * edge["length_m"]
            for edge in stage_edges
        ) / stage_length_m

        stage_axis = (
            anchor["dx"] / anchor["length_m"],
            anchor["dy"] / anchor["length_m"],
        )

        normal_a = (
            -stage_axis[1],
            stage_axis[0],
        )

        normal_b = (
            stage_axis[1],
            -stage_axis[0],
        )

        centroid_vector = (
            polygon.centroid.x - stage_mid_x,
            polygon.centroid.y - stage_mid_y,
        )

        if (
            centroid_vector[0] * normal_a[0]
            + centroid_vector[1] * normal_a[1]
        ) >= 0.0:
            inward_normal = normal_a
        else:
            inward_normal = normal_b

        local_points = []

        for x, y in boundary[:-1]:
            dx = x - stage_mid_x
            dy = y - stage_mid_y

            local_x = (
                dx * stage_axis[0]
                + dy * stage_axis[1]
            )

            local_y = (
                dx * inward_normal[0]
                + dy * inward_normal[1]
            )

            local_points.append(
                (local_x, local_y)
            )

        min_x = min(
            point[0]
            for point in local_points
        )

        max_x = max(
            point[0]
            for point in local_points
        )

        min_y = min(
            point[1]
            for point in local_points
        )

        max_y = max(
            point[1]
            for point in local_points
        )

        width_m = max_x - min_x
        usable_depth_m = max_y

        orchestra_depth_m = (
            usable_depth_m
            * AtlasAncientTheatreGeometryProfiler
            .DEFAULT_ORCHESTRA_DEPTH_RATIO
        )

        stage_depth_m = (
            usable_depth_m
            * AtlasAncientTheatreGeometryProfiler
            .DEFAULT_STAGE_DEPTH_RATIO
        )

        cavea_inner_depth_m = (
            usable_depth_m
            * AtlasAncientTheatreGeometryProfiler
            .DEFAULT_CAVEA_INNER_DEPTH_RATIO
        )

        return {
            "valid": True,
            "reason": None,
            "polygon_area_m2": polygon.area,
            "polygon_perimeter_m": polygon.length,
            "boundary_point_count": len(boundary) - 1,
            "stage_edge_indices": tuple(
                edge["index"]
                for edge in stage_edges
            ),
            "stage_front_length_m": stage_length_m,
            "stage_front_midpoint_m": (
                stage_mid_x,
                stage_mid_y,
            ),
            "stage_axis": stage_axis,
            "inward_normal": inward_normal,
            "local_min_x_m": min_x,
            "local_max_x_m": max_x,
            "local_min_y_m": min_y,
            "local_max_y_m": max_y,
            "width_m": width_m,
            "usable_depth_m": usable_depth_m,
            "orchestra_depth_m": orchestra_depth_m,
            "stage_depth_m": stage_depth_m,
            "cavea_inner_depth_m": cavea_inner_depth_m,
        }

    @staticmethod
    def _to_metric_polygon(geometry):
        average_lat = sum(
            point[0]
            for point in geometry
        ) / len(geometry)

        average_lon = sum(
            point[1]
            for point in geometry
        ) / len(geometry)

        zone = int(
            (average_lon + 180.0) / 6.0
        ) + 1

        epsg = (
            32600 + zone
            if average_lat >= 0.0
            else 32700 + zone
        )

        transformer = Transformer.from_crs(
            "EPSG:4326",
            f"EPSG:{epsg}",
            always_xy=True,
        )

        points_m = [
            transformer.transform(
                lon,
                lat,
            )
            for lat, lon in geometry
        ]

        polygon = Polygon(points_m)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.area <= 0.0
        ):
            return None

        return polygon

    @staticmethod
    def _build_edges(boundary):
        edges = []

        for index in range(
            len(boundary) - 1
        ):
            x1, y1 = boundary[index]
            x2, y2 = boundary[index + 1]

            dx = x2 - x1
            dy = y2 - y1
            length_m = hypot(dx, dy)

            if length_m <= 0.0:
                continue

            edges.append(
                {
                    "index": index,
                    "dx": dx,
                    "dy": dy,
                    "length_m": length_m,
                    "angle_degrees": degrees(
                        atan2(dy, dx)
                    ),
                    "midpoint": (
                        (x1 + x2) * 0.5,
                        (y1 + y2) * 0.5,
                    ),
                }
            )

        return edges

    @staticmethod
    def _parallel_difference(
        angle_a,
        angle_b,
    ):
        difference = (
            abs(angle_a - angle_b)
            % 180.0
        )

        return min(
            difference,
            180.0 - difference,
        )
