from __future__ import annotations

from copy import deepcopy

from shapely.geometry import Polygon

from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_semantic_material_hierarchy import (
    AtlasSemanticMaterialHierarchy,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)
from CORE.atlas_wall_collection_product_builder import (
    AtlasWallCollectionProductBuilder,
)
from CORE.atlas_wall_frame_hanger_mesher import (
    AtlasWallFrameHangerMesher,
)
from CORE.atlas_wall_hanger_spec import AtlasWallHangerSpec
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


class AtlasProductColorPreviewRenderer:
    DEFAULT_COLOR_ROOF_THICKNESS_MM = 0.40

    GROUP_TO_BATCH = {
        "terrain": "terrain",
        "buildings": "buildings",
        "landmarks": "landmarks",
        "roads": "roads",
        "parks": "parks",
        "trees": "trees",
        "forest_canopies": "trees",
        "waters": "water",
    }

    @staticmethod
    def _translate_mesh(
        mesh: dict,
        offset_x_mm: float,
        offset_y_mm: float,
    ) -> dict:
        translated = deepcopy(mesh)

        if "triangles" in translated:
            translated["triangles"] = [
                tuple(
                    (
                        float(x) + offset_x_mm,
                        float(y) + offset_y_mm,
                        float(z),
                    )
                    for x, y, z in triangle
                )
                for triangle in translated["triangles"]
            ]

        return translated

    @staticmethod
    def _replace_z(
        point: tuple,
        *,
        source_z: float,
        target_z: float,
        tolerance: float = 1e-6,
    ) -> tuple:
        x, y, z = point

        if abs(float(z) - float(source_z)) <= tolerance:
            z = target_z

        return (
            float(x),
            float(y),
            float(z),
        )

    @staticmethod
    def _triangulate_ring_at_z(
        points: list,
        *,
        z_level: float,
        reverse: bool = False,
    ) -> list:
        ring = []

        for point in points:
            if len(point) < 2:
                continue

            xy = (
                float(point[0]),
                float(point[1]),
            )

            if ring and xy == ring[-1]:
                continue

            ring.append(xy)

        if len(ring) > 1 and ring[0] == ring[-1]:
            ring.pop()

        flat_triangles = AtlasPolygonTriangulator.triangulate(
            ring
        )

        triangles = []

        for first, second, third in flat_triangles:
            first_3d = (
                float(first[0]),
                float(first[1]),
                float(z_level),
            )
            second_3d = (
                float(second[0]),
                float(second[1]),
                float(z_level),
            )
            third_3d = (
                float(third[0]),
                float(third[1]),
                float(z_level),
            )

            if reverse:
                triangles.append(
                    (
                        first_3d,
                        third_3d,
                        second_3d,
                    )
                )
            else:
                triangles.append(
                    (
                        first_3d,
                        second_3d,
                        third_3d,
                    )
                )

        return triangles

    @classmethod
    def _build_skillion_roof_color_solids(
        cls,
        *,
        mesh: dict,
    ) -> tuple[dict, dict] | None:
        if mesh.get("roof_geometry") != "skillion":
            return None

        wall_triangles = list(
            mesh.get("building_wall_triangles", [])
        )
        roof_triangles = list(
            mesh.get("building_roof_triangles", [])
        )
        body_top_points = list(mesh.get("top", []))
        skillion_top_points = list(
            mesh.get(
                "building_skillion_roof_points",
                [],
            )
        )

        if (
            not wall_triangles
            or not roof_triangles
            or len(body_top_points) < 3
            or len(skillion_top_points)
            != len(body_top_points)
        ):
            return None

        body_top_z = mesh.get("body_top_z")

        if body_top_z is None:
            body_top_z = max(
                float(point[2])
                for triangle in wall_triangles
                for point in triangle
            )

        bottom_points = list(mesh.get("bottom", []))

        if bottom_points:
            bottom_z = min(
                float(point[2])
                for point in bottom_points
            )
        else:
            bottom_z = min(
                float(point[2])
                for triangle in wall_triangles
                for point in triangle
            )

        body_top_triangles = cls._triangulate_ring_at_z(
            body_top_points,
            z_level=float(body_top_z),
            reverse=False,
        )
        roof_bottom_triangles = cls._triangulate_ring_at_z(
            body_top_points,
            z_level=float(body_top_z),
            reverse=True,
        )

        if (
            not body_top_triangles
            or not roof_bottom_triangles
        ):
            return None

        bottom_triangles = [
            triangle
            for triangle in mesh.get("triangles", [])
            if all(
                abs(float(point[2]) - bottom_z) <= 1e-6
                for point in triangle
            )
        ]

        if not bottom_triangles:
            bottom_triangles = cls._triangulate_ring_at_z(
                bottom_points or body_top_points,
                z_level=bottom_z,
                reverse=True,
            )

        boundary_edges = {}

        for triangle in roof_triangles:
            for first, second in (
                (triangle[0], triangle[1]),
                (triangle[1], triangle[2]),
                (triangle[2], triangle[0]),
            ):
                first_key = tuple(
                    round(float(value), 6)
                    for value in first
                )
                second_key = tuple(
                    round(float(value), 6)
                    for value in second
                )
                edge_key = tuple(
                    sorted(
                        (
                            first_key,
                            second_key,
                        )
                    )
                )

                if edge_key in boundary_edges:
                    boundary_edges[edge_key]["count"] += 1
                else:
                    boundary_edges[edge_key] = {
                        "count": 1,
                        "first": first,
                        "second": second,
                    }

        open_boundary_edges = [
            edge
            for edge in boundary_edges.values()
            if edge["count"] == 1
        ]

        source_roof_already_has_sides = (
            bool(open_boundary_edges)
            and all(
                abs(
                    float(point[2])
                    - float(body_top_z)
                )
                <= 1e-6
                for edge in open_boundary_edges
                for point in (
                    edge["first"],
                    edge["second"],
                )
            )
        )

        roof_side_triangles = []

        if not source_roof_already_has_sides:
            point_count = len(body_top_points)

            for index in range(point_count):
                next_index = (index + 1) % point_count

                bottom_first = (
                    float(body_top_points[index][0]),
                    float(body_top_points[index][1]),
                    float(body_top_z),
                )
                bottom_second = (
                    float(body_top_points[next_index][0]),
                    float(body_top_points[next_index][1]),
                    float(body_top_z),
                )
                top_first = tuple(
                    float(value)
                    for value in skillion_top_points[index]
                )
                top_second = tuple(
                    float(value)
                    for value in skillion_top_points[next_index]
                )

                roof_side_triangles.extend(
                    [
                        (
                            bottom_first,
                            bottom_second,
                            top_second,
                        ),
                        (
                            bottom_first,
                            top_second,
                            top_first,
                        ),
                    ]
                )

        wall_mesh = {
            "type": "building_wall_color_solid",
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *body_top_triangles,
            ],
        }
        roof_mesh = {
            "type": "building_roof_color_solid",
            "triangles": [
                *roof_triangles,
                *roof_bottom_triangles,
                *roof_side_triangles,
            ],
        }

        return wall_mesh, roof_mesh

    @classmethod
    def _build_pitched_roof_color_solids(
        cls,
        *,
        mesh: dict,
    ) -> tuple[dict, dict] | None:
        roof_geometry = mesh.get("roof_geometry")

        if roof_geometry not in {"gable", "hipped"}:
            return None

        wall_triangles = list(
            mesh.get("building_wall_triangles", [])
        )
        roof_triangles = list(
            mesh.get("building_roof_triangles", [])
        )
        top_points = list(mesh.get("top", []))

        if (
            not wall_triangles
            or not roof_triangles
            or len(top_points) < 3
        ):
            return None

        body_top_z = mesh.get("body_top_z")

        if body_top_z is None:
            body_top_z = max(
                float(point[2])
                for triangle in wall_triangles
                for point in triangle
            )

        bottom_points = list(mesh.get("bottom", []))

        if bottom_points:
            bottom_z = min(
                float(point[2])
                for point in bottom_points
            )
        else:
            bottom_z = min(
                float(point[2])
                for triangle in wall_triangles
                for point in triangle
            )

        body_top_triangles = cls._triangulate_ring_at_z(
            top_points,
            z_level=float(body_top_z),
            reverse=False,
        )

        if not body_top_triangles:
            return None

        bottom_triangles = [
            triangle
            for triangle in mesh.get("triangles", [])
            if all(
                abs(
                    float(point[2])
                    - bottom_z
                ) <= 1e-6
                for point in triangle
            )
        ]

        if not bottom_triangles:
            bottom_triangles = cls._triangulate_ring_at_z(
                bottom_points or top_points,
                z_level=bottom_z,
                reverse=True,
            )

        closed_roof_triangles = list(roof_triangles)

        if roof_geometry == "hipped":
            roof_bottom_triangles = (
                cls._triangulate_ring_at_z(
                    top_points,
                    z_level=float(body_top_z),
                    reverse=True,
                )
            )

            if not roof_bottom_triangles:
                return None

            closed_roof_triangles.extend(
                roof_bottom_triangles
            )

        wall_mesh = {
            "type": "building_wall_color_solid",
            "triangles": [
                *bottom_triangles,
                *wall_triangles,
                *body_top_triangles,
            ],
        }
        roof_mesh = {
            "type": "building_roof_color_solid",
            "triangles": closed_roof_triangles,
        }

        return wall_mesh, roof_mesh

    @classmethod
    def _build_flat_roof_color_solids(
        cls,
        *,
        mesh: dict,
    ) -> tuple[dict, dict] | None:
        roof_triangles = list(
            mesh.get(
                "building_flat_roof_triangles",
                [],
            )
        )
        wall_triangles = list(
            mesh.get(
                "building_wall_triangles",
                [],
            )
        )

        if not roof_triangles or not wall_triangles:
            return None

        roof_z_values = {
            round(float(point[2]), 6)
            for triangle in roof_triangles
            for point in triangle
        }

        if len(roof_z_values) != 1:
            return None

        roof_top_z = float(next(iter(roof_z_values)))
        bottom_points = list(mesh.get("bottom", []))

        if bottom_points:
            bottom_z = min(
                float(point[2])
                for point in bottom_points
            )
        else:
            bottom_z = min(
                float(point[2])
                for triangle in wall_triangles
                for point in triangle
            )

        available_height = roof_top_z - bottom_z

        if available_height <= 0.0:
            return None

        roof_thickness_mm = min(
            cls.DEFAULT_COLOR_ROOF_THICKNESS_MM,
            available_height / 2.0,
        )
        roof_bottom_z = roof_top_z - roof_thickness_mm

        lowered_wall_triangles = [
            tuple(
                cls._replace_z(
                    point,
                    source_z=roof_top_z,
                    target_z=roof_bottom_z,
                )
                for point in triangle
            )
            for triangle in wall_triangles
        ]

        wall_top_triangles = [
            tuple(
                cls._replace_z(
                    point,
                    source_z=roof_top_z,
                    target_z=roof_bottom_z,
                )
                for point in triangle
            )
            for triangle in roof_triangles
        ]

        bottom_triangles = [
            triangle
            for triangle in mesh.get("triangles", [])
            if all(
                abs(float(point[2]) - bottom_z) <= 1e-6
                for point in triangle
            )
        ]

        if not bottom_triangles:
            bottom_triangles = cls._triangulate_ring_at_z(
                bottom_points or mesh.get("top", []),
                z_level=bottom_z,
                reverse=True,
            )

        roof_bottom_triangles = [
            (
                cls._replace_z(
                    triangle[0],
                    source_z=roof_top_z,
                    target_z=roof_bottom_z,
                ),
                cls._replace_z(
                    triangle[2],
                    source_z=roof_top_z,
                    target_z=roof_bottom_z,
                ),
                cls._replace_z(
                    triangle[1],
                    source_z=roof_top_z,
                    target_z=roof_bottom_z,
                ),
            )
            for triangle in roof_triangles
        ]

        boundary_edges = {}

        for triangle in roof_triangles:
            for first, second in (
                (triangle[0], triangle[1]),
                (triangle[1], triangle[2]),
                (triangle[2], triangle[0]),
            ):
                first_key = tuple(
                    round(float(value), 6)
                    for value in first
                )
                second_key = tuple(
                    round(float(value), 6)
                    for value in second
                )
                key = tuple(sorted((first_key, second_key)))

                if key in boundary_edges:
                    boundary_edges[key]["count"] += 1
                else:
                    boundary_edges[key] = {
                        "count": 1,
                        "first": first,
                        "second": second,
                    }

        roof_side_triangles = []

        for edge in boundary_edges.values():
            if edge["count"] != 1:
                continue

            top_first = edge["first"]
            top_second = edge["second"]
            bottom_first = cls._replace_z(
                top_first,
                source_z=roof_top_z,
                target_z=roof_bottom_z,
            )
            bottom_second = cls._replace_z(
                top_second,
                source_z=roof_top_z,
                target_z=roof_bottom_z,
            )

            roof_side_triangles.extend(
                [
                    (
                        bottom_first,
                        bottom_second,
                        top_second,
                    ),
                    (
                        bottom_first,
                        top_second,
                        top_first,
                    ),
                ]
            )

        wall_mesh = {
            "type": "building_wall_color_solid",
            "triangles": [
                *bottom_triangles,
                *lowered_wall_triangles,
                *wall_top_triangles,
            ],
        }
        roof_mesh = {
            "type": "building_roof_color_solid",
            "triangles": [
                *roof_triangles,
                *roof_bottom_triangles,
                *roof_side_triangles,
            ],
        }

        return wall_mesh, roof_mesh

    @staticmethod
    def _safe_footprint_polygon(mesh: dict) -> Polygon | None:
        points = list(mesh.get("bottom", []))

        if len(points) < 3:
            points = list(mesh.get("top", []))

        ring = []

        for point in points:
            if len(point) < 2:
                continue

            xy = (
                float(point[0]),
                float(point[1]),
            )

            if ring and xy == ring[-1]:
                continue

            ring.append(xy)

        if len(ring) > 1 and ring[0] == ring[-1]:
            ring.pop()

        if len(ring) < 3:
            return None

        try:
            polygon = Polygon(ring)
        except (TypeError, ValueError):
            return None

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
    def _mesh_bottom_top_z(
        mesh: dict,
    ) -> tuple[float, float] | None:
        bottom_points = list(mesh.get("bottom", []))
        top_points = list(mesh.get("top", []))

        bottom_z = mesh.get("foundation_z")
        top_z = mesh.get("body_top_z")

        if bottom_points:
            bottom_z = min(
                float(point[2])
                for point in bottom_points
                if len(point) >= 3
            )

        if top_points:
            top_z = max(
                float(point[2])
                for point in top_points
                if len(point) >= 3
            )

        if bottom_z is None or top_z is None:
            return None

        return (
            float(bottom_z),
            float(top_z),
        )

    @classmethod
    def _filter_covered_same_height_building_parts(
        cls,
        meshes: list,
        *,
        z_tolerance: float = 1e-6,
        coverage_tolerance: float = 1e-6,
    ) -> list:
        prepared = []

        for mesh in meshes:
            polygon = cls._safe_footprint_polygon(mesh)
            z_range = cls._mesh_bottom_top_z(mesh)

            prepared.append(
                {
                    "mesh": mesh,
                    "polygon": polygon,
                    "z_range": z_range,
                    "is_building_part": bool(
                        mesh.get("is_building_part")
                        or (
                            mesh.get(
                                "building_roof_decision_source"
                            )
                            == "building_part"
                        )
                    ),
                }
            )

        retained = []

        for candidate in prepared:
            if not candidate["is_building_part"]:
                retained.append(candidate["mesh"])
                continue

            candidate_polygon = candidate["polygon"]

            if candidate_polygon is None:
                retained.append(candidate["mesh"])
                continue

            covered = False

            for parent in prepared:
                if parent is candidate:
                    continue

                if parent["is_building_part"]:
                    continue

                parent_polygon = parent["polygon"]

                if parent_polygon is None:
                    continue

                if parent_polygon.buffer(
                    coverage_tolerance
                ).covers(candidate_polygon):
                    covered = True
                    break

            if not covered:
                retained.append(candidate["mesh"])

        return retained

    @classmethod
    def _separate_touching_building_solids(
        cls,
        meshes: list,
        *,
        separation_mm: float = 1e-4,
    ) -> list:
        separated = [deepcopy(mesh) for mesh in meshes]
        polygons = [
            cls._safe_footprint_polygon(mesh)
            for mesh in separated
        ]

        for first_index in range(len(separated)):
            first_polygon = polygons[first_index]

            if first_polygon is None:
                continue

            for second_index in range(
                first_index + 1,
                len(separated),
            ):
                second_polygon = polygons[second_index]

                if second_polygon is None:
                    continue

                if not first_polygon.intersects(second_polygon):
                    continue

                first_centroid = first_polygon.centroid
                second_centroid = second_polygon.centroid

                offset_x = (
                    float(second_centroid.x)
                    - float(first_centroid.x)
                )
                offset_y = (
                    float(second_centroid.y)
                    - float(first_centroid.y)
                )
                length = (
                    offset_x * offset_x
                    + offset_y * offset_y
                ) ** 0.5

                if length <= 1e-12:
                    offset_x = separation_mm
                    offset_y = 0.0
                else:
                    offset_x = (
                        offset_x / length
                    ) * separation_mm
                    offset_y = (
                        offset_y / length
                    ) * separation_mm

                separated[second_index] = (
                    cls._translate_mesh_geometry_xy(
                        separated[second_index],
                        offset_x_mm=offset_x,
                        offset_y_mm=offset_y,
                    )
                )
                polygons[second_index] = (
                    cls._safe_footprint_polygon(
                        separated[second_index]
                    )
                )

        return separated

    @classmethod
    def _filter_covered_grass_parks(
        cls,
        meshes: list,
        *,
        coverage_tolerance: float = 1e-6,
    ) -> list:
        prepared = []

        for mesh in meshes:
            prepared.append(
                {
                    "mesh": mesh,
                    "park_type": mesh.get("park_type"),
                    "polygon": cls._safe_footprint_polygon(mesh),
                }
            )

        retained = []

        covered_subarea_types = {
            "landuse:grass",
            "leisure:playground",
            "leisure:garden",
        }

        for candidate in prepared:
            if (
                candidate["park_type"]
                not in covered_subarea_types
            ):
                retained.append(candidate["mesh"])
                continue

            candidate_polygon = candidate["polygon"]

            if candidate_polygon is None:
                retained.append(candidate["mesh"])
                continue

            covered = False

            for parent in prepared:
                if parent is candidate:
                    continue

                if parent["park_type"] != "leisure:park":
                    continue

                parent_polygon = parent["polygon"]

                if parent_polygon is None:
                    continue

                if parent_polygon.buffer(
                    coverage_tolerance
                ).covers(candidate_polygon):
                    covered = True
                    break

            if not covered:
                retained.append(candidate["mesh"])

        return retained

    @staticmethod
    def _triangle_xy_area(triangle: tuple) -> float:
        first, second, third = triangle

        return abs(
            (
                float(first[0])
                * (
                    float(second[1])
                    - float(third[1])
                )
                + float(second[0])
                * (
                    float(third[1])
                    - float(first[1])
                )
                + float(third[0])
                * (
                    float(first[1])
                    - float(second[1])
                )
            )
            / 2.0
        )

    @classmethod
    def _remove_internal_park_boundary_walls(
        cls,
        meshes: list,
        *,
        boundary_tolerance: float = 1e-6,
    ) -> list:
        prepared = [
            {
                "mesh": mesh,
                "polygon": cls._safe_footprint_polygon(mesh),
            }
            for mesh in meshes
        ]

        shared_boundaries = {
            index: []
            for index in range(len(prepared))
        }

        for first_index, first in enumerate(prepared):
            first_polygon = first["polygon"]

            if first_polygon is None:
                continue

            for second_index in range(
                first_index + 1,
                len(prepared),
            ):
                second_polygon = prepared[
                    second_index
                ]["polygon"]

                if second_polygon is None:
                    continue

                shared = first_polygon.boundary.intersection(
                    second_polygon.boundary
                )

                if shared.is_empty or shared.length <= 0.0:
                    continue

                shared_boundaries[first_index].append(shared)
                shared_boundaries[second_index].append(shared)

        cleaned_meshes = []

        for mesh_index, prepared_mesh in enumerate(prepared):
            mesh = prepared_mesh["mesh"]
            boundaries = shared_boundaries[mesh_index]

            if not boundaries:
                cleaned_meshes.append(mesh)
                continue

            cleaned = deepcopy(mesh)
            retained_triangles = []

            for triangle in mesh.get("triangles", []):
                if (
                    cls._triangle_xy_area(triangle)
                    > boundary_tolerance
                ):
                    retained_triangles.append(triangle)
                    continue

                xy_points = [
                    (
                        float(point[0]),
                        float(point[1]),
                    )
                    for point in triangle
                ]

                lies_on_shared_boundary = any(
                    all(
                        boundary.distance(
                            Polygon(
                                [
                                    xy_point,
                                    (
                                        xy_point[0]
                                        + boundary_tolerance,
                                        xy_point[1],
                                    ),
                                    (
                                        xy_point[0],
                                        xy_point[1]
                                        + boundary_tolerance,
                                    ),
                                ]
                            ).centroid
                        )
                        <= boundary_tolerance
                        for xy_point in xy_points
                    )
                    for boundary in boundaries
                )

                if not lies_on_shared_boundary:
                    retained_triangles.append(triangle)

            cleaned["triangles"] = retained_triangles
            cleaned_meshes.append(cleaned)

        return cleaned_meshes

    @classmethod
    def _translate_mesh_geometry_xy(
        cls,
        mesh: dict,
        *,
        offset_x_mm: float,
        offset_y_mm: float,
    ) -> dict:
        translated = deepcopy(mesh)

        triangle_keys = (
            "triangles",
            "building_wall_triangles",
            "building_roof_triangles",
            "building_flat_roof_triangles",
            "building_gable_roof_triangles",
            "building_hipped_roof_triangles",
        )

        for key in triangle_keys:
            if key not in translated:
                continue

            translated[key] = [
                tuple(
                    (
                        float(point[0]) + offset_x_mm,
                        float(point[1]) + offset_y_mm,
                        float(point[2]),
                    )
                    for point in triangle
                )
                for triangle in translated[key]
            ]

        for key in ("bottom", "top"):
            if key not in translated:
                continue

            translated[key] = [
                (
                    float(point[0]) + offset_x_mm,
                    float(point[1]) + offset_y_mm,
                    float(point[2]),
                )
                for point in translated[key]
            ]

        if translated.get("roof_apex") is not None:
            point = translated["roof_apex"]
            translated["roof_apex"] = (
                float(point[0]) + offset_x_mm,
                float(point[1]) + offset_y_mm,
                float(point[2]),
            )

        return translated

    @classmethod
    def _separate_point_touching_park_solids(
        cls,
        meshes: list,
        *,
        separation_mm: float = 1e-4,
    ) -> list:
        separated = [deepcopy(mesh) for mesh in meshes]
        polygons = [
            cls._safe_footprint_polygon(mesh)
            for mesh in separated
        ]

        for first_index in range(len(separated)):
            first_polygon = polygons[first_index]

            if first_polygon is None:
                continue

            for second_index in range(
                first_index + 1,
                len(separated),
            ):
                second_polygon = polygons[second_index]

                if second_polygon is None:
                    continue

                intersection = first_polygon.intersection(
                    second_polygon
                )

                if intersection.is_empty:
                    continue

                if intersection.geom_type not in {
                    "Point",
                    "MultiPoint",
                }:
                    continue

                first_centroid = first_polygon.centroid
                second_centroid = second_polygon.centroid

                offset_x = (
                    float(second_centroid.x)
                    - float(first_centroid.x)
                )
                offset_y = (
                    float(second_centroid.y)
                    - float(first_centroid.y)
                )
                length = (
                    offset_x * offset_x
                    + offset_y * offset_y
                ) ** 0.5

                if length <= 1e-12:
                    offset_x = separation_mm
                    offset_y = 0.0
                else:
                    offset_x = (
                        offset_x / length
                    ) * separation_mm
                    offset_y = (
                        offset_y / length
                    ) * separation_mm

                separated[second_index] = (
                    cls._translate_mesh_geometry_xy(
                        separated[second_index],
                        offset_x_mm=offset_x,
                        offset_y_mm=offset_y,
                    )
                )
                second_polygon = cls._safe_footprint_polygon(
                    separated[second_index]
                )
                polygons[second_index] = second_polygon

        return separated

    @classmethod
    def build_scene(
        cls,
        *,
        city_result: dict,
        frame_spec: AtlasWallFrameSpec,
        frame_depth_mm: float,
        material_profile: AtlasProductPreviewMaterialProfile,
        label_plate_spec: AtlasLabelPlateSpec | None = None,
        label_text_spec: AtlasLabelTextSpec | None = None,
        highlighted_building_source_ids=None,
        highlighted_landmark_ids=None,
    ) -> dict:
        highlighted_building_source_ids = {
            str(source_id)
            for source_id in (
                highlighted_building_source_ids or ()
            )
        }
        highlighted_landmark_ids = {
            str(landmark_id)
            for landmark_id in (
                highlighted_landmark_ids or ()
            )
        }

        applied_highlighted_building_source_ids = set()
        applied_highlighted_landmark_ids = set()

        terrain_size_x_mm = float(city_result["terrain_size_x_mm"])
        terrain_size_y_mm = float(city_result["terrain_size_y_mm"])

        city_offset_x_mm = -(terrain_size_x_mm / 2.0)
        city_offset_y_mm = -(terrain_size_y_mm / 2.0)

        hanger_spec = AtlasWallHangerSpec.for_product_size(
            outer_width_mm=frame_spec.outer_width_mm,
            outer_height_mm=frame_spec.outer_height_mm,
            frame_width_mm=frame_spec.frame_width_mm,
            frame_depth_mm=frame_depth_mm,
        )

        frame_mesh = AtlasWallFrameHangerMesher.build(
            frame_spec=frame_spec,
            hanger_spec=hanger_spec,
            frame_depth_mm=frame_depth_mm,
        )

        semantic_material_hierarchy = (
            AtlasSemanticMaterialHierarchy.resolve(
                material_profile=material_profile,
                maximum_physical_color_count=None,
            )
        )

        semantic_roles = (
            semantic_material_hierarchy["roles"]
        )

        material_batches = {
            "frame": {
                "rgb": material_profile.frame_rgb,
                "meshes": [frame_mesh],
            },
            "terrain": {
                "rgb": material_profile.terrain_rgb,
                "meshes": [],
            },
            "buildings": {
                "rgb": material_profile.building_rgb,
                "meshes": [],
            },
            "landmarks": {
                "rgb": material_profile.landmark_rgb,
                "meshes": [],
            },
            "building_walls": {
                "rgb": material_profile.building_wall_rgb,
                "meshes": [],
            },
            "building_roofs": {
                "rgb": material_profile.building_roof_rgb,
                "meshes": [],
            },
            "roads": {
                "rgb": material_profile.road_rgb,
                "meshes": [],
            },
            "parks": {
                "rgb": material_profile.green_rgb,
                "meshes": [],
            },
            "trees": {
                "rgb": material_profile.tree_rgb,
                "meshes": [],
            },
            "water": {
                "rgb": material_profile.water_rgb,
                "meshes": [],
            },
            "label_plate": {
                "rgb": material_profile.label_plate_rgb,
                "meshes": [],
            },
            "label_text": {
                "rgb": material_profile.label_text_rgb,
                "meshes": [],
            },
        }

        batch_to_semantic_role = {
            "frame": "frame",
            "terrain": "terrain",
            "buildings": "generic_building",
            "landmarks": "landmark_wall",
            "building_walls": "generic_building",
            "building_roofs": "generic_building_roof",
            "roads": "roads_hardscape",
            "parks": "vegetation",
            "trees": "vegetation",
            "water": "water",
            "label_plate": "label_plate",
            "label_text": "label_text",
        }

        for batch_name, semantic_role in (
            batch_to_semantic_role.items()
        ):
            role = semantic_roles[
                semantic_role
            ]

            material_batches[
                batch_name
            ].update(
                {
                    "semantic_role": (
                        role["semantic_role"]
                    ),
                    "physical_material": (
                        role["physical_material"]
                    ),
                    "surface_treatment": (
                        role["surface_treatment"]
                    ),
                    "relief_priority": (
                        role["relief_priority"]
                    ),
                    "readability_priority": (
                        role["readability_priority"]
                    ),
                }
            )

        mesh_groups = city_result.get("mesh_groups", {})

        building_meshes = (
            cls._filter_covered_same_height_building_parts(
                list(mesh_groups.get("buildings", []))
            )
        )
        building_meshes = (
            cls._separate_touching_building_solids(
                building_meshes
            )
        )
        park_meshes = cls._filter_covered_grass_parks(
            list(mesh_groups.get("parks", []))
        )
        park_meshes = (
            cls._separate_point_touching_park_solids(
                park_meshes
            )
        )
        park_meshes = (
            cls._remove_internal_park_boundary_walls(
                park_meshes
            )
        )

        for group_name, batch_name in cls.GROUP_TO_BATCH.items():
            if group_name == "buildings":
                group_meshes = building_meshes
            elif group_name == "parks":
                group_meshes = park_meshes
            else:
                group_meshes = mesh_groups.get(group_name, [])

            for mesh in group_meshes:
                if (
                    group_name == "buildings"
                    and "building_wall_triangles" in mesh
                    and "building_roof_triangles" in mesh
                ):
                    color_solids = (
                        cls._build_flat_roof_color_solids(
                            mesh=mesh,
                        )
                    )

                    if color_solids is None:
                        color_solids = (
                            cls._build_skillion_roof_color_solids(
                                mesh=mesh,
                            )
                        )

                    if color_solids is None:
                        color_solids = (
                            cls._build_pitched_roof_color_solids(
                                mesh=mesh,
                            )
                        )

                    if color_solids is None:
                        wall_mesh = {
                            "type": mesh.get(
                                "type",
                                "building",
                            ),
                            "triangles": (
                                mesh[
                                    "building_wall_triangles"
                                ]
                            ),
                        }
                        roof_mesh = {
                            "type": mesh.get(
                                "type",
                                "building",
                            ),
                            "triangles": (
                                mesh[
                                    "building_roof_triangles"
                                ]
                            ),
                        }
                    else:
                        wall_mesh, roof_mesh = color_solids

                    source_id = mesh.get("source_id")

                    wall_mesh["source_id"] = source_id
                    roof_mesh["source_id"] = source_id

                    translated_wall_mesh = cls._translate_mesh(
                        wall_mesh,
                        city_offset_x_mm,
                        city_offset_y_mm,
                    )
                    translated_roof_mesh = cls._translate_mesh(
                        roof_mesh,
                        city_offset_x_mm,
                        city_offset_y_mm,
                    )

                    if (
                        source_id is not None
                        and str(source_id)
                        in highlighted_building_source_ids
                    ):
                        highlighted_mesh = {
                            "type": "highlighted_building",
                            "source_id": source_id,
                            "triangles": list(
                                mesh.get("triangles", [])
                            ),
                        }
                        material_batches[
                            "building_roofs"
                        ]["meshes"].append(
                            cls._translate_mesh(
                                highlighted_mesh,
                                city_offset_x_mm,
                                city_offset_y_mm,
                            )
                        )
                        applied_highlighted_building_source_ids.add(
                            str(source_id)
                        )
                        continue

                    material_batches[
                        "building_walls"
                    ]["meshes"].append(
                        translated_wall_mesh
                    )
                    material_batches[
                        "building_roofs"
                    ]["meshes"].append(
                        translated_roof_mesh
                    )
                    continue

                source_id = mesh.get("source_id")
                landmark_id = mesh.get("landmark_id")

                is_highlighted_building_component = (
                    group_name == "buildings"
                    and source_id is not None
                    and str(source_id)
                    in highlighted_building_source_ids
                )
                is_highlighted_landmark = (
                    group_name == "landmarks"
                    and landmark_id is not None
                    and str(landmark_id)
                    in highlighted_landmark_ids
                )

                if (
                    is_highlighted_building_component
                    or is_highlighted_landmark
                ):
                    highlighted_mesh = dict(mesh)
                    highlighted_mesh["type"] = (
                        "highlighted_building_component"
                        if is_highlighted_building_component
                        else "highlighted_landmark"
                    )

                    material_batches[
                        "building_roofs"
                    ]["meshes"].append(
                        cls._translate_mesh(
                            highlighted_mesh,
                            city_offset_x_mm,
                            city_offset_y_mm,
                        )
                    )

                    if is_highlighted_building_component:
                        applied_highlighted_building_source_ids.add(
                            str(source_id)
                        )

                    if is_highlighted_landmark:
                        applied_highlighted_landmark_ids.add(
                            str(landmark_id)
                        )

                    continue

                material_batches[batch_name]["meshes"].append(
                    cls._translate_mesh(
                        mesh,
                        city_offset_x_mm,
                        city_offset_y_mm,
                    )
                )

        if label_plate_spec is not None or label_text_spec is not None:
            product = AtlasWallCollectionProductBuilder.build(
                city_result=city_result,
                frame_spec=frame_spec,
                frame_depth_mm=frame_depth_mm,
                label_plate_spec=label_plate_spec,
                label_text_spec=label_text_spec,
            )
            material_batches["label_plate"]["meshes"].extend(
                product["label_plate_meshes"]
            )
            material_batches["label_text"]["meshes"].extend(
                product["label_text_meshes"]
            )
            material_batches["label_text"]["meshes"].extend(
                product["label_graduation_cap_meshes"]
            )

        return {
            "type": "product_color_preview_scene",
            "profile_name": material_profile.name,
            "semantic_material_hierarchy": (
                semantic_material_hierarchy
            ),
            "resolved_scene_morphology": (
                city_result.get(
                    "resolved_scene_morphology"
                )
            ),
            "effective_scene_morphology": (
                city_result.get(
                    "effective_scene_morphology"
                )
            ),
            "morphology_composition_policy": (
                city_result.get(
                    "morphology_composition_policy"
                )
            ),
            "city_composition_lod": (
                city_result.get(
                    "city_composition_lod"
                )
            ),
            "city_composition_suppressed_meshes": (
                city_result.get(
                    "city_composition_suppressed_meshes",
                    0,
                )
            ),
            "highlighting": {
                "requested_building_source_ids": tuple(
                    sorted(
                        highlighted_building_source_ids
                    )
                ),
                "applied_building_source_ids": tuple(
                    sorted(
                        applied_highlighted_building_source_ids
                    )
                ),
                "requested_landmark_ids": tuple(
                    sorted(
                        highlighted_landmark_ids
                    )
                ),
                "applied_landmark_ids": tuple(
                    sorted(
                        applied_highlighted_landmark_ids
                    )
                ),
            },
            "outer_width_mm": frame_spec.outer_width_mm,
            "outer_height_mm": frame_spec.outer_height_mm,
            "opening_width_mm": frame_spec.inner_width_mm,
            "opening_height_mm": frame_spec.inner_height_mm,
            "frame_depth_mm": float(frame_depth_mm),
            "city_offset_x_mm": city_offset_x_mm,
            "city_offset_y_mm": city_offset_y_mm,
            "material_batches": material_batches,
        }
