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
from CORE.atlas_water_surface_texture import (
    AtlasWaterSurfaceTexture,
)
from CORE.atlas_water_textured_solid_mesher import (
    AtlasWaterTexturedSolidMesher,
)
from CORE.atlas_terrain_contour_band_builder import (
    AtlasTerrainContourBandBuilder,
)
from CORE.atlas_linear_infrastructure_solid_builder import (
    AtlasLinearInfrastructureSolidBuilder,
)
from CORE.atlas_water_shoreline_composition_resolver import (
    AtlasWaterShorelineCompositionResolver,
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
        surface_texture_amplitude_mm=None,
        surface_texture_wavelength_x_mm=7.0,
        surface_texture_wavelength_y_mm=11.0,
        surface_texture_edge_fade_mm=1.5,
        surface_texture_maximum_edge_length_mm=2.5,
    ):
        texture = AtlasWaterSurfaceTexture(
            amplitude_mm=surface_texture_amplitude_mm,
            wavelength_x_mm=surface_texture_wavelength_x_mm,
            wavelength_y_mm=surface_texture_wavelength_y_mm,
            edge_fade_mm=surface_texture_edge_fade_mm,
        )

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
                    texture=texture,
                    maximum_edge_length_mm=(
                        surface_texture_maximum_edge_length_mm
                    ),
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
    def build_narrow_waterway_meshes(
        waters,
        coordinate_engine,
        terrain_mesh,
        minimum_printable_width_mm,
        cartographic_product_size_mm,
        cartographic_nozzle_diameter_mm,
        cartographic_lod_level,
        debug=True,
    ):
        meshes = []
        skipped = 0

        for water in waters or ():
            tags = water.get("tags", {}) or {}

            waterway_type = str(
                tags.get("waterway", "")
            ).strip().lower()

            if waterway_type not in {
                "river",
                "stream",
                "canal",
            }:
                skipped += 1
                continue

            geometry = water.get("geometry", ())

            if len(geometry) < 2:
                skipped += 1
                continue

            source_width = tags.get("width")

            try:
                candidate = source_width

                if isinstance(candidate, str):
                    candidate = (
                        candidate
                        .replace("m", "")
                        .strip()
                    )

                source_width_m = float(candidate)

                if source_width_m <= 0.0:
                    raise ValueError
            except (
                TypeError,
                ValueError,
            ):
                skipped += 1
                continue

            exaggeration = (
                AtlasWaterShorelineCompositionResolver
                .resolve_cartographic_exaggeration(
                    semantic_class="narrow_waterway",
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
                    semantic_priority=0.80,
                    lod_level=(
                        cartographic_lod_level
                    ),
                )
            )

            mesh = (
                AtlasWaterFoundationBuilder
                ._build_narrow_waterway_mesh(
                    geometry=geometry,
                    coordinate_engine=coordinate_engine,
                    terrain_mesh=terrain_mesh,
                    width_mm=(
                        exaggeration.physical_width_mm
                    ),
                    waterway_type=waterway_type,
                    source_id=water.get("id"),
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
                "ATLAS NARROW WATERWAY "
                "FOUNDATION BUILDER"
            )
            print("=" * 70)
            print(
                f"Input waters      : "
                f"{len(waters or ())}"
            )
            print(
                f"Accepted waterways: "
                f"{len(meshes)}"
            )
            print(
                f"Skipped waterways : "
                f"{skipped}"
            )
            print("=" * 70)
            print("")

        return meshes

    @staticmethod
    def _build_narrow_waterway_mesh(
        *,
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        waterway_type,
        source_id,
    ):
        width_mm = float(width_mm)

        if width_mm <= 0.0:
            raise ValueError(
                "width_mm must be greater than zero"
            )

        points = (
            coordinate_engine
            .geometry_to_stl_mm(
                geometry
            )
        )

        if len(points) < 2:
            return None

        footprint = (
            AtlasTerrainContourBandBuilder
            .build_band(
                polyline=points,
                half_width_mm=(
                    width_mm / 2.0
                ),
            )
        )

        if len(footprint) < 3:
            return None

        mesh = (
            AtlasLinearInfrastructureSolidBuilder
            .build_polygon_solid(
                points=footprint,
                terrain_mesh=terrain_mesh,
                height_mm=(
                    AtlasWaterFoundationBuilder
                    .WATER_HEIGHT_MM
                ),
            )
        )

        if mesh is None:
            return None

        return {
            **mesh,
            "type": (
                "narrow_waterway_foundation"
            ),
            "waterway_type": waterway_type,
            "source_id": source_id,
            "physical_width_mm": width_mm,
            "placement_mode": (
                "terrain_following"
            ),
        }

    @staticmethod
    def build_inland_water_meshes(
        water_polygons,
        coordinate_engine,
        terrain_mesh,
        debug=True,
        surface_texture_amplitude_mm=None,
        surface_texture_wavelength_x_mm=7.0,
        surface_texture_wavelength_y_mm=11.0,
        surface_texture_edge_fade_mm=1.5,
        surface_texture_maximum_edge_length_mm=2.5,
    ):
        texture = AtlasWaterSurfaceTexture(
            amplitude_mm=surface_texture_amplitude_mm,
            wavelength_x_mm=surface_texture_wavelength_x_mm,
            wavelength_y_mm=surface_texture_wavelength_y_mm,
            edge_fade_mm=surface_texture_edge_fade_mm,
        )

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
                    texture=texture,
                    maximum_edge_length_mm=(
                        surface_texture_maximum_edge_length_mm
                    ),
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
        texture,
        maximum_edge_length_mm,
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
                texture=texture,
                maximum_edge_length_mm=(
                    maximum_edge_length_mm
                ),
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
        texture,
        maximum_edge_length_mm,
    ):
        if texture.enabled:
            textured = AtlasWaterTexturedSolidMesher.build(
                boundary_points=points,
                water_bottom_z=water_bottom_z,
                water_surface_z=water_surface_z,
                texture=texture,
                maximum_edge_length_mm=(
                    maximum_edge_length_mm
                ),
            )

            return {
                **textured,
                "type": mesh_type,
                "source_index": source_index,
                "water_type": water_type,
                "water_bottom_z": water_bottom_z,
                "water_surface_z": water_surface_z,
                "placement_mode": placement_mode,
                "surface_texture_amplitude_mm": (
                    texture.amplitude_mm
                ),
                "surface_texture_wavelength_x_mm": (
                    texture.wavelength_x_mm
                ),
                "surface_texture_wavelength_y_mm": (
                    texture.wavelength_y_mm
                ),
                "surface_texture_edge_fade_mm": (
                    texture.edge_fade_mm
                ),
            }

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
            "surface_texture_enabled": False,
            "surface_texture_amplitude_mm": None,
        }

    @staticmethod
    def _build_coastline_water_mesh(
        polygon,
        coordinate_engine,
        terrain_mesh,
        source_index,
        texture,
        maximum_edge_length_mm,
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

        return (
            AtlasWaterFoundationBuilder
            ._build_horizontal_water_solid(
                points=points,
                flat_triangles=flat_triangles,
                water_bottom_z=water_bottom_z,
                water_surface_z=water_surface_z,
                mesh_type="coastline_water_foundation",
                water_type="sea",
                placement_mode="horizontal_sea_level",
                source_index=source_index,
                texture=texture,
                maximum_edge_length_mm=(
                    maximum_edge_length_mm
                ),
            )
        )

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
