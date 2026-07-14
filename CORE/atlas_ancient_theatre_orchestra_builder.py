"""
ATLAS Ancient Theatre Orchestra Builder v0.1

Antik tiyatro profilinden açık orchestra tabanını üretir.

Orchestra:
- sahne binasının iç tarafında konumlanır,
- yarım disk biçimindedir,
- terrain yüzeyine hafifçe gömülür,
- kapalı ve basılabilir bir slab olarak üretilir.
"""

from math import cos
from math import pi
from math import sin

from pyproj import Transformer

from CORE.atlas_ancient_theatre_geometry_profiler import (
    AtlasAncientTheatreGeometryProfiler,
)
from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasAncientTheatreOrchestraBuilder:
    ARC_SEGMENTS = 32

    EMBED_DEPTH_MM = 0.12
    VISIBLE_HEIGHT_MM = 0.18

    @staticmethod
    def build(
        raw_building,
        coordinate_engine,
        terrain_mesh,
        diagnostics=None,
    ):
        profile = (
            AtlasAncientTheatreGeometryProfiler
            .profile(raw_building)
        )

        if not profile.get("valid"):
            return (
                AtlasAncientTheatreOrchestraBuilder
                ._reject(
                    diagnostics,
                    profile.get(
                        "reason",
                        "invalid_theatre_geometry",
                    ),
                )
            )

        metric_points = (
            AtlasAncientTheatreOrchestraBuilder
            ._build_metric_semidisk(profile)
        )

        latlon_points = (
            AtlasAncientTheatreOrchestraBuilder
            ._metric_to_latlon(
                metric_points=metric_points,
                raw_building=raw_building,
            )
        )

        scaled_points = (
            coordinate_engine.geometry_to_stl_mm(
                latlon_points
            )
        )

        flat_triangles = (
            AtlasPolygonTriangulator.triangulate(
                scaled_points
            )
        )

        if not flat_triangles:
            return (
                AtlasAncientTheatreOrchestraBuilder
                ._reject(
                    diagnostics,
                    "orchestra_triangulation_failed",
                )
            )

        terrain_values = [
            AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=point[0],
                y=point[1],
            )
            for point in scaled_points
        ]

        if not terrain_values:
            return (
                AtlasAncientTheatreOrchestraBuilder
                ._reject(
                    diagnostics,
                    "orchestra_foundation_sampling_failed",
                )
            )

        foundation_z = min(terrain_values)

        bottom_z = (
            foundation_z
            - AtlasAncientTheatreOrchestraBuilder
            .EMBED_DEPTH_MM
        )

        top_z = (
            foundation_z
            + AtlasAncientTheatreOrchestraBuilder
            .VISIBLE_HEIGHT_MM
        )

        bottom_points = [
            (x, y, bottom_z)
            for x, y in scaled_points
        ]

        top_points = [
            (x, y, top_z)
            for x, y in scaled_points
        ]

        triangles = []

        for triangle in flat_triangles:
            point_a, point_b, point_c = triangle

            triangles.append(
                (
                    (
                        point_c[0],
                        point_c[1],
                        bottom_z,
                    ),
                    (
                        point_b[0],
                        point_b[1],
                        bottom_z,
                    ),
                    (
                        point_a[0],
                        point_a[1],
                        bottom_z,
                    ),
                )
            )

            triangles.append(
                (
                    (
                        point_a[0],
                        point_a[1],
                        top_z,
                    ),
                    (
                        point_b[0],
                        point_b[1],
                        top_z,
                    ),
                    (
                        point_c[0],
                        point_c[1],
                        top_z,
                    ),
                )
            )

        wall_quads = []
        point_count = len(scaled_points)

        for index in range(point_count):
            next_index = (
                index + 1
            ) % point_count

            bottom_1 = bottom_points[index]
            bottom_2 = bottom_points[next_index]
            top_1 = top_points[index]
            top_2 = top_points[next_index]

            wall_quads.append(
                (
                    bottom_1,
                    bottom_2,
                    top_2,
                    top_1,
                )
            )

            triangles.append(
                (
                    bottom_1,
                    bottom_2,
                    top_2,
                )
            )

            triangles.append(
                (
                    bottom_1,
                    top_2,
                    top_1,
                )
            )

        mesh = {
            "type": "ancient_theatre_orchestra",
            "ancient_theatre_component": "orchestra",
            "source_id": raw_building.get("id"),
            "name": raw_building.get(
                "tags",
                {},
            ).get("name"),
            "bottom": bottom_points,
            "top": top_points,
            "walls": wall_quads,
            "triangles": triangles,
            "foundation_z": foundation_z,
            "bottom_z": bottom_z,
            "top_z": top_z,
            "placement_mode": "foundation_first",
            "ancient_theatre_profile": profile,
        }

        return mesh

    @staticmethod
    def _build_metric_semidisk(profile):
        stage_mid_x, stage_mid_y = profile[
            "stage_front_midpoint_m"
        ]

        axis_x, axis_y = profile["stage_axis"]

        inward_x, inward_y = profile[
            "inward_normal"
        ]

        stage_depth_m = profile[
            "stage_depth_m"
        ]

        radius_m = min(
            profile["orchestra_depth_m"],
            profile["width_m"] * 0.30,
        )

        center_x = (
            stage_mid_x
            + inward_x
            * (
                stage_depth_m
                + radius_m * 0.15
            )
        )

        center_y = (
            stage_mid_y
            + inward_y
            * (
                stage_depth_m
                + radius_m * 0.15
            )
        )

        points = []

        for index in range(
            AtlasAncientTheatreOrchestraBuilder
            .ARC_SEGMENTS
            + 1
        ):
            angle = (
                pi
                - (
                    pi
                    * index
                    / AtlasAncientTheatreOrchestraBuilder
                    .ARC_SEGMENTS
                )
            )

            lateral = cos(angle) * radius_m
            inward = sin(angle) * radius_m

            points.append(
                (
                    center_x
                    + axis_x * lateral
                    + inward_x * inward,
                    center_y
                    + axis_y * lateral
                    + inward_y * inward,
                )
            )

        return points

    @staticmethod
    def _metric_to_latlon(
        metric_points,
        raw_building,
    ):
        geometry = raw_building.get(
            "geometry",
            [],
        )

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
            f"EPSG:{epsg}",
            "EPSG:4326",
            always_xy=True,
        )

        points = []

        for x, y in metric_points:
            lon, lat = transformer.transform(
                x,
                y,
            )

            points.append(
                (lat, lon)
            )

        return points

    @staticmethod
    def _reject(
        diagnostics,
        reason,
    ):
        if diagnostics is not None:
            diagnostics["reason"] = reason

        return None
