# CORE/atlas_elevated_area_foundation_builder.py

from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_polygon_cleaner import AtlasPolygonCleaner
from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator


class AtlasElevatedAreaFoundationBuilder:
    """
    ATLAS Elevated Area Foundation Builder v0.2

    Görev:
    - Kapalı ve yüksekliği tanımlı yaya alanlarını 3D mesh'e dönüştürmek.
    - Bağımsız alanların alt yüzeyini terrain'e oturtmak.
    - İç içe kademelerde çocuk alanı ebeveynin üst kotundan başlatmak.
    - Üst yüzeyi yatay üretmek.
    - Kapalı ve manifold hacimler oluşturmak.
    """

    MIN_PRINTABLE_THICKNESS_MM = 0.18

    @staticmethod
    def build_areas(
        areas,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        prepared_areas = (
            AtlasElevatedAreaFoundationBuilder
            ._prepare_areas(
                areas=areas,
                coordinate_engine=coordinate_engine,
            )
        )

        meshes = []
        meshes_by_source_id = {}
        accepted = 0
        skipped = 0

        for prepared in prepared_areas:
            parent_mesh = None
            parent_source_id = prepared.get(
                "parent_source_id"
            )

            if parent_source_id is not None:
                parent_mesh = meshes_by_source_id.get(
                    parent_source_id
                )

            mesh = (
                AtlasElevatedAreaFoundationBuilder
                ._build_area_mesh(
                    prepared=prepared,
                    terrain_mesh=terrain_mesh,
                    parent_mesh=parent_mesh,
                )
            )

            if mesh is None:
                skipped += 1
                continue

            meshes.append(mesh)
            meshes_by_source_id[mesh["source_id"]] = mesh
            accepted += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ELEVATED AREA BUILDER REPORT")
            print("=" * 60)
            print(f"Input areas     : {len(areas)}")
            print(f"Accepted areas  : {accepted}")
            print(f"Skipped areas   : {skipped}")
            print(f"Area meshes     : {len(meshes)}")
            print(
                "Triangles       : "
                f"{AtlasElevatedAreaFoundationBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _prepare_areas(
        areas,
        coordinate_engine,
    ):
        prepared = []

        for area in areas:
            geometry = AtlasPolygonCleaner.clean(
                area.get("geometry", [])
            )

            if len(geometry) < 3:
                continue

            points = coordinate_engine.geometry_to_stl_mm(
                geometry
            )

            points = (
                AtlasElevatedAreaFoundationBuilder
                ._remove_closing_point(points)
            )

            if len(points) < 3:
                continue

            try:
                height_m = float(
                    area.get(
                        "height_m",
                        area.get("tags", {}).get("height"),
                    )
                )
            except (TypeError, ValueError):
                continue

            if height_m <= 0.0:
                continue

            height_mm = coordinate_engine.height_to_stl_mm(
                height_m
            )

            prepared.append(
                {
                    "source": area,
                    "source_id": area.get("id"),
                    "points": points,
                    "height_m": height_m,
                    "height_mm": height_mm,
                    "area_abs": abs(
                        AtlasElevatedAreaFoundationBuilder
                        ._signed_area(points)
                    ),
                    "parent_source_id": None,
                }
            )

        for child in prepared:
            child_center = (
                AtlasElevatedAreaFoundationBuilder
                ._polygon_centroid(child["points"])
            )

            parent_candidates = []

            for candidate in prepared:
                if candidate is child:
                    continue

                if candidate["area_abs"] <= child["area_abs"]:
                    continue

                if candidate["height_m"] >= child["height_m"]:
                    continue

                if not AtlasElevatedAreaFoundationBuilder._point_in_polygon(
                    point=child_center,
                    polygon=candidate["points"],
                ):
                    continue

                parent_candidates.append(candidate)

            if parent_candidates:
                parent = min(
                    parent_candidates,
                    key=lambda item: item["area_abs"],
                )

                child["parent_source_id"] = parent[
                    "source_id"
                ]

        prepared.sort(
            key=lambda item: (
                item["height_m"],
                -item["area_abs"],
            )
        )

        return prepared

    @staticmethod
    def _build_area_mesh(
        prepared,
        terrain_mesh,
        parent_mesh=None,
    ):
        points = prepared["points"]

        flat_triangles = AtlasPolygonTriangulator.triangulate(
            points
        )

        if not flat_triangles:
            return None

        terrain_z_values = [
            AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=x,
                y=y,
            )
            for x, y in points
        ]

        if not terrain_z_values:
            return None

        highest_terrain_z = max(terrain_z_values)
        height_mm = prepared["height_mm"]

        if parent_mesh is not None:
            base_mode = "parent_top"
            base_z = parent_mesh["top_z"]

            terrain_reference_mode = "parent_top"
            terrain_reference_z = base_z
            maximum_bottom_z = None

            parent_height_mm = parent_mesh["height_mm"]

            height_increment_mm = max(
                0.0,
                height_mm - parent_height_mm,
            )

            top_z = base_z + height_increment_mm

            bottom_z_values = [
                base_z
                for _point in points
            ]
        else:
            base_mode = "terrain"

            ordered_terrain_z = sorted(
                terrain_z_values
            )

            middle_index = len(
                ordered_terrain_z
            ) // 2

            if len(ordered_terrain_z) % 2 == 0:
                terrain_reference_z = (
                    ordered_terrain_z[
                        middle_index - 1
                    ]
                    + ordered_terrain_z[
                        middle_index
                    ]
                ) * 0.5
            else:
                terrain_reference_z = (
                    ordered_terrain_z[
                        middle_index
                    ]
                )

            terrain_reference_mode = "median"

            printable_height_mm = max(
                height_mm,
                AtlasElevatedAreaFoundationBuilder
                .MIN_PRINTABLE_THICKNESS_MM,
            )

            top_z = (
                terrain_reference_z
                + printable_height_mm
            )

            maximum_bottom_z = (
                top_z
                - AtlasElevatedAreaFoundationBuilder
                .MIN_PRINTABLE_THICKNESS_MM
            )

            bottom_z_values = [
                min(
                    terrain_z,
                    maximum_bottom_z,
                )
                for terrain_z in terrain_z_values
            ]

        printable_height_mm = top_z - min(
            bottom_z_values
        )

        bottom = []
        top = []
        walls = []
        triangles = []

        for (x, y), bottom_z in zip(
            points,
            bottom_z_values,
        ):
            bottom.append(
                (
                    x,
                    y,
                    bottom_z,
                )
            )

            top.append(
                (
                    x,
                    y,
                    top_z,
                )
            )

        for triangle in flat_triangles:
            top_triangle = tuple(
                (
                    x,
                    y,
                    top_z,
                )
                for x, y in triangle
            )

            bottom_triangle = []

            for x, y in triangle:
                if parent_mesh is not None:
                    bottom_z = parent_mesh["top_z"]
                else:
                    sampled_terrain_z = (
                        AtlasFoundationSampler
                        .terrain_z_at_xy(
                            terrain_mesh=terrain_mesh,
                            x=x,
                            y=y,
                        )
                    )

                    bottom_z = min(
                        sampled_terrain_z,
                        maximum_bottom_z,
                    )

                bottom_triangle.append(
                    (
                        x,
                        y,
                        bottom_z,
                    )
                )

            triangles.append(top_triangle)

            triangles.append(
                (
                    bottom_triangle[2],
                    bottom_triangle[1],
                    bottom_triangle[0],
                )
            )

        point_count = len(points)

        for index in range(point_count):
            next_index = (
                index + 1
            ) % point_count

            b1 = bottom[index]
            b2 = bottom[next_index]
            t1 = top[index]
            t2 = top[next_index]

            walls.append(
                (
                    b1,
                    b2,
                    t2,
                    t1,
                )
            )

            triangles.append(
                (
                    b1,
                    b2,
                    t2,
                )
            )

            triangles.append(
                (
                    b1,
                    t2,
                    t1,
                )
            )

        shared_parent_edge_indices = []
        new_step_edge_indices = []

        if parent_mesh is not None:
            parent_points = [
                (
                    float(point[0]),
                    float(point[1]),
                )
                for point in parent_mesh.get(
                    "bottom",
                    [],
                )
            ]

            for edge_index in range(point_count):
                next_index = (
                    edge_index + 1
                ) % point_count

                edge_start = points[edge_index]
                edge_end = points[next_index]

                is_shared = (
                    AtlasElevatedAreaFoundationBuilder
                    ._edge_lies_on_polygon_boundary(
                        edge_start=edge_start,
                        edge_end=edge_end,
                        polygon=parent_points,
                    )
                )

                if is_shared:
                    shared_parent_edge_indices.append(
                        edge_index
                    )
                else:
                    new_step_edge_indices.append(
                        edge_index
                    )
        else:
            new_step_edge_indices = list(
                range(point_count)
            )

        source = prepared["source"]

        mesh = {
            "type": "elevated_area_foundation",
            "source_id": prepared["source_id"],
            "parent_source_id": prepared[
                "parent_source_id"
            ],
            "base_mode": base_mode,
            "area_type": source.get(
                "area_type",
                "elevated_pedestrian_area",
            ),
            "height_m": prepared["height_m"],
            "height_mm": height_mm,
            "printable_height_mm": printable_height_mm,
            "highest_terrain_z": highest_terrain_z,
            "terrain_reference_mode": (
                terrain_reference_mode
            ),
            "terrain_reference_z": (
                terrain_reference_z
            ),
            "top_z": top_z,
            "shared_parent_edge_count": len(
                shared_parent_edge_indices
            ),
            "new_step_edge_count": len(
                new_step_edge_indices
            ),
            "shared_parent_edge_indices": (
                shared_parent_edge_indices
            ),
            "new_step_edge_indices": (
                new_step_edge_indices
            ),
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "placement_mode": "foundation_first",
        }

        report = AtlasMeshValidator.report(mesh)

        if not report["valid"]:
            return None

        return mesh

    @staticmethod
    def _edge_lies_on_polygon_boundary(
        edge_start,
        edge_end,
        polygon,
        tolerance=1e-7,
    ):
        if len(polygon) < 2:
            return False

        for index in range(len(polygon)):
            parent_start = polygon[index]
            parent_end = polygon[
                (index + 1) % len(polygon)
            ]

            if (
                AtlasElevatedAreaFoundationBuilder
                ._point_lies_on_segment(
                    point=edge_start,
                    segment_start=parent_start,
                    segment_end=parent_end,
                    tolerance=tolerance,
                )
                and
                AtlasElevatedAreaFoundationBuilder
                ._point_lies_on_segment(
                    point=edge_end,
                    segment_start=parent_start,
                    segment_end=parent_end,
                    tolerance=tolerance,
                )
            ):
                return True

        return False

    @staticmethod
    def _point_lies_on_segment(
        point,
        segment_start,
        segment_end,
        tolerance=1e-7,
    ):
        px, py = point
        ax, ay = segment_start
        bx, by = segment_end

        segment_x = bx - ax
        segment_y = by - ay

        point_x = px - ax
        point_y = py - ay

        cross = (
            segment_x * point_y
            - segment_y * point_x
        )

        segment_length = (
            segment_x ** 2
            + segment_y ** 2
        ) ** 0.5

        if segment_length <= tolerance:
            return (
                (
                    (px - ax) ** 2
                    + (py - ay) ** 2
                ) ** 0.5
                <= tolerance
            )

        if abs(cross) > (
            tolerance * segment_length
        ):
            return False

        dot = (
            point_x * segment_x
            + point_y * segment_y
        )

        if dot < -tolerance:
            return False

        squared_length = (
            segment_x ** 2
            + segment_y ** 2
        )

        if dot > squared_length + tolerance:
            return False

        return True

    @staticmethod
    def _signed_area(points):
        area = 0.0

        for index in range(len(points)):
            x1, y1 = points[index]
            x2, y2 = points[
                (index + 1) % len(points)
            ]

            area += x1 * y2 - x2 * y1

        return area * 0.5

    @staticmethod
    def _polygon_centroid(points):
        area_factor = 0.0
        centroid_x = 0.0
        centroid_y = 0.0

        for index in range(len(points)):
            x1, y1 = points[index]
            x2, y2 = points[
                (index + 1) % len(points)
            ]

            cross = x1 * y2 - x2 * y1
            area_factor += cross
            centroid_x += (x1 + x2) * cross
            centroid_y += (y1 + y2) * cross

        if abs(area_factor) <= 1e-12:
            return (
                sum(point[0] for point in points)
                / len(points),
                sum(point[1] for point in points)
                / len(points),
            )

        return (
            centroid_x / (3.0 * area_factor),
            centroid_y / (3.0 * area_factor),
        )

    @staticmethod
    def _point_in_polygon(
        point,
        polygon,
    ):
        x, y = point
        inside = False
        previous_index = len(polygon) - 1

        for index in range(len(polygon)):
            x1, y1 = polygon[index]
            x2, y2 = polygon[previous_index]

            crosses = (
                (y1 > y) != (y2 > y)
                and x
                < (
                    (x2 - x1)
                    * (y - y1)
                    / ((y2 - y1) or 1e-15)
                    + x1
                )
            )

            if crosses:
                inside = not inside

            previous_index = index

        return inside

    @staticmethod
    def _remove_closing_point(points):
        points = list(points)

        if (
            len(points) >= 2
            and points[0] == points[-1]
        ):
            points.pop()

        return points

    @staticmethod
    def _count_triangles(meshes):
        return sum(
            len(mesh.get("triangles", []))
            for mesh in meshes
            if isinstance(mesh, dict)
        )
