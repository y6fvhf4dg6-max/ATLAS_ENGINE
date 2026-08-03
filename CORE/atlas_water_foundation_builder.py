"""
ATLAS Water Foundation Builder v0.1

Kapalı OSM su polygonlarını ve coastline verisinden oluşturulan
deniz polygonlarını yatay, ince ve yazdırılabilir meshler hâline getirir.

Temel kural:

- Park ve arazi terrain eğimini takip eder.
- Deniz, göl ve geniş su yüzeyleri yatay kalır.
- Coastline su kotu, DEM'deki 0 metre deniz seviyesinden hesaplanır.
"""

from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)
from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


class AtlasWaterFoundationBuilder:
    VERSION = "0.1"

    WATER_HEIGHT_MM = 0.10
    POINT_PRECISION = 9

    @staticmethod
    def build_coastline_water_meshes(
        water_polygons,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        skipped = 0

        for index, polygon in enumerate(
            water_polygons or [],
            start=1,
        ):
            mesh = (
                AtlasWaterFoundationBuilder
                ._build_coastline_water_mesh(
                    polygon=polygon,
                    coordinate_engine=coordinate_engine,
                    terrain_mesh=terrain_mesh,
                    source_index=index,
                )
            )

            if mesh is None:
                skipped += 1
                continue

            meshes.append(mesh)

        if debug:
            print("")
            print("=" * 70)
            print(
                "ATLAS WATER FOUNDATION BUILDER "
                f"v{AtlasWaterFoundationBuilder.VERSION}"
            )
            print("=" * 70)
            print(
                f"Input water polygons : "
                f"{len(water_polygons or [])}"
            )
            print(
                f"Accepted polygons    : "
                f"{len(meshes)}"
            )
            print(
                f"Skipped polygons     : "
                f"{skipped}"
            )
            print(
                f"Water meshes         : "
                f"{len(meshes)}"
            )

            for index, mesh in enumerate(
                meshes,
                start=1,
            ):
                print(
                    f"Water mesh {index} "
                    f"surface Z      : "
                    f"{mesh['water_surface_z']:.6f} mm"
                )
                print(
                    f"Water mesh {index} "
                    f"triangles      : "
                    f"{len(mesh['triangles'])}"
                )

            print("=" * 70)
            print("")

        return meshes

    @staticmethod
    def build_inland_water_meshes(
        water_polygons,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        skipped = 0

        for index, polygon in enumerate(
            water_polygons or [],
            start=1,
        ):
            mesh = (
                AtlasWaterFoundationBuilder
                ._build_inland_water_mesh(
                    polygon=polygon,
                    coordinate_engine=coordinate_engine,
                    terrain_mesh=terrain_mesh,
                    source_index=index,
                )
            )

            if mesh is None:
                skipped += 1
                continue

            meshes.append(mesh)

        if debug:
            print("")
            print("=" * 70)
            print(
                "ATLAS INLAND WATER FOUNDATION BUILDER "
                f"v{AtlasWaterFoundationBuilder.VERSION}"
            )
            print("=" * 70)
            print(
                f"Input water polygons : "
                f"{len(water_polygons or [])}"
            )
            print(
                f"Accepted polygons    : "
                f"{len(meshes)}"
            )
            print(
                f"Skipped polygons     : "
                f"{skipped}"
            )
            print("=" * 70)
            print("")

        return meshes

    @staticmethod
    def _build_inland_water_mesh(
        polygon,
        coordinate_engine,
        terrain_mesh,
        source_index,
    ):
        prepared = (
            AtlasWaterFoundationBuilder
            ._prepare_polygon_points(
                polygon=polygon,
                coordinate_engine=coordinate_engine,
            )
        )

        if prepared is None:
            return None

        points, flat_triangles = prepared

        terrain_values = AtlasFoundationSampler.sample_polygon(
            terrain_mesh=terrain_mesh,
            footprint_points=points,
            sample_grid=7,
        )

        if not terrain_values:
            terrain_values = [
                AtlasFoundationSampler.terrain_z_at_xy(
                    terrain_mesh=terrain_mesh,
                    x=float(x),
                    y=float(y),
                )
                for x, y in points
            ]

        if not terrain_values:
            return None

        water_bottom_z = max(
            float(value)
            for value in terrain_values
        )
        water_surface_z = (
            water_bottom_z
            + AtlasWaterFoundationBuilder.WATER_HEIGHT_MM
        )

        return (
            AtlasWaterFoundationBuilder
            ._build_horizontal_water_solid(
                points=points,
                flat_triangles=flat_triangles,
                water_bottom_z=water_bottom_z,
                water_surface_z=water_surface_z,
                mesh_type="inland_water_foundation",
                water_type="inland",
                placement_mode="horizontal_above_terrain",
                source_index=source_index,
            )
        )

    @staticmethod
    def _prepare_polygon_points(
        polygon,
        coordinate_engine,
    ):
        if polygon is None or polygon.is_empty:
            return None

        if polygon.geom_type != "Polygon":
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.geom_type != "Polygon"
            or polygon.area <= 0.0
        ):
            return None

        exterior_coordinates = list(
            polygon.exterior.coords
        )

        if len(exterior_coordinates) < 4:
            return None

        geographic_geometry = [
            (
                lat,
                lon,
            )
            for lon, lat in exterior_coordinates
        ]

        points = (
            coordinate_engine
            .geometry_to_stl_mm(
                geographic_geometry
            )
        )

        points = (
            AtlasWaterFoundationBuilder
            ._deduplicate_points(
                points
            )
        )

        if (
            len(points) >= 2
            and points[0] == points[-1]
        ):
            points = points[:-1]

        if len(points) < 3:
            return None

        flat_triangles = (
            AtlasPolygonTriangulator
            .triangulate(
                points
            )
        )

        if not flat_triangles:
            return None

        return points, flat_triangles

    @staticmethod
    def _build_horizontal_water_solid(
        *,
        points,
        flat_triangles,
        water_bottom_z,
        water_surface_z,
        mesh_type,
        water_type,
        placement_mode,
        source_index,
    ):
        bottom = [
            (
                x,
                y,
                water_bottom_z,
            )
            for x, y in points
        ]

        top = [
            (
                x,
                y,
                water_surface_z,
            )
            for x, y in points
        ]

        triangles = []
        walls = []

        for triangle in flat_triangles:
            top_triangle = tuple(
                (
                    x,
                    y,
                    water_surface_z,
                )
                for x, y in triangle
            )

            bottom_triangle = [
                (
                    x,
                    y,
                    water_bottom_z,
                )
                for x, y in triangle
            ]

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

            triangles.extend(
                [
                    (
                        b1,
                        b2,
                        t2,
                    ),
                    (
                        b1,
                        t2,
                        t1,
                    ),
                ]
            )

        return {
            "type": mesh_type,
            "source_index": source_index,
            "water_type": water_type,
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "water_bottom_z": water_bottom_z,
            "water_surface_z": water_surface_z,
            "placement_mode": placement_mode,
        }

    @staticmethod
    def _build_coastline_water_mesh(
        polygon,
        coordinate_engine,
        terrain_mesh,
        source_index,
    ):
        if polygon is None or polygon.is_empty:
            return None

        if polygon.geom_type != "Polygon":
            return None

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if (
            polygon.is_empty
            or not polygon.is_valid
            or polygon.geom_type != "Polygon"
            or polygon.area <= 0.0
        ):
            return None

        exterior_coordinates = list(
            polygon.exterior.coords
        )

        if len(exterior_coordinates) < 4:
            return None

        geographic_geometry = [
            (
                lat,
                lon,
            )
            for lon, lat in exterior_coordinates
        ]

        points = (
            coordinate_engine
            .geometry_to_stl_mm(
                geographic_geometry
            )
        )

        points = (
            AtlasWaterFoundationBuilder
            ._deduplicate_points(
                points
            )
        )

        if (
            len(points) >= 2
            and points[0] == points[-1]
        ):
            points = points[:-1]

        if len(points) < 3:
            return None

        flat_triangles = (
            AtlasPolygonTriangulator
            .triangulate(
                points
            )
        )

        if not flat_triangles:
            return None

        water_bottom_z = (
            AtlasWaterFoundationBuilder
            ._sea_level_z(
                terrain_mesh
            )
        )

        water_surface_z = (
            water_bottom_z
            + AtlasWaterFoundationBuilder
            .WATER_HEIGHT_MM
        )

        bottom = [
            (
                x,
                y,
                water_bottom_z,
            )
            for x, y in points
        ]

        top = [
            (
                x,
                y,
                water_surface_z,
            )
            for x, y in points
        ]

        triangles = []
        walls = []

        for triangle in flat_triangles:
            top_triangle = tuple(
                (
                    x,
                    y,
                    water_surface_z,
                )
                for x, y in triangle
            )

            bottom_triangle = [
                (
                    x,
                    y,
                    water_bottom_z,
                )
                for x, y in triangle
            ]

            triangles.append(
                top_triangle
            )

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

            triangles.extend(
                [
                    (
                        b1,
                        b2,
                        t2,
                    ),
                    (
                        b1,
                        t2,
                        t1,
                    ),
                ]
            )

        return {
            "type": "coastline_water_foundation",
            "source_index": source_index,
            "water_type": "sea",
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "water_bottom_z": water_bottom_z,
            "water_surface_z": water_surface_z,
            "placement_mode": "horizontal_sea_level",
        }

    @staticmethod
    def _sea_level_z(
        terrain_mesh,
    ):
        metadata = (
            terrain_mesh.get(
                "metadata",
                {},
            )
            if terrain_mesh
            else {}
        )

        base_z = float(
            metadata.get(
                "base_z",
                0.0,
            )
        )

        min_height_m = float(
            metadata.get(
                "min_height_m",
                0.0,
            )
        )

        z_scale = float(
            metadata.get(
                "z_scale",
                5500.0,
            )
        )

        if z_scale <= 0.0:
            raise ValueError(
                "Terrain z_scale must be positive."
            )

        return (
            base_z
            + (
                (
                    0.0
                    - min_height_m
                )
                / z_scale
            )
            * 1000.0
        )

    @staticmethod
    def _deduplicate_points(
        points,
    ):
        result = []
        seen = set()

        for x, y in points:
            point = (
                round(
                    float(x),
                    AtlasWaterFoundationBuilder
                    .POINT_PRECISION,
                ),
                round(
                    float(y),
                    AtlasWaterFoundationBuilder
                    .POINT_PRECISION,
                ),
            )

            if result and point == result[-1]:
                continue

            result.append(point)
            seen.add(point)

        return result
