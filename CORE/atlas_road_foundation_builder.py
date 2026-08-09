# CORE/atlas_road_foundation_builder.py

from CORE.atlas_road_foundation_extruder import AtlasRoadFoundationExtruder
from CORE.atlas_urban_road_hierarchy_resolver import (
    AtlasUrbanRoadHierarchyResolver,
)
from CORE.atlas_physical_cartographic_exaggeration_resolver import (
    AtlasPhysicalCartographicExaggerationResolver,
)


class AtlasRoadFoundationBuilder:
    """
    ATLAS Road Foundation Builder v0.1

    Görev:
    - OSM road polyline verisini terrain'e oturan road mesh'e dönüştürmek.
    - Eski road_mesh_builder.py dosyasını bozmadan Foundation-First yol hattını kurmak.
    """

    DEFAULT_WIDTHS_M = {
        "motorway": 12.0,
        "trunk": 10.0,
        "primary": 8.0,
        "secondary": 7.0,
        "tertiary": 6.0,
        "residential": 5.0,
        "service": 4.0,
        "living_street": 4.0,
        "unclassified": 5.0,
        "road": 5.0,
    }

    @staticmethod
    def build_roads(
        roads,
        coordinate_engine,
        terrain_mesh,
        minimum_printable_width_mm=None,
        cartographic_product_size_mm=None,
        cartographic_nozzle_diameter_mm=None,
        cartographic_lod_level=None,
        debug=True,
    ):
        meshes = []
        accepted = 0
        skipped = 0

        for road in roads:
            road_type = road.get("road_type") or road.get("tags", {}).get("highway")

            geometry = road.get("geometry", [])

            if len(geometry) < 2:
                skipped += 1
                continue

            if minimum_printable_width_mm is None:
                if road_type not in AtlasRoadFoundationBuilder.DEFAULT_WIDTHS_M:
                    skipped += 1
                    continue

                width_m = AtlasRoadFoundationBuilder.DEFAULT_WIDTHS_M[
                    road_type
                ]
                width_mm = coordinate_engine.height_to_stl_mm(
                    width_m
                )
            else:
                tags = road.get(
                    "tags",
                    {},
                )

                source_width = tags.get(
                    "width"
                )

                profile = (
                    AtlasUrbanRoadHierarchyResolver.resolve_profile(
                        highway=road_type,
                        source_width=source_width,
                        scale_ratio=coordinate_engine.xy_scale,
                        minimum_printable_width_mm=(
                            minimum_printable_width_mm
                        ),
                    )
                )

                if profile is None:
                    skipped += 1
                    continue

                width_mm = profile.physical_width_mm

                use_cartographic_exaggeration = (
                    cartographic_product_size_mm is not None
                    and cartographic_nozzle_diameter_mm is not None
                    and cartographic_lod_level is not None
                )

                if use_cartographic_exaggeration:
                    default_width_m = (
                        AtlasUrbanRoadHierarchyResolver
                        .default_width_m(
                            road_type
                        )
                    )

                    if default_width_m is None:
                        skipped += 1
                        continue

                    source_width_m = (
                        AtlasUrbanRoadHierarchyResolver
                        .resolve_source_width_m(
                            source_width=source_width,
                            default_width_m=default_width_m,
                        )
                    )

                    exaggeration = (
                        AtlasPhysicalCartographicExaggerationResolver
                        .resolve(
                            semantic_class=(
                                profile.semantic_class
                            ),
                            source_width_m=source_width_m,
                            scale_ratio=(
                                coordinate_engine.xy_scale
                            ),
                            product_size_mm=(
                                cartographic_product_size_mm
                            ),
                            nozzle_diameter_mm=(
                                cartographic_nozzle_diameter_mm
                            ),
                            minimum_printable_width_mm=(
                                minimum_printable_width_mm
                            ),
                            semantic_priority=(
                                profile.semantic_priority
                            ),
                            lod_level=(
                                cartographic_lod_level
                            ),
                        )
                    )

                    width_mm = (
                        exaggeration.physical_width_mm
                    )

            mesh = AtlasRoadFoundationBuilder._build_polyline_mesh(
                geometry=geometry,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                width_mm=width_mm,
                road_type=road_type,
            )

            if mesh:
                mesh["source_id"] = road.get("id")
                meshes.append(mesh)
                accepted += 1
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ROAD FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input roads      : {len(roads)}")
            print(f"Accepted roads   : {accepted}")
            print(f"Skipped roads    : {skipped}")
            print(f"Road meshes      : {len(meshes)}")
            print(
                f"Road triangles   : {AtlasRoadFoundationBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_polyline_mesh(
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        points = coordinate_engine.geometry_to_stl_mm(geometry)
        points = AtlasRoadFoundationBuilder._clip_points_to_bounds(
            points=points,
            min_x=0.0,
            max_x=200.0,
            min_y=0.0,
            max_y=200.0,
        )

        if len(points) < 2:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for index in range(len(points) - 1):
            p1 = points[index]
            p2 = points[index + 1]

            start_is_straight_join = (
                index > 0
                and AtlasRoadFoundationBuilder
                ._segments_continue_straight(
                    points[index - 1],
                    points[index],
                    points[index + 1],
                )
            )

            end_is_straight_join = (
                index < len(points) - 2
                and AtlasRoadFoundationBuilder
                ._segments_continue_straight(
                    points[index],
                    points[index + 1],
                    points[index + 2],
                )
            )

            segment = AtlasRoadFoundationExtruder.build_segment(
                p1=p1,
                p2=p2,
                terrain_mesh=terrain_mesh,
                width_mm=width_mm,
                include_start_cap=(
                    not start_is_straight_join
                ),
                include_end_cap=(
                    not end_is_straight_join
                ),
            )

            if not segment:
                continue

            bottom.extend(segment["bottom"])
            top.extend(segment["top"])
            walls.extend(segment["walls"])
            triangles.extend(segment["triangles"])

        triangles = (
            AtlasRoadFoundationBuilder
            ._remove_duplicate_triangle_pairs(
                triangles
            )
        )

        if not triangles:
            return None

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "type": "road_foundation",
            "road_type": road_type,
            "placement_mode": "foundation_first",
        }

    @staticmethod
    def _segments_continue_straight(
        p1,
        p2,
        p3,
        tolerance=1e-9,
    ):
        first_x = float(p2[0]) - float(p1[0])
        first_y = float(p2[1]) - float(p1[1])

        second_x = float(p3[0]) - float(p2[0])
        second_y = float(p3[1]) - float(p2[1])

        first_length = (
            first_x * first_x
            + first_y * first_y
        ) ** 0.5

        second_length = (
            second_x * second_x
            + second_y * second_y
        ) ** 0.5

        if (
            first_length <= tolerance
            or second_length <= tolerance
        ):
            return False

        cross = (
            first_x * second_y
            - first_y * second_x
        )

        dot = (
            first_x * second_x
            + first_y * second_y
        )

        return (
            abs(cross)
            <= (
                tolerance
                * first_length
                * second_length
            )
            and dot > 0.0
        )

    @staticmethod
    def _remove_duplicate_triangle_pairs(
        triangles,
        precision=9,
    ):
        triangle_counts = {}

        def triangle_key(triangle):
            points = [
                tuple(
                    round(
                        float(value),
                        precision,
                    )
                    for value in point
                )
                for point in triangle
            ]

            return tuple(
                sorted(points)
            )

        for triangle in triangles:
            key = triangle_key(triangle)

            triangle_counts[key] = (
                triangle_counts.get(
                    key,
                    0,
                )
                + 1
            )

        return [
            triangle
            for triangle in triangles
            if triangle_counts[
                triangle_key(triangle)
            ]
            == 1
        ]

    @staticmethod
    def _clip_points_to_bounds(points, min_x, max_x, min_y, max_y):
        clipped = []

        for x, y in points:
            if min_x <= x <= max_x and min_y <= y <= max_y:
                clipped.append((x, y))

        return clipped

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict) and mesh.get("triangles"):
                total += len(mesh["triangles"])

        return total
