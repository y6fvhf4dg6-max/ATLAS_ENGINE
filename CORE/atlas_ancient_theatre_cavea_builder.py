from math import cos
from math import pi
from math import sin
from statistics import median

from pyproj import Transformer

from CORE.atlas_ancient_theatre_cavea_profile import (
    AtlasAncientTheatreCaveaProfile,
)
from CORE.atlas_ancient_theatre_geometry_profiler import (
    AtlasAncientTheatreGeometryProfiler,
)
from CORE.atlas_coordinate_engine import (
    AtlasCoordinateEngine,
)
from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasAncientTheatreCaveaBuilder:
    ARC_SEGMENTS = 32
    RADIAL_SEGMENTS = 8

    DEFAULT_CAVEA_RISE_RATIO = 0.16

    EMBED_DEPTH_MM = 0.30
    MIN_TOP_CLEARANCE_MM = 0.20
    VISIBLE_HEIGHT_MM = 0.60

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

        metric_bowl_grid = (
            AtlasAncientTheatreCaveaBuilder
            ._build_metric_bowl_grid(
                profile
            )
        )

        if not metric_bowl_grid:
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "cavea_bowl_geometry_failed"
                )

            return None

        stl_bowl_grid = (
            AtlasAncientTheatreCaveaBuilder
            ._metric_bowl_grid_to_stl(
                bowl_grid=metric_bowl_grid,
                raw_building=raw_building,
                coordinate_engine=coordinate_engine,
            )
        )

        if not stl_bowl_grid:
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "cavea_bowl_conversion_failed"
                )

            return None

        placed_bowl_grid = (
            AtlasAncientTheatreCaveaBuilder
            ._place_bowl_grid_on_terrain(
                stl_bowl_grid=stl_bowl_grid,
                terrain_mesh=terrain_mesh,
            )
        )

        if not placed_bowl_grid:
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "cavea_bowl_placement_failed"
                )

            return None

        closed_bowl = (
            AtlasAncientTheatreCaveaBuilder
            ._build_closed_bowl_triangles(
                placed_bowl_grid
            )
        )

        if not closed_bowl:
            if diagnostics is not None:
                diagnostics["reason"] = (
                    "cavea_closed_body_failed"
                )

            return None

        wall_quads = closed_bowl[
            "wall_quads"
        ]

        boundary_bottom = [
            quad[0]
            for quad in wall_quads
        ]

        boundary_top = [
            quad[3]
            for quad in wall_quads
        ]

        mesh = {
            "type": "ancient_theatre_cavea",
            "ancient_theatre_component": (
                "cavea"
            ),
            "source_id": raw_building.get(
                "id"
            ),
            "name": raw_building.get(
                "tags",
                {},
            ).get("name"),
            "bottom": boundary_bottom,
            "top": boundary_top,
            "walls": wall_quads,
            "outer_wall_quads": (
                closed_bowl[
                    "outer_wall_quads"
                ]
            ),
            "triangles": closed_bowl[
                "triangles"
            ],
            "foundation_z": (
                placed_bowl_grid[
                    "bottom_z_min"
                ]
            ),
            "bottom_z": (
                placed_bowl_grid[
                    "bottom_z_min"
                ]
            ),
            "top_z": (
                placed_bowl_grid[
                    "top_z_max"
                ]
            ),
            "bottom_z_min": (
                placed_bowl_grid[
                    "bottom_z_min"
                ]
            ),
            "bottom_z_max": (
                placed_bowl_grid[
                    "bottom_z_max"
                ]
            ),
            "top_z_min": (
                placed_bowl_grid[
                    "top_z_min"
                ]
            ),
            "top_z_max": (
                placed_bowl_grid[
                    "top_z_max"
                ]
            ),
            "bowl_base_z": (
                placed_bowl_grid[
                    "bowl_base_z"
                ]
            ),
            "base_lift_mm": (
                placed_bowl_grid[
                    "base_lift_mm"
                ]
            ),
            "placement_mode": (
                "local_terrain_inverted_bowl"
            ),
            "ancient_theatre_profile": (
                profile
            ),
            "metric_bowl_grid": (
                metric_bowl_grid
            ),
            "stl_bowl_grid": (
                stl_bowl_grid
            ),
            "placed_bowl_grid": (
                placed_bowl_grid
            ),
            "top_triangle_count": len(
                closed_bowl[
                    "top_triangles"
                ]
            ),
            "bottom_triangle_count": len(
                closed_bowl[
                    "bottom_triangles"
                ]
            ),
            "wall_triangle_count": len(
                closed_bowl[
                    "wall_triangles"
                ]
            ),
        }

        if diagnostics is not None:
            diagnostics.update(
                {
                    "reason": None,
                    "placement_mode": mesh[
                        "placement_mode"
                    ],
                    "triangle_count": len(
                        mesh["triangles"]
                    ),
                    "bowl_base_z": mesh[
                        "bowl_base_z"
                    ],
                    "top_z_min": mesh[
                        "top_z_min"
                    ],
                    "top_z_max": mesh[
                        "top_z_max"
                    ],
                }
            )

        return mesh

    @staticmethod
    def _build_metric_bowl_grid(
        profile,
        radial_segments=None,
        cavea_rise_m=None,
    ):
        if radial_segments is None:
            radial_segments = (
                AtlasAncientTheatreCaveaBuilder
                .RADIAL_SEGMENTS
            )

        radial_segments = int(
            radial_segments
        )

        if radial_segments < 1:
            raise ValueError(
                "radial_segments must be at least one"
            )

        stage_mid_x, stage_mid_y = profile[
            "stage_front_midpoint_m"
        ]

        axis_x, axis_y = profile[
            "stage_axis"
        ]

        inward_x, inward_y = profile[
            "inward_normal"
        ]

        stage_depth_m = profile[
            "stage_depth_m"
        ]

        orchestra_radius_m = min(
            profile["orchestra_depth_m"],
            profile["width_m"] * 0.30,
        )

        center_offset_m = (
            stage_depth_m
            + orchestra_radius_m * 0.15
        )

        center_x = (
            stage_mid_x
            + inward_x * center_offset_m
        )

        center_y = (
            stage_mid_y
            + inward_y * center_offset_m
        )

        inner_radius_m = (
            orchestra_radius_m
            + max(
                1.50,
                profile["width_m"] * 0.015,
            )
        )

        available_inward_radius_m = (
            profile["local_max_y_m"]
            - center_offset_m
        )

        available_lateral_radius_m = min(
            abs(profile["local_min_x_m"]),
            abs(profile["local_max_x_m"]),
        )

        outer_radius_m = min(
            available_inward_radius_m,
            available_lateral_radius_m,
            profile["width_m"] * 0.48,
        )

        if outer_radius_m <= inner_radius_m:
            return None

        if cavea_rise_m is None:
            cavea_rise_m = (
                profile["width_m"]
                * AtlasAncientTheatreCaveaBuilder
                .DEFAULT_CAVEA_RISE_RATIO
            )

        cavea_rise_m = max(
            0.0,
            float(cavea_rise_m),
        )

        rings = []

        for radial_index in range(
            radial_segments + 1
        ):
            radial_ratio = (
                radial_index
                / radial_segments
            )

            radius_m = (
                inner_radius_m
                + (
                    outer_radius_m
                    - inner_radius_m
                )
                * radial_ratio
            )

            terrace_start_index = max(
                1,
                radial_segments - 1,
            )

            height_radial_ratio = min(
                1.0,
                radial_index
                / terrace_start_index,
            )

            relative_height_m = (
                cavea_rise_m
                * AtlasAncientTheatreCaveaProfile
                .normalized_height(
                    radial_ratio=(
                        height_radial_ratio
                    ),
                )
            )

            ring = []

            for arc_index in range(
                AtlasAncientTheatreCaveaBuilder
                .ARC_SEGMENTS + 1
            ):
                angle = (
                    pi
                    - pi
                    * arc_index
                    / AtlasAncientTheatreCaveaBuilder
                    .ARC_SEGMENTS
                )

                lateral = (
                    cos(angle)
                    * radius_m
                )

                inward = (
                    sin(angle)
                    * radius_m
                )

                ring.append(
                    (
                        center_x
                        + axis_x * lateral
                        + inward_x * inward,
                        center_y
                        + axis_y * lateral
                        + inward_y * inward,
                        relative_height_m,
                    )
                )

            rings.append(ring)

        return {
            "rings": rings,
            "center_m": (
                center_x,
                center_y,
            ),
            "inner_radius_m": inner_radius_m,
            "outer_radius_m": outer_radius_m,
            "cavea_rise_m": cavea_rise_m,
            "radial_segments": radial_segments,
            "arc_segments": (
                AtlasAncientTheatreCaveaBuilder
                .ARC_SEGMENTS
            ),
        }

    @staticmethod
    def _metric_bowl_grid_to_stl(
        bowl_grid,
        raw_building,
        coordinate_engine,
    ):
        metric_rings = bowl_grid.get(
            "rings",
            [],
        )

        if not metric_rings:
            return None

        flat_metric_points = [
            (
                point[0],
                point[1],
            )
            for ring in metric_rings
            for point in ring
        ]

        latlon_points = (
            AtlasAncientTheatreCaveaBuilder
            ._metric_to_latlon(
                metric_points=flat_metric_points,
                raw_building=raw_building,
            )
        )

        scaled_xy = (
            coordinate_engine.geometry_to_stl_mm(
                latlon_points
            )
        )

        point_count_per_ring = len(
            metric_rings[0]
        )

        scaled_rings = []
        flat_index = 0

        for metric_ring in metric_rings:
            scaled_ring = []

            for metric_point in metric_ring:
                xy_point = scaled_xy[flat_index]

                relative_height_mm = (
                    coordinate_engine.height_to_stl_mm(
                        metric_point[2]
                    )
                )

                scaled_ring.append(
                    (
                        xy_point[0],
                        xy_point[1],
                        relative_height_mm,
                    )
                )

                flat_index += 1

            scaled_rings.append(
                scaled_ring
            )

        if any(
            len(ring) != point_count_per_ring
            for ring in scaled_rings
        ):
            return None

        return {
            **bowl_grid,
            "rings": scaled_rings,
            "coordinate_space": "stl_mm",
        }

    @staticmethod
    def _build_bowl_surface_triangles(
        stl_bowl_grid,
    ):
        rings = stl_bowl_grid.get(
            "rings",
            [],
        )

        if len(rings) < 2:
            return []

        point_count = len(rings[0])

        if point_count < 2:
            return []

        if any(
            len(ring) != point_count
            for ring in rings
        ):
            return []

        triangles = []

        for radial_index in range(
            len(rings) - 1
        ):
            inner_ring = rings[
                radial_index
            ]
            outer_ring = rings[
                radial_index + 1
            ]

            for arc_index in range(
                point_count - 1
            ):
                inner_1 = inner_ring[
                    arc_index
                ]
                inner_2 = inner_ring[
                    arc_index + 1
                ]
                outer_1 = outer_ring[
                    arc_index
                ]
                outer_2 = outer_ring[
                    arc_index + 1
                ]

                triangles.append(
                    (
                        inner_1,
                        outer_1,
                        outer_2,
                    )
                )

                triangles.append(
                    (
                        inner_1,
                        outer_2,
                        inner_2,
                    )
                )

        return triangles

    @staticmethod
    def _place_bowl_grid_on_terrain(
        stl_bowl_grid,
        terrain_mesh,
    ):
        relative_rings = stl_bowl_grid.get(
            "rings",
            [],
        )

        if not relative_rings:
            return None

        terrain_rings = []

        for relative_ring in relative_rings:
            terrain_ring = [
                (
                    AtlasFoundationSampler
                    .terrain_z_at_xy(
                        terrain_mesh=terrain_mesh,
                        x=point[0],
                        y=point[1],
                    )
                )
                for point in relative_ring
            ]

            terrain_rings.append(
                terrain_ring
            )

        inner_median_base_z = median(
            terrain_rings[0]
        )

        required_base_z = max(
            terrain_rings[radial_index][arc_index]
            + AtlasAncientTheatreCaveaBuilder
            .MIN_TOP_CLEARANCE_MM
            - point[2]
            for radial_index, ring in enumerate(
                relative_rings
            )
            for arc_index, point in enumerate(ring)
        )

        bowl_base_z = max(
            inner_median_base_z,
            required_base_z,
        )

        top_rings = []
        bottom_rings = []

        for radial_index, relative_ring in enumerate(
            relative_rings
        ):
            top_ring = []
            bottom_ring = []

            for arc_index, point in enumerate(
                relative_ring
            ):
                terrain_z = terrain_rings[
                    radial_index
                ][arc_index]

                bottom_ring.append(
                    (
                        point[0],
                        point[1],
                        terrain_z
                        - AtlasAncientTheatreCaveaBuilder
                        .EMBED_DEPTH_MM,
                    )
                )

                top_ring.append(
                    (
                        point[0],
                        point[1],
                        bowl_base_z
                        + point[2],
                    )
                )

            bottom_rings.append(
                bottom_ring
            )

            top_rings.append(
                top_ring
            )

        terrain_values = [
            terrain_z
            for ring in terrain_rings
            for terrain_z in ring
        ]

        top_values = [
            point[2]
            for ring in top_rings
            for point in ring
        ]

        bottom_values = [
            point[2]
            for ring in bottom_rings
            for point in ring
        ]

        return {
            **stl_bowl_grid,
            "relative_rings": relative_rings,
            "terrain_rings": terrain_rings,
            "bottom_rings": bottom_rings,
            "top_rings": top_rings,
            "bowl_base_z": bowl_base_z,
            "inner_median_base_z": (
                inner_median_base_z
            ),
            "required_base_z": required_base_z,
            "base_lift_mm": (
                bowl_base_z
                - inner_median_base_z
            ),
            "minimum_top_clearance_mm": (
                AtlasAncientTheatreCaveaBuilder
                .MIN_TOP_CLEARANCE_MM
            ),
            "terrain_z_min": min(
                terrain_values
            ),
            "terrain_z_max": max(
                terrain_values
            ),
            "bottom_z_min": min(
                bottom_values
            ),
            "bottom_z_max": max(
                bottom_values
            ),
            "top_z_min": min(
                top_values
            ),
            "top_z_max": max(
                top_values
            ),
            "placement_mode": (
                "local_terrain_inverted_bowl"
            ),
        }

    @staticmethod
    def _build_stepped_surface_triangles(
        placed_bowl_grid,
    ):
        top_rings = placed_bowl_grid.get(
            "top_rings",
            [],
        )

        if len(top_rings) < 2:
            return None

        point_count = len(top_rings[0])

        if point_count < 2:
            return None

        if any(
            len(ring) != point_count
            for ring in top_rings
        ):
            return None

        tread_triangles = []
        riser_triangles = []
        tread_quads = []
        riser_quads = []

        for radial_index in range(
            len(top_rings) - 1
        ):
            inner_ring = top_rings[
                radial_index
            ]

            outer_ring = top_rings[
                radial_index + 1
            ]

            tread_z = inner_ring[0][2]
            next_z = outer_ring[0][2]

            lower_outer_ring = [
                (
                    point[0],
                    point[1],
                    tread_z,
                )
                for point in outer_ring
            ]

            for arc_index in range(
                point_count - 1
            ):
                inner_1 = inner_ring[
                    arc_index
                ]
                inner_2 = inner_ring[
                    arc_index + 1
                ]

                outer_lower_1 = (
                    lower_outer_ring[
                        arc_index
                    ]
                )

                outer_lower_2 = (
                    lower_outer_ring[
                        arc_index + 1
                    ]
                )

                outer_upper_1 = outer_ring[
                    arc_index
                ]

                outer_upper_2 = outer_ring[
                    arc_index + 1
                ]

                tread_quads.append(
                    (
                        inner_1,
                        outer_lower_1,
                        outer_lower_2,
                        inner_2,
                    )
                )

                tread_triangles.append(
                    (
                        inner_1,
                        outer_lower_1,
                        outer_lower_2,
                    )
                )

                tread_triangles.append(
                    (
                        inner_1,
                        outer_lower_2,
                        inner_2,
                    )
                )

                if next_z > tread_z:
                    riser_quads.append(
                        (
                            outer_lower_1,
                            outer_upper_1,
                            outer_upper_2,
                            outer_lower_2,
                        )
                    )

                    riser_triangles.append(
                        (
                            outer_lower_1,
                            outer_upper_1,
                            outer_upper_2,
                        )
                    )

                    riser_triangles.append(
                        (
                            outer_lower_1,
                            outer_upper_2,
                            outer_lower_2,
                        )
                    )

        return {
            "tread_triangles": (
                tread_triangles
            ),
            "riser_triangles": (
                riser_triangles
            ),
            "tread_quads": tread_quads,
            "riser_quads": riser_quads,
            "triangles": (
                tread_triangles
                + riser_triangles
            ),
            "step_count": (
                len(top_rings) - 1
            ),
        }

    @staticmethod
    def _build_closed_bowl_triangles(
        placed_bowl_grid,
    ):
        top_rings = placed_bowl_grid.get(
            "top_rings",
            [],
        )

        bottom_rings = placed_bowl_grid.get(
            "bottom_rings",
            [],
        )

        if len(top_rings) < 2:
            return None

        if len(top_rings) != len(
            bottom_rings
        ):
            return None

        point_count = len(top_rings[0])

        if point_count < 2:
            return None

        if any(
            len(ring) != point_count
            for ring in top_rings
        ):
            return None

        if any(
            len(ring) != point_count
            for ring in bottom_rings
        ):
            return None

        bottom_grid = {
            "rings": bottom_rings,
        }

        stepped_surface = (
            AtlasAncientTheatreCaveaBuilder
            ._build_stepped_surface_triangles(
                placed_bowl_grid
            )
        )

        if not stepped_surface:
            return None

        top_triangles = stepped_surface[
            "triangles"
        ]

        bottom_surface = (
            AtlasAncientTheatreCaveaBuilder
            ._build_bowl_surface_triangles(
                bottom_grid
            )
        )

        bottom_triangles = [
            (
                triangle[2],
                triangle[1],
                triangle[0],
            )
            for triangle in bottom_surface
        ]

        wall_triangles = []
        wall_quads = []
        outer_wall_quads = []

        def append_wall_quad(
            bottom_1,
            bottom_2,
            top_2,
            top_1,
        ):
            wall_quads.append(
                (
                    bottom_1,
                    bottom_2,
                    top_2,
                    top_1,
                )
            )

            wall_triangles.append(
                (
                    bottom_1,
                    bottom_2,
                    top_2,
                )
            )

            wall_triangles.append(
                (
                    bottom_1,
                    top_2,
                    top_1,
                )
            )

        inner_top = top_rings[0]
        inner_bottom = bottom_rings[0]

        for arc_index in range(
            point_count - 1
        ):
            append_wall_quad(
                inner_bottom[
                    arc_index + 1
                ],
                inner_bottom[
                    arc_index
                ],
                inner_top[
                    arc_index
                ],
                inner_top[
                    arc_index + 1
                ],
            )

        outer_top = top_rings[-1]
        outer_bottom = bottom_rings[-1]

        for arc_index in range(
            point_count - 1
        ):
            outer_quad = (
                outer_bottom[
                    arc_index
                ],
                outer_bottom[
                    arc_index + 1
                ],
                outer_top[
                    arc_index + 1
                ],
                outer_top[
                    arc_index
                ],
            )

            outer_wall_quads.append(
                outer_quad
            )

            append_wall_quad(
                *outer_quad
            )

        radial_count = len(top_rings)

        def append_stepped_radial_wall(
            bottom_inner,
            bottom_outer,
            top_inner,
            top_outer,
            reverse=False,
        ):
            top_outer_lower = (
                top_outer[0],
                top_outer[1],
                top_inner[2],
            )

            is_flat_terrace_band = (
                abs(
                    top_outer[2]
                    - top_inner[2]
                )
                < 1e-9
            )

            if is_flat_terrace_band:
                if not reverse:
                    wall_triangles.extend(
                        [
                            (
                                bottom_inner,
                                bottom_outer,
                                top_outer,
                            ),
                            (
                                bottom_inner,
                                top_outer,
                                top_inner,
                            ),
                        ]
                    )
                else:
                    wall_triangles.extend(
                        [
                            (
                                bottom_outer,
                                bottom_inner,
                                top_inner,
                            ),
                            (
                                bottom_outer,
                                top_inner,
                                top_outer,
                            ),
                        ]
                    )
            elif not reverse:
                wall_triangles.extend(
                    [
                        (
                            bottom_inner,
                            bottom_outer,
                            top_outer,
                        ),
                        (
                            bottom_inner,
                            top_outer,
                            top_outer_lower,
                        ),
                        (
                            bottom_inner,
                            top_outer_lower,
                            top_inner,
                        ),
                    ]
                )
            else:
                wall_triangles.extend(
                    [
                        (
                            bottom_outer,
                            bottom_inner,
                            top_inner,
                        ),
                        (
                            bottom_outer,
                            top_inner,
                            top_outer_lower,
                        ),
                        (
                            bottom_outer,
                            top_outer_lower,
                            top_outer,
                        ),
                    ]
                )

            wall_quads.append(
                (
                    bottom_inner,
                    bottom_outer,
                    top_outer,
                    top_inner,
                )
            )

        for radial_index in range(
            radial_count - 1
        ):
            append_stepped_radial_wall(
                bottom_inner=bottom_rings[
                    radial_index
                ][0],
                bottom_outer=bottom_rings[
                    radial_index + 1
                ][0],
                top_inner=top_rings[
                    radial_index
                ][0],
                top_outer=top_rings[
                    radial_index + 1
                ][0],
                reverse=False,
            )

        last_arc_index = (
            point_count - 1
        )

        for radial_index in range(
            radial_count - 1
        ):
            append_stepped_radial_wall(
                bottom_inner=bottom_rings[
                    radial_index
                ][last_arc_index],
                bottom_outer=bottom_rings[
                    radial_index + 1
                ][last_arc_index],
                top_inner=top_rings[
                    radial_index
                ][last_arc_index],
                top_outer=top_rings[
                    radial_index + 1
                ][last_arc_index],
                reverse=True,
            )

        triangles = (
            top_triangles
            + bottom_triangles
            + wall_triangles
        )

        return {
            "top_triangles": top_triangles,
            "tread_triangles": stepped_surface[
                "tread_triangles"
            ],
            "riser_triangles": stepped_surface[
                "riser_triangles"
            ],
            "step_count": stepped_surface[
                "step_count"
            ],
            "bottom_triangles": (
                bottom_triangles
            ),
            "wall_triangles": wall_triangles,
            "wall_quads": wall_quads,
            "outer_wall_quads": (
                outer_wall_quads
            ),
            "triangles": triangles,
        }

    @staticmethod
    def _build_metric_semiring(profile):
        stage_mid_x, stage_mid_y = profile[
            "stage_front_midpoint_m"
        ]

        axis_x, axis_y = profile[
            "stage_axis"
        ]

        inward_x, inward_y = profile[
            "inward_normal"
        ]

        stage_depth_m = profile[
            "stage_depth_m"
        ]

        orchestra_radius_m = min(
            profile["orchestra_depth_m"],
            profile["width_m"] * 0.30,
        )

        center_offset_m = (
            stage_depth_m
            + orchestra_radius_m * 0.15
        )

        center_x = (
            stage_mid_x
            + inward_x * center_offset_m
        )

        center_y = (
            stage_mid_y
            + inward_y * center_offset_m
        )

        inner_radius_m = (
            orchestra_radius_m
            + max(
                1.50,
                profile["width_m"] * 0.015,
            )
        )

        available_inward_radius_m = (
            profile["local_max_y_m"]
            - center_offset_m
        )

        available_lateral_radius_m = min(
            abs(profile["local_min_x_m"]),
            abs(profile["local_max_x_m"]),
        )

        outer_radius_m = min(
            available_inward_radius_m,
            available_lateral_radius_m,
            profile["width_m"] * 0.48,
        )

        if outer_radius_m <= inner_radius_m:
            return None

        outer_arc = []

        for index in range(
            AtlasAncientTheatreCaveaBuilder
            .ARC_SEGMENTS + 1
        ):
            angle = (
                pi
                - pi
                * index
                / AtlasAncientTheatreCaveaBuilder
                .ARC_SEGMENTS
            )

            lateral = cos(angle) * outer_radius_m
            inward = sin(angle) * outer_radius_m

            outer_arc.append(
                (
                    center_x
                    + axis_x * lateral
                    + inward_x * inward,
                    center_y
                    + axis_y * lateral
                    + inward_y * inward,
                )
            )

        inner_arc = []

        for index in range(
            AtlasAncientTheatreCaveaBuilder
            .ARC_SEGMENTS,
            -1,
            -1,
        ):
            angle = (
                pi
                - pi
                * index
                / AtlasAncientTheatreCaveaBuilder
                .ARC_SEGMENTS
            )

            lateral = cos(angle) * inner_radius_m
            inward = sin(angle) * inner_radius_m

            inner_arc.append(
                (
                    center_x
                    + axis_x * lateral
                    + inward_x * inward,
                    center_y
                    + axis_y * lateral
                    + inward_y * inward,
                )
            )

        return outer_arc + inner_arc

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
