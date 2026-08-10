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
        clip_bounds=None,
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

            mesh_kwargs = {
                "geometry": geometry,
                "coordinate_engine": coordinate_engine,
                "terrain_mesh": terrain_mesh,
                "width_mm": width_mm,
                "road_type": road_type,
            }

            if clip_bounds is not None:
                mesh_kwargs["clip_bounds"] = clip_bounds

            mesh = AtlasRoadFoundationBuilder._build_polyline_mesh(
                **mesh_kwargs
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
        clip_bounds=None,
    ):
        points = coordinate_engine.geometry_to_stl_mm(
            geometry
        )

        segment_records = []

        if clip_bounds is None:
            # Preserve legacy direct-builder behavior.
            points = (
                AtlasRoadFoundationBuilder
                ._clip_points_to_bounds(
                    points=points,
                    min_x=0.0,
                    max_x=200.0,
                    min_y=0.0,
                    max_y=200.0,
                )
            )

            for index in range(
                len(points) - 1
            ):
                segment_records.append(
                    (
                        index,
                        points[index],
                        points[index + 1],
                    )
                )

        else:
            if len(clip_bounds) != 4:
                raise ValueError(
                    "clip_bounds must contain "
                    "(min_x, max_x, min_y, max_y)"
                )

            (
                min_x,
                max_x,
                min_y,
                max_y,
            ) = (
                float(value)
                for value in clip_bounds
            )

            if (
                max_x <= min_x
                or max_y <= min_y
            ):
                raise ValueError(
                    "clip_bounds must have "
                    "positive area"
                )

            half_width = (
                float(width_mm) / 2.0
            )

            for index in range(
                len(points) - 1
            ):
                p1 = points[index]
                p2 = points[index + 1]

                dx = (
                    float(p2[0])
                    - float(p1[0])
                )
                dy = (
                    float(p2[1])
                    - float(p1[1])
                )

                length = (
                    dx * dx
                    + dy * dy
                ) ** 0.5

                if length <= 1e-12:
                    continue

                normal_x = (
                    -dy / length
                )
                normal_y = (
                    dx / length
                )

                # Clip the centerline against bounds
                # inset by this segment's perpendicular
                # half-width. Therefore the extruded
                # road solid, not only its centerline,
                # remains inside the product rectangle.
                inset_x = (
                    abs(normal_x)
                    * half_width
                )
                inset_y = (
                    abs(normal_y)
                    * half_width
                )

                segment_min_x = (
                    min_x + inset_x
                )
                segment_max_x = (
                    max_x - inset_x
                )
                segment_min_y = (
                    min_y + inset_y
                )
                segment_max_y = (
                    max_y - inset_y
                )

                if (
                    segment_max_x
                    <= segment_min_x
                    or segment_max_y
                    <= segment_min_y
                ):
                    continue

                clipped = (
                    AtlasRoadFoundationBuilder
                    ._clip_segment_to_bounds(
                        p1=p1,
                        p2=p2,
                        min_x=segment_min_x,
                        max_x=segment_max_x,
                        min_y=segment_min_y,
                        max_y=segment_max_y,
                    )
                )

                if clipped is None:
                    continue

                segment_records.append(
                    (
                        index,
                        clipped[0],
                        clipped[1],
                    )
                )

        if not segment_records:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for record_index, (
            source_index,
            p1,
            p2,
        ) in enumerate(segment_records):
            start_is_straight_join = False
            end_is_straight_join = False

            if record_index > 0:
                (
                    previous_source_index,
                    previous_p1,
                    previous_p2,
                ) = segment_records[
                    record_index - 1
                ]

                if (
                    previous_source_index
                    == source_index - 1
                    and AtlasRoadFoundationBuilder
                    ._points_match(
                        previous_p2,
                        p1,
                    )
                ):
                    start_is_straight_join = (
                        AtlasRoadFoundationBuilder
                        ._segments_continue_straight(
                            previous_p1,
                            p1,
                            p2,
                        )
                    )

            if (
                record_index
                < len(segment_records) - 1
            ):
                (
                    next_source_index,
                    next_p1,
                    next_p2,
                ) = segment_records[
                    record_index + 1
                ]

                if (
                    next_source_index
                    == source_index + 1
                    and AtlasRoadFoundationBuilder
                    ._points_match(
                        p2,
                        next_p1,
                    )
                ):
                    end_is_straight_join = (
                        AtlasRoadFoundationBuilder
                        ._segments_continue_straight(
                            p1,
                            p2,
                            next_p2,
                        )
                    )

            segment = (
                AtlasRoadFoundationExtruder
                .build_segment(
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
            )

            if not segment:
                continue

            bottom.extend(
                segment["bottom"]
            )
            top.extend(
                segment["top"]
            )
            walls.extend(
                segment["walls"]
            )
            triangles.extend(
                segment["triangles"]
            )

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
    def _clip_segment_to_bounds(
        p1,
        p2,
        min_x,
        max_x,
        min_y,
        max_y,
        tolerance=1e-12,
    ):
        x1 = float(p1[0])
        y1 = float(p1[1])
        x2 = float(p2[0])
        y2 = float(p2[1])

        dx = x2 - x1
        dy = y2 - y1

        if (
            abs(dx) <= tolerance
            and abs(dy) <= tolerance
        ):
            return None

        lower = 0.0
        upper = 1.0

        constraints = (
            (-dx, x1 - float(min_x)),
            (dx, float(max_x) - x1),
            (-dy, y1 - float(min_y)),
            (dy, float(max_y) - y1),
        )

        for direction, distance in constraints:
            if abs(direction) <= tolerance:
                if distance < -tolerance:
                    return None

                continue

            ratio = (
                distance / direction
            )

            if direction < 0.0:
                if ratio > upper:
                    return None

                lower = max(
                    lower,
                    ratio,
                )

            else:
                if ratio < lower:
                    return None

                upper = min(
                    upper,
                    ratio,
                )

        if upper < lower:
            return None

        start = (
            x1 + lower * dx,
            y1 + lower * dy,
        )
        end = (
            x1 + upper * dx,
            y1 + upper * dy,
        )

        if (
            abs(end[0] - start[0])
            <= tolerance
            and abs(end[1] - start[1])
            <= tolerance
        ):
            return None

        return (
            start,
            end,
        )

    @staticmethod
    def _points_match(
        first,
        second,
        tolerance=1e-9,
    ):
        return (
            abs(
                float(first[0])
                - float(second[0])
            )
            <= tolerance
            and abs(
                float(first[1])
                - float(second[1])
            )
            <= tolerance
        )

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
