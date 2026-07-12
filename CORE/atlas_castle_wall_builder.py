"""
ATLAS Castle Wall Builder v0.2

OSM city_wall / citywalls polyline verisini terrain üzerine oturan,
sürekli, kalın ve yüksek baskıya uygun sur meshlerine dönüştürür.
"""

from CORE.atlas_castle_wall_extruder import (
    AtlasCastleWallExtruder,
)


class AtlasCastleWallBuilder:
    DEFAULT_WALL_WIDTH_M = 4.0
    DEFAULT_WALL_HEIGHT_M = 10.0

    MIN_WALL_WIDTH_MM = 1.20
    MIN_WALL_HEIGHT_MM = 1.80

    @staticmethod
    def build_walls(
        castle_walls,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        accepted = 0
        skipped = 0

        for wall in castle_walls:
            mesh = AtlasCastleWallBuilder._build_wall_mesh(
                wall=wall,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
            )

            if mesh:
                meshes.append(mesh)
                accepted += 1
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS CASTLE WALL BUILDER REPORT")
            print("=" * 60)
            print(f"Input walls      : {len(castle_walls)}")
            print(f"Accepted walls   : {accepted}")
            print(f"Skipped walls    : {skipped}")
            print(f"Wall meshes      : {len(meshes)}")
            print(
                f"Wall triangles   : "
                f"{AtlasCastleWallBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_wall_mesh(
        wall,
        coordinate_engine,
        terrain_mesh,
    ):
        geometry = wall.get("geometry", [])

        if len(geometry) < 2:
            return None

        points = coordinate_engine.geometry_to_stl_mm(geometry)

        metadata = terrain_mesh.get(
            "metadata",
            {},
        )

        legacy_size_mm = float(
            metadata.get(
                "size_mm",
                200.0,
            )
        )

        terrain_size_x_mm = float(
            metadata.get(
                "size_x_mm",
                legacy_size_mm,
            )
        )

        terrain_size_y_mm = float(
            metadata.get(
                "size_y_mm",
                legacy_size_mm,
            )
        )

        points = AtlasCastleWallBuilder._clip_points_to_bounds(
            points=points,
            min_x=0.0,
            max_x=terrain_size_x_mm,
            min_y=0.0,
            max_y=terrain_size_y_mm,
        )

        if len(points) < 2:
            return None

        tags = wall.get("tags", {})

        width_m = AtlasCastleWallBuilder._read_positive_float(
            tags.get("width"),
            AtlasCastleWallBuilder.DEFAULT_WALL_WIDTH_M,
        )

        height_m = AtlasCastleWallBuilder._read_positive_float(
            tags.get("height"),
            AtlasCastleWallBuilder.DEFAULT_WALL_HEIGHT_M,
        )

        width_mm = max(
            coordinate_engine.height_to_stl_mm(width_m),
            AtlasCastleWallBuilder.MIN_WALL_WIDTH_MM,
        )

        height_mm = max(
            coordinate_engine.height_to_stl_mm(height_m),
            AtlasCastleWallBuilder.MIN_WALL_HEIGHT_MM,
        )

        closed = AtlasCastleWallBuilder._is_closed_wall(
            wall=wall,
            points=points,
        )

        mesh = AtlasCastleWallExtruder.build_wall(
            points=points,
            terrain_mesh=terrain_mesh,
            width_mm=width_mm,
            height_mm=height_mm,
            closed=closed,
        )

        if not mesh:
            return None

        mesh.update(
            {
                "type": "castle_wall_foundation",
                "wall_type": wall.get(
                    "wall_type",
                    "city_wall",
                ),
                "source_id": wall.get("id"),
                "placement_mode": "foundation_first",
                "wall_width_mm": width_mm,
                "wall_height_mm": height_mm,
                "relation_role": wall.get("relation_role"),
            }
        )

        return mesh

    @staticmethod
    def _is_closed_wall(wall, points):
        relation_role = wall.get("relation_role")

        if relation_role in {"outer", "inner"}:
            return True

        tags = wall.get("tags", {})

        if tags.get("source") == "castle_relation":
            return True
        if (
            wall.get("inferred") is True
            and wall.get("wall_type") == "inferred_castle_perimeter"
        ):
            return True
        geometry = wall.get("geometry", [])

        if len(geometry) >= 3 and geometry[0] == geometry[-1]:
            return True

        if len(points) >= 3 and points[0] == points[-1]:
            return True

        return False

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
    def _clip_points_to_bounds(
        points,
        min_x,
        max_x,
        min_y,
        max_y,
    ):
        clipped = []

        for x, y in points:
            if min_x <= x <= max_x and min_y <= y <= max_y:
                clipped.append((x, y))

        return clipped

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            total += len(mesh.get("triangles", []))

        return total
