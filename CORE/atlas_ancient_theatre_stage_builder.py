"""
ATLAS Ancient Theatre Stage Builder v0.1

Antik tiyatro footprint profilinden sahne binasının kapalı prizma
mesh'ini üretir.

Bu ilk sürüm yalnızca stage building üretir.
Cavea, orchestra ve galeri bu modülde henüz yoktur.
"""

from dataclasses import dataclass

from pyproj import Transformer

from CORE.atlas_ancient_theatre_geometry_profiler import (
    AtlasAncientTheatreGeometryProfiler,
)
from CORE.atlas_foundation_mesh_extruder import (
    AtlasFoundationMeshExtruder,
)
from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


@dataclass
class _TheatreStageBuilding:
    geometry: list
    estimated_height: float
    area_m2: float
    min_height: float = None
    min_level: int = None
    is_castle_building: bool = False
    is_building_part: bool = False
    tags: dict = None


class AtlasAncientTheatreStageBuilder:
    DEFAULT_STAGE_HEIGHT_M = 24.0

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
            if diagnostics is not None:
                diagnostics["reason"] = profile.get(
                    "reason",
                    "invalid_theatre_geometry",
                )

            return None

        stage_geometry = (
            AtlasAncientTheatreStageBuilder
            ._build_stage_geometry(
                raw_building=raw_building,
                profile=profile,
            )
        )

        if not stage_geometry:
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "stage_geometry_failed"
                )

            return None

        stage_building = _TheatreStageBuilding(
            geometry=stage_geometry,
            estimated_height=(
                AtlasAncientTheatreStageBuilder
                .DEFAULT_STAGE_HEIGHT_M
            ),
            area_m2=(
                profile["stage_front_length_m"]
                * profile["stage_depth_m"]
            ),
            tags={
                "atlas:ancient_theatre_component": (
                    "stage_building"
                ),
            },
        )

        scaled_points = (
            coordinate_engine.geometry_to_stl_mm(
                stage_geometry
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
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "stage_foundation_sampling_failed"
                )

            return None

        mesh = (
            AtlasAncientTheatreStageBuilder
            ._build_local_terrain_mesh(
                scaled_points=scaled_points,
                terrain_values=terrain_values,
                stage_building=stage_building,
                coordinate_engine=coordinate_engine,
                diagnostics=diagnostics,
            )
        )

        if not mesh:
            return None

        mesh["type"] = (
            "ancient_theatre_stage_building"
        )

        mesh["ancient_theatre_component"] = (
            "stage_building"
        )

        mesh["ancient_theatre_profile"] = profile
        mesh["source_id"] = raw_building.get("id")
        mesh["name"] = raw_building.get(
            "tags",
            {},
        ).get("name")

        walls = mesh.get(
            "walls",
            [],
        )

        if walls:
            mesh["stage_front_wall_quad"] = (
                walls[2]
            )
            mesh["stage_side_wall_quads"] = [
                walls[1],
                walls[3],
            ]
            mesh["stage_back_wall_quad"] = (
                walls[0]
            )

        return mesh

    @staticmethod
    def _build_local_terrain_mesh(
        scaled_points,
        terrain_values,
        stage_building,
        coordinate_engine,
        diagnostics=None,
    ):
        scaled_points = list(scaled_points)
        terrain_values = list(terrain_values)

        if (
            len(scaled_points) >= 2
            and scaled_points[0] == scaled_points[-1]
        ):
            scaled_points = scaled_points[:-1]
            terrain_values = terrain_values[:-1]

        if (
            not scaled_points
            or len(scaled_points) < 3
            or len(scaled_points) != len(terrain_values)
        ):
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "invalid_stage_local_terrain_input"
                )

            return None

        flat_triangles = (
            AtlasPolygonTriangulator.triangulate(
                scaled_points
            )
        )

        if not flat_triangles:
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "stage_triangulation_failed"
                )

            return None

        embed_depth_mm = 0.30

        bottom_points = [
            (
                point[0],
                point[1],
                terrain_z - embed_depth_mm,
            )
            for point, terrain_z in zip(
                scaled_points,
                terrain_values,
            )
        ]

        stage_height_mm = (
            coordinate_engine.height_to_stl_mm(
                stage_building.estimated_height
            )
        )

        top_z = (
            max(terrain_values)
            + stage_height_mm
        )

        top_points = [
            (
                point[0],
                point[1],
                top_z,
            )
            for point in scaled_points
        ]

        point_index = {
            (
                round(point[0], 9),
                round(point[1], 9),
            ): index
            for index, point in enumerate(
                scaled_points
            )
        }

        triangles = []

        for triangle in flat_triangles:
            indices = [
                point_index[
                    (
                        round(point[0], 9),
                        round(point[1], 9),
                    )
                ]
                for point in triangle
            ]

            index_a, index_b, index_c = indices

            triangles.append(
                (
                    bottom_points[index_c],
                    bottom_points[index_b],
                    bottom_points[index_a],
                )
            )

            triangles.append(
                (
                    top_points[index_a],
                    top_points[index_b],
                    top_points[index_c],
                )
            )

        walls = []
        point_count = len(scaled_points)

        for index in range(point_count):
            next_index = (
                index + 1
            ) % point_count

            bottom_1 = bottom_points[index]
            bottom_2 = bottom_points[next_index]
            top_1 = top_points[index]
            top_2 = top_points[next_index]

            walls.append(
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

        bottom_z_min = min(
            point[2]
            for point in bottom_points
        )

        bottom_z_max = max(
            point[2]
            for point in bottom_points
        )

        return {
            "type": "building",
            "bottom": bottom_points,
            "top": top_points,
            "walls": walls,
            "triangles": triangles,
            "foundation_z": bottom_z_min,
            "bottom_z": bottom_z_min,
            "bottom_z_min": bottom_z_min,
            "bottom_z_max": bottom_z_max,
            "top_z": top_z,
            "placement_mode": (
                "foundation_first_local_terrain"
            ),
        }

    @staticmethod
    def _build_stage_geometry(
        raw_building,
        profile,
    ):
        midpoint_x, midpoint_y = profile[
            "stage_front_midpoint_m"
        ]

        axis_x, axis_y = profile["stage_axis"]
        inward_x, inward_y = profile[
            "inward_normal"
        ]

        half_width = (
            profile["stage_front_length_m"]
            * 0.5
        )

        depth = profile["stage_depth_m"]

        metric_points = [
            (
                midpoint_x - axis_x * half_width,
                midpoint_y - axis_y * half_width,
            ),
            (
                midpoint_x + axis_x * half_width,
                midpoint_y + axis_y * half_width,
            ),
            (
                midpoint_x
                + axis_x * half_width
                + inward_x * depth,
                midpoint_y
                + axis_y * half_width
                + inward_y * depth,
            ),
            (
                midpoint_x
                - axis_x * half_width
                + inward_x * depth,
                midpoint_y
                - axis_y * half_width
                + inward_y * depth,
            ),
        ]

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

        latlon_points = []

        for x, y in metric_points:
            lon, lat = transformer.transform(
                x,
                y,
            )

            latlon_points.append(
                (lat, lon)
            )

        latlon_points.append(
            latlon_points[0]
        )

        return latlon_points
