"""
ATLAS Castle Tower Cap Builder v0.3

v0.2:
- Kule alt yüzeyi yerel terrain + shell yüksekliğini takip eder
- Kule üst yüzeyi düz kalır
- Yan duvarlar triangulation sınır kenarlarından üretilir
- Kollinear sınır noktalarından kaynaklanan open-edge hataları önlenir

v0.3 diagnostic:
- Straight-chord + raw-region birleşimindeki tekrar eden boundary noktalarını raporlar
- Teşhis bloğu yalnız _extrude_region() içinde, ringler oluşturulduktan sonra çalışır

Amaç:
- Ana shell eşit sur yüksekliğinde kalır
- Kule bölgeleri ayrı cap meshleri olarak yükseltilir
- Surdan kuleye çapraz rampa oluşmaz
- Kule tepeleri düz olur
"""

import math
from collections import defaultdict, deque

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from CORE.atlas_castle_shell_triangulator import AtlasCastleShellTriangulator
from CORE.atlas_castle_shell_height_profiler import AtlasCastleShellHeightProfiler
from CORE.atlas_foundation_sampler import AtlasFoundationSampler


class AtlasCastleTowerCapBuilder:
    BUFFER_PERCENTILE = 0.75
    BUFFER_FACTOR = 0.90

    POINT_PRECISION = 9
    EPSILON = 1e-9
    AREA_TOLERANCE = 1e-8

    THICKNESS_PERCENTILE = 0.75
    INFLUENCE_FACTOR = 0.50

    MIN_CLIPPED_AREA_MM2 = 0.005
    MIN_OVERLAP_RATIO = 0.025
    MAX_REGION_DISTANCE_MM = 0.02
    MAX_GROWTH_ROUNDS = 4
    COLLINEAR_TOLERANCE = 1e-7

    @staticmethod
    def build_caps(castles, coordinate_engine, terrain_mesh, debug=True):
        meshes = []
        accepted_castles = 0
        skipped_castles = 0
        cap_regions = 0

        for castle in castles:
            if castle.get("geometry_type") != "relation":
                skipped_castles += 1
                continue

            castle_meshes = AtlasCastleTowerCapBuilder._build_castle_caps(
                castle=castle,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
            )

            if castle_meshes:
                meshes.extend(castle_meshes)
                accepted_castles += 1
                cap_regions += len(castle_meshes)
            else:
                skipped_castles += 1

        if debug:
            print("")
            print("=" * 64)
            print("ATLAS CASTLE TOWER CAP BUILDER REPORT")
            print("=" * 64)
            print(f"Input castles       : {len(castles)}")
            print(f"Accepted castles    : {accepted_castles}")
            print(f"Skipped castles     : {skipped_castles}")
            print(f"Tower cap regions   : {cap_regions}")
            print(f"Tower cap meshes    : {len(meshes)}")
            print(
                f"Tower cap triangles : "
                f"{AtlasCastleTowerCapBuilder._count_triangles(meshes)}"
            )
            print("=" * 64)
            print("")

        return meshes

    @staticmethod
    def _build_castle_caps(castle, coordinate_engine, terrain_mesh):
        outer_geometries = castle.get("outer_geometries", [])
        inner_geometries = castle.get("inner_geometries", [])

        if not outer_geometries:
            return []

        converted_outer_rings = [
            coordinate_engine.geometry_to_stl_mm(geometry)
            for geometry in outer_geometries
            if len(geometry) >= 3
        ]

        converted_inner_rings = [
            coordinate_engine.geometry_to_stl_mm(geometry)
            for geometry in inner_geometries
            if len(geometry) >= 3
        ]

        if not converted_outer_rings:
            return []

        primary_outer = converted_outer_rings[0]
        candidate_inner_rings = converted_outer_rings[1:] + converted_inner_rings

        normalized = AtlasCastleShellTriangulator.normalize_rings(
            outer_ring=primary_outer,
            inner_rings=candidate_inner_rings,
        )

        outer_ring = normalized.get("outer_ring", [])
        inner_rings = normalized.get("inner_rings", [])

        if len(outer_ring) < 3 or not inner_rings:
            return []

        profile = AtlasCastleShellHeightProfiler.build_profile(
            outer_ring=outer_ring,
            inner_rings=inner_rings,
        )

        shell_polygon = Polygon(shell=outer_ring, holes=inner_rings)

        if (
            shell_polygon.is_empty
            or not shell_polygon.is_valid
            or shell_polygon.area <= AtlasCastleTowerCapBuilder.EPSILON
        ):
            return []

        tags = castle.get("tags", {})

        shell_height_m = AtlasCastleTowerCapBuilder._read_positive_float(
            tags.get("height"),
            10.0,
        )

        shell_height_mm = max(
            coordinate_engine.height_to_stl_mm(shell_height_m),
            1.80,
        )

        tower_height_mm = (
            shell_height_mm * AtlasCastleShellHeightProfiler.TOWER_HEIGHT_MULTIPLIER
        )
        cap_extra_height_mm = tower_height_mm - shell_height_mm

        if cap_extra_height_mm <= 0:
            return []

        meshes = []

        for run_index, run in enumerate(profile.get("tower_runs", []), start=1):
            region = AtlasCastleTowerCapBuilder._build_run_region(
                run_index=run_index,
                run=run,
                outer_ring=outer_ring,
                profile=profile,
                shell_polygon=shell_polygon,
            )

            if region is None:
                continue

            mesh = AtlasCastleTowerCapBuilder._extrude_region(
                region=region,
                terrain_mesh=terrain_mesh,
                shell_height_mm=shell_height_mm,
                cap_extra_height_mm=cap_extra_height_mm,
                castle=castle,
                run_index=run_index,
            )

            if mesh:
                meshes.append(mesh)

        return meshes

    @staticmethod
    def _build_run_region(run_index, run, outer_ring, profile, shell_polygon):
        if (
            shell_polygon is None
            or shell_polygon.is_empty
            or not shell_polygon.is_valid
            or shell_polygon.area <= AtlasCastleTowerCapBuilder.EPSILON
        ):
            return None

        inner_rings = [
            [(float(x), float(y)) for x, y in list(interior.coords)[:-1]]
            for interior in shell_polygon.interiors
        ]

        flat_triangles = AtlasCastleShellTriangulator.triangulate(
            outer_ring=outer_ring,
            inner_rings=inner_rings,
        )

        if not flat_triangles:
            return None

        point_to_run = {}
        run_indices = {}

        for current_run_index, (start, end, _length) in enumerate(
            profile.get("tower_runs", []),
            start=1,
        ):
            indices = []
            current = start

            while True:
                indices.append(current)
                point_to_run[
                    AtlasCastleTowerCapBuilder._point_key(outer_ring[current])
                ] = current_run_index

                if current == end:
                    break

                current = (current + 1) % len(outer_ring)

            run_indices[current_run_index] = indices

        if run_index not in run_indices:
            return None

        records = []

        for triangle_index, triangle in enumerate(flat_triangles):
            votes = []

            for point in triangle:
                detected_run = point_to_run.get(
                    AtlasCastleTowerCapBuilder._point_key(point)
                )
                if detected_run is not None:
                    votes.append(detected_run)

            unique_runs = set(votes)

            if len(unique_runs) > 1:
                category = "cross_run"
                detected_run = None
            elif len(votes) == 3:
                category = "pure"
                detected_run = votes[0]
            elif len(votes) == 2:
                category = "mixed_2"
                detected_run = votes[0]
            elif len(votes) == 1:
                category = "mixed_1"
                detected_run = votes[0]
            else:
                category = "wall"
                detected_run = None

            polygon = Polygon(triangle)

            if (
                polygon.is_empty
                or not polygon.is_valid
                or polygon.area <= AtlasCastleTowerCapBuilder.EPSILON
            ):
                continue

            records.append(
                {
                    "index": triangle_index,
                    "polygon": polygon,
                    "category": category,
                    "run_index": detected_run,
                    "edge_keys": {
                        AtlasCastleTowerCapBuilder._edge_key(a, b)
                        for a, b in AtlasCastleTowerCapBuilder._triangle_edges(triangle)
                    },
                }
            )

        if not records:
            return None

        record_by_index = {record["index"]: record for record in records}
        edge_to_triangles = defaultdict(list)

        for record in records:
            for current_edge in record["edge_keys"]:
                edge_to_triangles[current_edge].append(record["index"])

        adjacency = defaultdict(set)

        for triangle_indices in edge_to_triangles.values():
            if len(triangle_indices) != 2:
                continue

            first_index, second_index = triangle_indices
            adjacency[first_index].add(second_index)
            adjacency[second_index].add(first_index)

        seed_indices = {
            record["index"]
            for record in records
            if (
                record["run_index"] == run_index
                and record["category"] in {"pure", "mixed_2"}
            )
        }

        if not seed_indices:
            return None

        seed_components = AtlasCastleTowerCapBuilder._connected_components(
            triangle_indices=seed_indices,
            adjacency=adjacency,
        )

        seed_components.sort(
            key=lambda component: sum(
                record_by_index[index]["polygon"].area for index in component
            ),
            reverse=True,
        )

        active_triangle_indices = set(seed_components[0])
        core_union = unary_union(
            [record_by_index[index]["polygon"] for index in active_triangle_indices]
        )
        core_region = AtlasCastleTowerCapBuilder._largest_polygon(core_union)

        if core_region is None:
            return None

        indices = run_indices[run_index]
        run_points = [outer_ring[index] for index in indices]
        run_thicknesses = [profile["smoothed_thicknesses"][index] for index in indices]

        base_thickness = AtlasCastleTowerCapBuilder._percentile(
            values=run_thicknesses,
            percentile=AtlasCastleTowerCapBuilder.THICKNESS_PERCENTILE,
        )

        influence_distance = (
            base_thickness * AtlasCastleTowerCapBuilder.INFLUENCE_FACTOR
        )

        influence_zone_raw = (
            LineString(run_points)
            .buffer(influence_distance, cap_style=2, join_style=2)
            .intersection(shell_polygon)
        )

        influence_zone = AtlasCastleTowerCapBuilder._largest_polygon(influence_zone_raw)

        if influence_zone is None:
            return None

        current_region = core_region
        accepted_parts = []
        processed_candidates = set()

        for _growth_round in range(
            1,
            AtlasCastleTowerCapBuilder.MAX_GROWTH_ROUNDS + 1,
        ):
            candidate_indices = set()

            for active_index in active_triangle_indices:
                for neighbor_index in adjacency[active_index]:
                    if neighbor_index in active_triangle_indices:
                        continue
                    if neighbor_index in processed_candidates:
                        continue
                    candidate_indices.add(neighbor_index)

            round_accepted = 0

            for candidate_index in sorted(candidate_indices):
                processed_candidates.add(candidate_index)
                candidate = record_by_index.get(candidate_index)

                if candidate is None:
                    continue
                if candidate["category"] == "cross_run":
                    continue
                if (
                    candidate["run_index"] is not None
                    and candidate["run_index"] != run_index
                ):
                    continue

                polygon = candidate["polygon"]
                clipped = polygon.intersection(influence_zone)
                clipped_polygon = AtlasCastleTowerCapBuilder._largest_polygon(clipped)

                if clipped_polygon is None:
                    continue

                clipped_area = clipped_polygon.area
                overlap_ratio = clipped_area / max(
                    polygon.area,
                    AtlasCastleTowerCapBuilder.EPSILON,
                )
                distance_to_region = clipped_polygon.distance(current_region)

                area_ok = (
                    clipped_area >= AtlasCastleTowerCapBuilder.MIN_CLIPPED_AREA_MM2
                )
                ratio_ok = overlap_ratio >= AtlasCastleTowerCapBuilder.MIN_OVERLAP_RATIO
                touches_region = (
                    distance_to_region
                    <= AtlasCastleTowerCapBuilder.MAX_REGION_DISTANCE_MM
                )

                if not (area_ok and ratio_ok and touches_region):
                    continue

                active_triangle_indices.add(candidate_index)
                accepted_parts.append(clipped_polygon)

                current_region = AtlasCastleTowerCapBuilder._largest_polygon(
                    unary_union([core_region, *accepted_parts])
                )

                if current_region is None:
                    return None

                round_accepted += 1

            if round_accepted == 0:
                break

        raw_region = AtlasCastleTowerCapBuilder._repair_polygon(current_region)

        if raw_region is None:
            return None

        chord_fill = AtlasCastleTowerCapBuilder._repair_polygon(
            Polygon([(float(point[0]), float(point[1])) for point in run_points])
        )

        if chord_fill is not None:
            chord_fill = AtlasCastleTowerCapBuilder._repair_polygon(
                chord_fill.intersection(shell_polygon)
            )

        chord_region = AtlasCastleTowerCapBuilder._union_preserving_raw(
            raw_region=raw_region,
            reconstruction_polygon=chord_fill,
        )

        if chord_region is None:
            return raw_region

        clipped_chord_region = chord_region.intersection(shell_polygon)
        final_region = AtlasCastleTowerCapBuilder._polygon_preserving_reference(
            geometry=clipped_chord_region,
            reference_polygon=raw_region,
        )

        if final_region is None:
            return raw_region

        return final_region

    @staticmethod
    def _point_key(point):
        return (
            round(float(point[0]), AtlasCastleTowerCapBuilder.POINT_PRECISION),
            round(float(point[1]), AtlasCastleTowerCapBuilder.POINT_PRECISION),
        )

    @staticmethod
    def _edge_key(point_1, point_2):
        return tuple(
            sorted(
                (
                    AtlasCastleTowerCapBuilder._point_key(point_1),
                    AtlasCastleTowerCapBuilder._point_key(point_2),
                )
            )
        )

    @staticmethod
    def _triangle_edges(triangle):
        return (
            (triangle[0], triangle[1]),
            (triangle[1], triangle[2]),
            (triangle[2], triangle[0]),
        )

    @staticmethod
    def _connected_components(triangle_indices, adjacency):
        remaining = set(triangle_indices)
        components = []

        while remaining:
            start = next(iter(remaining))
            queue = deque([start])
            remaining.remove(start)
            component = []

            while queue:
                current = queue.popleft()
                component.append(current)

                for neighbor in adjacency[current]:
                    if neighbor not in remaining:
                        continue
                    remaining.remove(neighbor)
                    queue.append(neighbor)

            components.append(component)

        return components

    @staticmethod
    def _geometry_components(geometry):
        if geometry is None or geometry.is_empty:
            return []
        if geometry.geom_type == "Polygon":
            return [geometry]
        if geometry.geom_type == "MultiPolygon":
            return list(geometry.geoms)
        return [
            item
            for item in getattr(geometry, "geoms", [])
            if item.geom_type == "Polygon"
        ]

    @staticmethod
    def _polygon_preserving_reference(geometry, reference_polygon):
        if geometry is None or geometry.is_empty:
            return None

        repaired = geometry
        if not repaired.is_valid:
            repaired = repaired.buffer(0)

        components = AtlasCastleTowerCapBuilder._geometry_components(repaired)

        if not components:
            return None
        if len(components) == 1:
            return components[0]

        return max(
            components,
            key=lambda component: (
                component.intersection(reference_polygon).area,
                component.area,
            ),
        )

    @staticmethod
    def _repair_polygon(geometry):
        if geometry is None or geometry.is_empty:
            return None

        repaired = geometry
        if not repaired.is_valid:
            repaired = repaired.buffer(0)

        polygon = AtlasCastleTowerCapBuilder._largest_polygon(repaired)

        if (
            polygon is None
            or polygon.is_empty
            or polygon.area <= AtlasCastleTowerCapBuilder.EPSILON
        ):
            return None

        return polygon

    @staticmethod
    def _union_preserving_raw(raw_region, reconstruction_polygon):
        if reconstruction_polygon is None:
            return raw_region

        merged = unary_union([raw_region, reconstruction_polygon])
        preserved = AtlasCastleTowerCapBuilder._polygon_preserving_reference(
            geometry=merged,
            reference_polygon=raw_region,
        )

        if preserved is None:
            return raw_region

        raw_missing_area = raw_region.difference(preserved).area

        if raw_missing_area > AtlasCastleTowerCapBuilder.AREA_TOLERANCE:
            merged_again = unary_union([preserved, raw_region])
            preserved_again = AtlasCastleTowerCapBuilder._polygon_preserving_reference(
                geometry=merged_again,
                reference_polygon=raw_region,
            )

            if preserved_again is not None:
                preserved = preserved_again

        return preserved

    @staticmethod
    def _point_on_segment(
        point,
        start,
        end,
        tolerance,
    ):
        direction_x = float(end[0]) - float(start[0])
        direction_y = float(end[1]) - float(start[1])

        length_squared = direction_x * direction_x + direction_y * direction_y

        if length_squared <= AtlasCastleTowerCapBuilder.EPSILON:
            return False

        relative_x = float(point[0]) - float(start[0])
        relative_y = float(point[1]) - float(start[1])

        cross = abs(direction_x * relative_y - direction_y * relative_x)

        segment_length = math.sqrt(length_squared)

        if cross > tolerance * segment_length:
            return False

        parameter = (
            relative_x * direction_x + relative_y * direction_y
        ) / length_squared

        return tolerance < parameter < 1.0 - tolerance

    @staticmethod
    def _remove_collinear_ring_points(
        ring,
    ):
        clean = [
            (
                float(point[0]),
                float(point[1]),
            )
            for point in ring
        ]

        if len(clean) < 4:
            return clean

        tolerance = AtlasCastleTowerCapBuilder.COLLINEAR_TOLERANCE

        changed = True

        while changed and len(clean) >= 4:
            changed = False
            result = []

            point_count = len(clean)

            for index in range(point_count):
                previous_point = clean[(index - 1) % point_count]

                current_point = clean[index]

                next_point = clean[(index + 1) % point_count]

                if AtlasCastleTowerCapBuilder._point_on_segment(
                    point=current_point,
                    start=previous_point,
                    end=next_point,
                    tolerance=tolerance,
                ):
                    changed = True
                    continue

                result.append(current_point)

            if len(result) < 3:
                break

            clean = result

        return clean

    @staticmethod
    def _extrude_region(
        region,
        terrain_mesh,
        shell_height_mm,
        cap_extra_height_mm,
        castle,
        run_index,
    ):
        if (
            region is None
            or region.is_empty
            or not region.is_valid
            or region.area <= AtlasCastleTowerCapBuilder.EPSILON
        ):
            return None

        outer_ring = AtlasCastleTowerCapBuilder._remove_collinear_ring_points(
            [(float(x), float(y)) for x, y in list(region.exterior.coords)[:-1]]
        )

        inner_rings = [
            AtlasCastleTowerCapBuilder._remove_collinear_ring_points(
                [(float(x), float(y)) for x, y in list(interior.coords)[:-1]]
            )
            for interior in region.interiors
        ]

        inner_rings = [ring for ring in inner_rings if len(ring) >= 3]

        boundary_occurrences = defaultdict(list)
        diagnostic_rings = [
            ("outer", outer_ring),
            *[
                (f"inner_{index}", ring)
                for index, ring in enumerate(inner_rings, start=1)
            ],
        ]

        for ring_name, ring in diagnostic_rings:
            point_count = len(ring)
            if point_count == 0:
                continue

            for point_index, point in enumerate(ring):
                previous_point = ring[(point_index - 1) % point_count]
                next_point = ring[(point_index + 1) % point_count]
                key = (
                    round(
                        float(point[0]),
                        AtlasCastleTowerCapBuilder.POINT_PRECISION,
                    ),
                    round(
                        float(point[1]),
                        AtlasCastleTowerCapBuilder.POINT_PRECISION,
                    ),
                )

                boundary_occurrences[key].append(
                    {
                        "ring": ring_name,
                        "index": point_index,
                        "previous": previous_point,
                        "current": point,
                        "next": next_point,
                    }
                )

        repeated_boundary_points = {
            key: occurrences
            for key, occurrences in boundary_occurrences.items()
            if len(occurrences) > 1
        }

        if repeated_boundary_points:
            print("")
            print(f"TOWER RUN {run_index} REPEATED BOUNDARY POINTS")

            for key, occurrences in repeated_boundary_points.items():
                print(f"Point {key} occurrences={len(occurrences)}")

                for occurrence in occurrences:
                    print(
                        f"  ring={occurrence['ring']} "
                        f"index={occurrence['index']} "
                        f"previous={occurrence['previous']} "
                        f"next={occurrence['next']}"
                    )

        flat_triangles = AtlasCastleShellTriangulator.triangulate(
            outer_ring=outer_ring,
            inner_rings=inner_rings,
        )

        if not flat_triangles:
            return None

        oriented_flat_triangles = []

        for flat_triangle in flat_triangles:
            p1, p2, p3 = flat_triangle

            if AtlasCastleTowerCapBuilder._triangle_signed_area(flat_triangle) < 0.0:
                p2, p3 = p3, p2

            oriented_flat_triangles.append((p1, p2, p3))

        bottom_z_cache = {}

        def local_bottom_z(point):
            key = (
                round(
                    float(point[0]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
                round(
                    float(point[1]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
            )

            cached = bottom_z_cache.get(key)
            if cached is not None:
                return cached

            terrain_z = AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=float(point[0]),
                y=float(point[1]),
            )
            value = terrain_z + shell_height_mm
            bottom_z_cache[key] = value
            return value

        all_points = list(outer_ring)
        for inner_ring in inner_rings:
            all_points.extend(inner_ring)

        if not all_points:
            return None

        local_bottom_values = [local_bottom_z(point) for point in all_points]
        minimum_bottom_z = min(local_bottom_values)
        maximum_bottom_z = max(local_bottom_values)
        cap_top_z = maximum_bottom_z + cap_extra_height_mm

        triangles = []

        for flat_triangle in oriented_flat_triangles:
            p1, p2, p3 = flat_triangle

            b1 = (p1[0], p1[1], local_bottom_z(p1))
            b2 = (p2[0], p2[1], local_bottom_z(p2))
            b3 = (p3[0], p3[1], local_bottom_z(p3))

            t1 = (p1[0], p1[1], cap_top_z)
            t2 = (p2[0], p2[1], cap_top_z)
            t3 = (p3[0], p3[1], cap_top_z)

            triangles.append((t1, t2, t3))
            triangles.append((b3, b2, b1))

        boundary_edges = AtlasCastleTowerCapBuilder._extract_directed_boundary_edges(
            oriented_flat_triangles
        )
        boundary_degree = defaultdict(list)

        for edge_index, (start, end) in enumerate(boundary_edges):
            start_key = (
                round(
                    float(start[0]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
                round(
                    float(start[1]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
            )

            end_key = (
                round(
                    float(end[0]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
                round(
                    float(end[1]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
            )

            boundary_degree[start_key].append(
                {
                    "edge_index": edge_index,
                    "role": "start",
                    "other": end,
                }
            )

            boundary_degree[end_key].append(
                {
                    "edge_index": edge_index,
                    "role": "end",
                    "other": start,
                }
            )

        abnormal_boundary_vertices = {
            key: incidents
            for key, incidents in boundary_degree.items()
            if len(incidents) != 2
        }

        if abnormal_boundary_vertices:
            print("")
            print(f"TOWER RUN {run_index} " f"ABNORMAL BOUNDARY DEGREE")

            for key, incidents in abnormal_boundary_vertices.items():
                print(f"Point {key} " f"degree={len(incidents)}")

            for incident in incidents:
                print(
                    f"  edge={incident['edge_index']} "
                    f"role={incident['role']} "
                    f"other={incident['other']}"
                )
            polygon_rings = [
                (
                    "outer",
                    list(region.exterior.coords)[:-1],
                )
            ]

            polygon_rings.extend(
                (
                    f"inner_{inner_index}",
                    list(interior.coords)[:-1],
                )
                for inner_index, interior in enumerate(
                    region.interiors,
                    start=1,
                )
            )

            for ring_name, ring_points in polygon_rings:
                matching_indices = []

                for point_index, point in enumerate(ring_points):
                    point_key = (
                        round(
                            float(point[0]),
                            AtlasCastleTowerCapBuilder.POINT_PRECISION,
                        ),
                        round(
                            float(point[1]),
                            AtlasCastleTowerCapBuilder.POINT_PRECISION,
                        ),
                    )

                    if point_key == key:
                        matching_indices.append(point_index)

                print(f"  {ring_name} occurrences=" f"{len(matching_indices)}")

                for point_index in matching_indices:
                    previous_point = ring_points[(point_index - 1) % len(ring_points)]

                    current_point = ring_points[point_index]

                    next_point = ring_points[(point_index + 1) % len(ring_points)]

                    print(f"    index={point_index}")
                    print(f"    previous={previous_point}")
                    print(f"    current={current_point}")
                    print(f"    next={next_point}")

            print(f"  region geom_type=" f"{region.geom_type}")
            print(f"  region valid=" f"{region.is_valid}")
            print(f"  boundary simple=" f"{region.boundary.is_simple}")
        walls = []
        AtlasCastleTowerCapBuilder._add_boundary_walls(
            boundary_edges=boundary_edges,
            local_bottom_z=local_bottom_z,
            top_z=cap_top_z,
            triangles=triangles,
            walls=walls,
        )

        return {
            "type": "castle_tower_cap",
            "source_id": castle.get("id"),
            "name": castle.get("tags", {}).get("name"),
            "run_index": run_index,
            "bottom_z": maximum_bottom_z,
            "minimum_bottom_z": minimum_bottom_z,
            "maximum_bottom_z": maximum_bottom_z,
            "bottom_z_range_mm": maximum_bottom_z - minimum_bottom_z,
            "top_z": cap_top_z,
            "cap_extra_height_mm": cap_extra_height_mm,
            "area_mm2": region.area,
            "bottom": [],
            "top": [],
            "walls": walls,
            "triangles": triangles,
            "placement_mode": "foundation_first_local_z",
        }

    @staticmethod
    def _extract_directed_boundary_edges(
        flat_triangles,
    ):
        """
        Triangulation içinde yalnız bir üçgen tarafından kullanılan
        sınır kenarlarını yönleriyle birlikte döndürür.
        """
        edge_records = {}

        def point_key(point):
            return (
                round(
                    float(point[0]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
                round(
                    float(point[1]),
                    AtlasCastleTowerCapBuilder.POINT_PRECISION,
                ),
            )

        for triangle in flat_triangles:
            p1, p2, p3 = triangle

            directed_edges = (
                (p1, p2),
                (p2, p3),
                (p3, p1),
            )

            for start, end in directed_edges:
                start_key = point_key(start)
                end_key = point_key(end)

                undirected_key = tuple(
                    sorted(
                        (
                            start_key,
                            end_key,
                        )
                    )
                )

                record = edge_records.get(undirected_key)

                if record is None:
                    edge_records[undirected_key] = {
                        "count": 1,
                        "start": (
                            float(start[0]),
                            float(start[1]),
                        ),
                        "end": (
                            float(end[0]),
                            float(end[1]),
                        ),
                    }
                else:
                    record["count"] += 1

        boundary_edges = [
            (
                record["start"],
                record["end"],
            )
            for record in edge_records.values()
            if record["count"] == 1
        ]

        return boundary_edges

    @staticmethod
    def _add_boundary_walls(
        boundary_edges,
        local_bottom_z,
        top_z,
        triangles,
        walls,
    ):
        for p1, p2 in boundary_edges:
            b1 = (p1[0], p1[1], local_bottom_z(p1))
            b2 = (p2[0], p2[1], local_bottom_z(p2))
            t1 = (p1[0], p1[1], top_z)
            t2 = (p2[0], p2[1], top_z)

            triangles.append((b1, b2, t2))
            triangles.append((b1, t2, t1))
            walls.append((b1, b2, t2, t1))

    @staticmethod
    def _largest_polygon(geometry):
        if geometry is None or geometry.is_empty:
            return None

        if geometry.geom_type == "Polygon":
            return geometry

        if geometry.geom_type == "MultiPolygon":
            polygons = list(geometry.geoms)
            if not polygons:
                return None
            return max(polygons, key=lambda item: item.area)

        polygons = [
            item
            for item in getattr(geometry, "geoms", [])
            if item.geom_type == "Polygon"
        ]

        if not polygons:
            return None

        return max(polygons, key=lambda item: item.area)

    @staticmethod
    def _percentile(values, percentile):
        ordered = sorted(values)

        if not ordered:
            return 0.0

        position = percentile * (len(ordered) - 1)
        lower = int(math.floor(position))
        upper = int(math.ceil(position))

        if lower == upper:
            return ordered[lower]

        fraction = position - lower
        return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction

    @staticmethod
    def _triangle_signed_area(triangle):
        p1, p2, p3 = triangle
        return (
            p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])
        ) / 2.0

    @staticmethod
    def _read_positive_float(value, default):
        try:
            parsed = float(value)
            if parsed > 0:
                return parsed
        except (TypeError, ValueError):
            pass
        return default

    @staticmethod
    def _count_triangles(meshes):
        return sum(len(mesh.get("triangles", [])) for mesh in meshes)
