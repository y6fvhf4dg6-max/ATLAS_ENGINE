# CORE/atlas_foundation_first_engine.py

from shapely.geometry import Point
from shapely.geometry import Polygon

from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_landmark_foundation_builder import AtlasLandmarkFoundationBuilder
from CORE.atlas_liedberg_muehlenturm_ruin_top_builder import (
    AtlasLiedbergMuehlenturmRuinTopBuilder,
)
from CORE.atlas_bridge_landmark_deduplicator import (
    AtlasBridgeLandmarkDeduplicator,
)
from CORE.atlas_landmark_building_deduplicator import (
    AtlasLandmarkBuildingDeduplicator,
)
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline
from CORE.atlas_foundation_scene_builder import (
    AtlasFoundationSceneBuilder,
)
from CORE.atlas_foundation_scene_xy_bounds_filter import (
    AtlasFoundationSceneXYBoundsFilter,
)
from CORE.atlas_debug_reporter import AtlasDebugReporter
from CORE.atlas_road_foundation_builder import (
    AtlasRoadFoundationBuilder,
)
from CORE.atlas_park_foundation_builder import (
    AtlasParkFoundationBuilder,
)
from CORE.atlas_elevated_area_foundation_builder import (
    AtlasElevatedAreaFoundationBuilder,
)
from CORE.atlas_artwork_foundation_builder import (
    AtlasArtworkFoundationBuilder,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)
from CORE.atlas_forest_canopy_foundation_builder import (
    AtlasForestCanopyFoundationBuilder,
)
from CORE.atlas_nature_pipeline import AtlasNaturePipeline
from CORE.atlas_vegetation_composition_resolver import (
    AtlasVegetationCompositionResolver,
)
from CORE.atlas_castle_wall_builder import (
    AtlasCastleWallBuilder,
)
from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)
from CORE.atlas_semantic_architecture_adapter_resolver import (
    AtlasSemanticArchitectureAdapterResolver,
)
from CORE.atlas_castle_shell_builder import (
    AtlasCastleShellBuilder,
)
from CORE.atlas_castle_tower_cap_builder import (
    AtlasCastleTowerCapBuilder,
)
from CORE.atlas_castle_focus_engine import (
    AtlasCastleFocusEngine,
)
from CORE.atlas_coastline_water_builder import (
    AtlasCoastlineWaterBuilder,
)
from CORE.atlas_inland_water_polygon_builder import (
    AtlasInlandWaterPolygonBuilder,
)
from CORE.atlas_water_foundation_builder import (
    AtlasWaterFoundationBuilder,
)
from CORE.atlas_input_quality_report import (
    AtlasInputQualityReport,
)
from EXPORT.atlas_stl_writer import AtlasSTLWriter


class AtlasFoundationFirstEngine:
    @staticmethod
    def _assemble_vegetation_output(
        *,
        tree_meshes,
        forest_canopy_meshes,
    ):
        tree_meshes = list(tree_meshes or ())
        forest_canopy_meshes = list(
            forest_canopy_meshes or ()
        )

        return {
            "meshes": [
                *tree_meshes,
                *forest_canopy_meshes,
            ],
            "mesh_groups": {
                "trees": tree_meshes,
                "forest_canopies": forest_canopy_meshes,
            },
        }

    @classmethod
    def _prepare_scene_vegetation(
        cls,
        *,
        existing_trees,
        nature_data,
        coordinate_engine,
        terrain_mesh,
        castle_only,
        debug=True,
    ):
        if castle_only:
            return {
                "tree_input": (),
                "tree_rows": (),
                "tree_clusters": (),
                "forest_canopies": (),
                "forest_canopy_surfaces": (),
                "tree_meshes": [],
                "forest_canopy_meshes": [],
            }

        return cls._build_vegetation_meshes(
            existing_trees=existing_trees,
            nature_data=nature_data,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_mesh,
            debug=debug,
        )


    @classmethod
    def _build_vegetation_meshes(
        cls,
        *,
        existing_trees,
        nature_data,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        composition = cls._resolve_vegetation_composition(
            existing_trees=existing_trees,
            nature_data=nature_data,
        )

        tree_meshes = AtlasTreeFoundationBuilder.build_trees(
            trees=composition["tree_input"],
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_mesh,
            debug=debug,
        )

        forest_canopy_meshes = (
            AtlasForestCanopyFoundationBuilder.build(
                surfaces=composition["forest_canopy_surfaces"],
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
                debug=debug,
            )
        )

        return {
            **composition,
            "tree_meshes": tree_meshes,
            "forest_canopy_meshes": forest_canopy_meshes,
        }

    @staticmethod
    def _resolve_vegetation_composition(
        *,
        existing_trees,
        nature_data,
    ):
        composition = (
            AtlasVegetationCompositionResolver
            .compose_nature_data(nature_data)
        )

        return {
            "tree_input": tuple(
                [
                    *(existing_trees or ()),
                    *composition["isolated_trees"],
                ]
            ),
            "tree_rows": composition["tree_rows"],
            "tree_clusters": composition["tree_clusters"],
            "forest_canopies": composition["forest_canopies"],
            "forest_canopy_surfaces": (
                composition["forest_canopy_surfaces"]
            ),
        }

    @staticmethod
    def resolve_castle_semantic_architecture(
        castle_geometry,
    ):
        return (
            AtlasSemanticArchitectureAdapterResolver
            .resolve(castle_geometry)
        )

    @staticmethod
    def attach_castle_semantic_architecture(
        *,
        result,
        castle_geometry,
        include,
    ):
        if not include:
            return result

        result["castle_semantic_architecture"] = (
            AtlasFoundationFirstEngine
            .resolve_castle_semantic_architecture(
                castle_geometry
            )
        )

        return result

    @staticmethod
    def _build_water_polygon_groups(
        waters,
        coastlines,
        bbox,
        debug=True,
    ):
        return {
            "coastline": (
                AtlasCoastlineWaterBuilder.build_water_polygons(
                    coastlines=coastlines,
                    bbox=bbox,
                    debug=debug,
                )
            ),
            "inland": (
                AtlasInlandWaterPolygonBuilder.build_polygons(
                    waters=waters,
                    bbox=bbox,
                    debug=debug,
                )
            ),
        }

    @staticmethod
    def _build_water_polygons(
        waters,
        coastlines,
        bbox,
        debug=True,
    ):
        groups = (
            AtlasFoundationFirstEngine
            ._build_water_polygon_groups(
                waters=waters,
                coastlines=coastlines,
                bbox=bbox,
                debug=debug,
            )
        )

        return [
            *groups["coastline"],
            *groups["inland"],
        ]

    @staticmethod
    def _water_polygons_to_stl_mm(
        water_polygons,
        coordinate_engine,
    ):
        converted = []

        for polygon in water_polygons or []:
            if (
                polygon is None
                or polygon.is_empty
                or polygon.geom_type != "Polygon"
            ):
                continue

            geographic_points = [
                (
                    float(lat),
                    float(lon),
                )
                for lon, lat in list(
                    polygon.exterior.coords
                )
            ]

            points_mm = (
                coordinate_engine.geometry_to_stl_mm(
                    geographic_points
                )
            )

            if len(points_mm) < 3:
                continue

            converted_polygon = Polygon(points_mm)

            if not converted_polygon.is_valid:
                converted_polygon = (
                    converted_polygon.buffer(0)
                )

            if (
                converted_polygon.is_empty
                or not converted_polygon.is_valid
                or converted_polygon.geom_type
                != "Polygon"
                or converted_polygon.area <= 0.0
            ):
                continue

            converted.append(converted_polygon)

        return converted

    @staticmethod
    def _tree_mesh_base_center(tree_mesh):
        points = [
            point
            for triangle in tree_mesh.get(
                "triangles",
                (),
            )
            for point in triangle
        ]

        if not points:
            return None

        minimum_z = min(
            float(point[2])
            for point in points
        )

        base_points = [
            point
            for point in points
            if abs(
                float(point[2]) - minimum_z
            )
            <= 1e-6
        ]

        if not base_points:
            return None

        return (
            sum(
                float(point[0])
                for point in base_points
            )
            / len(base_points),
            sum(
                float(point[1])
                for point in base_points
            )
            / len(base_points),
        )

    @classmethod
    def _remove_tree_meshes_inside_water_polygons(
        cls,
        tree_meshes,
        water_polygons_mm,
    ):
        water_polygons_mm = list(
            water_polygons_mm or []
        )

        if not water_polygons_mm:
            return list(tree_meshes or [])

        retained = []

        for tree_mesh in tree_meshes or []:
            source = str(
                tree_mesh.get("source")
                or tree_mesh.get(
                    "tags",
                    {},
                ).get("source")
                or ""
            ).strip().lower()

            if source != "worldcover":
                retained.append(tree_mesh)
                continue

            center = cls._tree_mesh_base_center(
                tree_mesh
            )

            if center is None:
                retained.append(tree_mesh)
                continue

            point = Point(
                float(center[0]),
                float(center[1]),
            )

            inside_water = any(
                polygon.covers(point)
                for polygon in water_polygons_mm
            )

            if not inside_water:
                retained.append(tree_mesh)

        return retained

    @staticmethod
    def _keep_landmark_meshes_inside_product_bounds(
        landmark_meshes,
        product_max_x,
        product_max_y,
    ):
        return AtlasFoundationSceneXYBoundsFilter.keep_fully_inside(
            meshes=landmark_meshes,
            min_x=0.0,
            max_x=float(product_max_x),
            min_y=0.0,
            max_y=float(product_max_y),
            tolerance=1e-9,
        )

    @staticmethod
    def _keep_road_meshes_inside_product_bounds(
        road_meshes,
        product_max_x,
        product_max_y,
    ):
        return AtlasFoundationSceneXYBoundsFilter.keep_fully_inside(
            meshes=road_meshes,
            min_x=0.0,
            max_x=float(product_max_x),
            min_y=0.0,
            max_y=float(product_max_y),
            tolerance=1e-9,
        )

    """
    ATLAS Foundation-First Engine v0.5

    Akış:
    PBF
      ↓
    Terrain
      ↓
    Buildings / Roads / Parks / Trees
      ↓
    Independent castle walls
      ↓
    Multipolygon castle shells
      ↓
    STL

    Kale davranışı:
    - barrier=city_wall gibi bağımsız surlar Wall Builder ile üretilir
    - relation outer/inner geometrileri Shell Builder ile tek kabuk yapılır
    - relation sınırları ayrıca ikinci kez sur olarak üretilmez

    v0.5:
    - İsteğe bağlı castle-focus bbox desteği
    - Sabit XY ölçeğinde dikdörtgen terrain desteği
    - Eski kare terrain davranışı varsayılan olarak korunur
    """

    VERSION = "0.5"
    BASE_PLATE_HEIGHT_MM = 0.80

    @staticmethod
    def _resolve_scene_scale(
        bbox,
        target_size_mm,
        bed_width_mm,
        bed_depth_mm,
        margin_mm,
        fixed_xy_scale,
        use_fixed_xy_scale,
        debug=True,
    ):
        if use_fixed_xy_scale:
            return AtlasScaleEngine.calculate_dimensions_from_scale(
                bbox=bbox,
                xy_scale=fixed_xy_scale,
                debug=debug,
            )

        return AtlasScaleEngine.calculate_fit_from_bbox(
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            debug=debug,
        )

    @staticmethod
    def generate_city_stl(
        pbf_path,
        bbox,
        output_path,
        target_size_mm=200,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=None,
        min_points=4,
        max_points=300,
        z_scale=5500,
        terrain_provider_name="srtm",
        terrain_smoothing_passes=0,
        terrain_surface_texture_amplitude_mm=None,
        terrain_surface_texture_wavelength_x_mm=28.0,
        terrain_surface_texture_wavelength_y_mm=37.0,
        terrain_surface_texture_edge_fade_mm=8.0,
        water_surface_texture_amplitude_mm=None,
        water_surface_texture_wavelength_x_mm=7.0,
        water_surface_texture_wavelength_y_mm=11.0,
        water_surface_texture_edge_fade_mm=1.5,
        water_surface_texture_maximum_edge_length_mm=5.0,
        strict_input_quality=False,
        nature_provider_names=("worldcover",),
        castle_only=False,
        castle_focus=False,
        castle_focus_padding_m=10.0,
        fixed_xy_scale=5500.0,
        use_fixed_xy_scale=False,
        include_castle_semantic_architecture=False,
        road_minimum_printable_width_mm=None,
        debug=True,
    ):
        source_bbox = bbox

        data = AtlasLocalOSMReader.read(
            pbf_path,
            source_bbox,
        )

        raw_buildings = data.get(
            "buildings",
            [],
        )

        hierarchy_raw_buildings = list(
            raw_buildings
        )

        landmarks = data.get(
            "landmarks",
            [],
        )

        landmarks = (
            AtlasBridgeLandmarkDeduplicator.filter_landmarks(
                landmarks
            )
        )

        raw_buildings = (
            AtlasLandmarkBuildingDeduplicator.filter_buildings(
                raw_buildings=raw_buildings,
                landmarks=landmarks,
            )
        )

        trees = data.get(
            "trees",
            [],
        )

        roads = data.get(
            "roads",
            [],
        )

        pedestrian_paths = data.get(
            "pedestrian_paths",
            [],
        )

        elevated_areas = data.get(
            "elevated_areas",
            [],
        )

        artworks = data.get(
            "artworks",
            [],
        )

        parks = data.get(
            "parks",
            [],
        )

        waters = data.get(
            "waters",
            [],
        )

        coastlines = data.get(
            "coastlines",
            [],
        )

        castles = data.get(
            "castles",
            [],
        )

        castle_walls = data.get(
            "castle_walls",
            [],
        )

        defensive_towers = data.get(
            "defensive_towers",
            [],
        )

        nature_data = AtlasNaturePipeline.fetch(
            bbox=source_bbox,
            provider_names=nature_provider_names,
            debug=debug,
        )

        castle_geometry = AtlasCastleGeometryClassifier.classify(
            castles=castles,
            castle_walls=castle_walls,
            debug=debug,
        )

        shell_castles = castle_geometry["shell_castles"]

        independent_castle_walls = castle_geometry["independent_castle_walls"]

        relation_castle_walls = castle_geometry["relation_castle_walls"]

        inferred_perimeter_walls = castle_geometry["inferred_perimeter_walls"]

        unknown_castles = castle_geometry["unknown_castles"]

        if debug:
            print("")
            print("=" * 70)
            print(
                "ATLAS FOUNDATION-FIRST ENGINE "
                f"v{AtlasFoundationFirstEngine.VERSION}"
            )
            print("=" * 70)
            print(f"Reader buildings        : " f"{len(raw_buildings)}")
            print(f"Reader landmarks        : " f"{len(landmarks)}")
            print(f"Reader trees            : " f"{len(trees)}")
            print(f"Reader roads            : " f"{len(roads)}")
            print(f"Reader pedestrian paths : " f"{len(pedestrian_paths)}")
            print(f"Reader parks            : " f"{len(parks)}")
            print(f"Reader waters           : " f"{len(waters)}")
            print(f"Reader castles          : " f"{len(castles)}")
            print(f"Reader castle walls     : " f"{len(castle_walls)}")
            print(f"Independent walls       : " f"{len(independent_castle_walls)}")
            print(f"Relation wall records   : " f"{len(relation_castle_walls)}")
            print(f"Inferred perimeter walls: " f"{len(inferred_perimeter_walls)}")
            print(f"Unknown castles         : " f"{len(unknown_castles)}")
            print(f"Reader defensive towers : " f"{len(defensive_towers)}")
            print("=" * 70)

        working_bbox = source_bbox
        size_x_mm = None
        size_y_mm = None
        focus_result = None

        use_castle_focus = bool(castle_focus)

        if use_castle_focus:
            focus_result = AtlasCastleFocusEngine.calculate_focus_bbox(
                raw_buildings=raw_buildings,
                castles=castles,
                independent_castle_walls=(independent_castle_walls),
                shell_castles=shell_castles,
                source_bbox=source_bbox,
                min_points=min_points,
                max_points=max_points,
                padding_m=castle_focus_padding_m,
                debug=debug,
            )

            working_bbox = focus_result["bbox"]

        fixed_scale_mode = bool(
            use_fixed_xy_scale
            or (
                use_castle_focus
                and castle_only
            )
        )

        scale_result = AtlasFoundationFirstEngine._resolve_scene_scale(
            bbox=working_bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            fixed_xy_scale=fixed_xy_scale,
            use_fixed_xy_scale=fixed_scale_mode,
            debug=debug,
        )

        xy_scale = scale_result["xy_scale"]

        if fixed_scale_mode:
            size_x_mm = scale_result["size_x_mm"]
            size_y_mm = scale_result["size_y_mm"]

        south, west, _north, _east = working_bbox

        coordinate_engine = AtlasCoordinateEngine(
            origin_lat=south,
            origin_lon=west,
            xy_scale=xy_scale,
            z_scale=z_scale,
        )

        terrain_slab = AtlasTerrainPipeline.build_terrain_slab(
            bbox=working_bbox,
            target_size_mm=target_size_mm,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            z_scale=z_scale,
            base_z=(AtlasFoundationFirstEngine.BASE_PLATE_HEIGHT_MM),
            bottom_z=0.0,
            grid_size=25,
            terrain_provider_name=(terrain_provider_name),
            smoothing_passes=terrain_smoothing_passes,
            surface_texture_amplitude_mm=(
                terrain_surface_texture_amplitude_mm
            ),
            surface_texture_wavelength_x_mm=(
                terrain_surface_texture_wavelength_x_mm
            ),
            surface_texture_wavelength_y_mm=(
                terrain_surface_texture_wavelength_y_mm
            ),
            surface_texture_edge_fade_mm=(
                terrain_surface_texture_edge_fade_mm
            ),
            debug=debug,
        )

        input_quality_report = AtlasInputQualityReport.build(
            buildings=raw_buildings,
            castles=castles,
            castle_geometry=castle_geometry,
            terrain_grid=terrain_slab.get(
                "grid",
                {},
            ),
            castle_focus_result=focus_result,
        )

        input_quality_policy = (
            AtlasInputQualityReport.evaluate_policy(
                input_quality_report
            )
        )

        input_quality_report["policy"] = (
            input_quality_policy
        )

        AtlasInputQualityReport.enforce_policy(
            policy=input_quality_policy,
            strict=strict_input_quality,
        )

        water_polygon_groups = (
            AtlasFoundationFirstEngine
            ._build_water_polygon_groups(
                waters=waters,
                coastlines=coastlines,
                bbox=working_bbox,
                debug=debug,
            )
        )

        coastline_water_meshes = (
            AtlasWaterFoundationBuilder
            .build_coastline_water_meshes(
                water_polygons=(
                    water_polygon_groups["coastline"]
                ),
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_slab,
                debug=debug,
                surface_texture_amplitude_mm=(
                    water_surface_texture_amplitude_mm
                ),
                surface_texture_wavelength_x_mm=(
                    water_surface_texture_wavelength_x_mm
                ),
                surface_texture_wavelength_y_mm=(
                    water_surface_texture_wavelength_y_mm
                ),
                surface_texture_edge_fade_mm=(
                    water_surface_texture_edge_fade_mm
                ),
                surface_texture_maximum_edge_length_mm=(
                    water_surface_texture_maximum_edge_length_mm
                ),
            )
        )

        inland_water_meshes = (
            AtlasWaterFoundationBuilder
            .build_inland_water_meshes(
                water_polygons=(
                    water_polygon_groups["inland"]
                ),
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_slab,
                debug=debug,
                surface_texture_amplitude_mm=(
                    water_surface_texture_amplitude_mm
                ),
                surface_texture_wavelength_x_mm=(
                    water_surface_texture_wavelength_x_mm
                ),
                surface_texture_wavelength_y_mm=(
                    water_surface_texture_wavelength_y_mm
                ),
                surface_texture_edge_fade_mm=(
                    water_surface_texture_edge_fade_mm
                ),
                surface_texture_maximum_edge_length_mm=(
                    water_surface_texture_maximum_edge_length_mm
                ),
            )
        )

        water_meshes = [
            *coastline_water_meshes,
            *inland_water_meshes,
        ]

        scene = AtlasFoundationSceneBuilder.build_scene(
            raw_buildings=raw_buildings,
            hierarchy_raw_buildings=(
                hierarchy_raw_buildings
            ),
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            castles=castles,
            bbox=working_bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            xy_scale=xy_scale,
            z_scale=z_scale,
            max_buildings=max_buildings,
            min_points=min_points,
            max_points=max_points,
            castle_only=castle_only,
            debug=debug,
        )

        building_meshes = scene.get_all_meshes()

        if castle_only:
            road_input = []
            park_input = []
            tree_input = []
        else:
            road_input = [
                *roads,
                *pedestrian_paths,
            ]

            park_input = parks
            tree_input = trees

        road_meshes = AtlasRoadFoundationBuilder.build_roads(
            roads=road_input,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            minimum_printable_width_mm=(
                road_minimum_printable_width_mm
            ),
            debug=debug,
        )

        park_meshes = AtlasParkFoundationBuilder.build_parks(
            parks=park_input,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        elevated_area_meshes = (
            AtlasElevatedAreaFoundationBuilder.build_areas(
                areas=(
                    []
                    if castle_only
                    else elevated_areas
                ),
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_slab,
                debug=debug,
            )
        )

        landmark_meshes = AtlasLandmarkFoundationBuilder.build_landmarks(
            landmarks=([] if castle_only else landmarks),
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            road_meshes=road_meshes,
            hierarchy_context=scene.metadata.get(
                "building_part_hierarchy"
            ),
            debug=debug,
        )

        landmark_meshes = [
            AtlasLiedbergMuehlenturmRuinTopBuilder.apply(
                tower_mesh=mesh,
            )
            for mesh in landmark_meshes
        ]

        artwork_meshes = AtlasArtworkFoundationBuilder.build_artworks(
            artworks=(
                []
                if castle_only
                else artworks
            ),
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        product_max_x = (
            float(size_x_mm)
            if size_x_mm is not None
            else float(target_size_mm)
        )
        product_max_y = (
            float(size_y_mm)
            if size_y_mm is not None
            else float(target_size_mm)
        )

        road_meshes = (
            AtlasFoundationFirstEngine
            ._keep_road_meshes_inside_product_bounds(
                road_meshes=road_meshes,
                product_max_x=product_max_x,
                product_max_y=product_max_y,
            )
        )

        landmark_meshes = (
            AtlasFoundationFirstEngine
            ._keep_landmark_meshes_inside_product_bounds(
                landmark_meshes=landmark_meshes,
                product_max_x=product_max_x,
                product_max_y=product_max_y,
            )
        )

        vegetation = (
            AtlasFoundationFirstEngine
            ._prepare_scene_vegetation(
                existing_trees=tree_input,
                nature_data=nature_data,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_slab,
                castle_only=castle_only,
                debug=debug,
            )
        )

        tree_meshes = vegetation["tree_meshes"]
        forest_canopy_meshes = vegetation[
            "forest_canopy_meshes"
        ]

        water_polygons_mm = (
            AtlasFoundationFirstEngine
            ._water_polygons_to_stl_mm(
                water_polygons=[
                    *water_polygon_groups["coastline"],
                    *water_polygon_groups["inland"],
                ],
                coordinate_engine=coordinate_engine,
            )
        )

        tree_meshes = (
            AtlasFoundationFirstEngine
            ._remove_tree_meshes_inside_water_polygons(
                tree_meshes=tree_meshes,
                water_polygons_mm=water_polygons_mm,
            )
        )

        castle_wall_meshes = AtlasCastleWallBuilder.build_walls(
            castle_walls=(independent_castle_walls),
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        castle_shell_meshes = AtlasCastleShellBuilder.build_shells(
            castles=shell_castles,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        AtlasInputQualityReport.add_shell_corrections(
            report=input_quality_report,
            shell_meshes=castle_shell_meshes,
        )

        castle_tower_cap_meshes = AtlasCastleTowerCapBuilder.build_caps(
            castles=shell_castles,
            coordinate_engine=coordinate_engine,
            terrain_mesh=terrain_slab,
            debug=debug,
        )

        meshes = [terrain_slab]

        meshes.extend(building_meshes)

        meshes.extend(road_meshes)

        meshes.extend(park_meshes)

        meshes.extend(elevated_area_meshes)

        meshes.extend(artwork_meshes)

        meshes.extend(landmark_meshes)

        vegetation_output = (
            AtlasFoundationFirstEngine
            ._assemble_vegetation_output(
                tree_meshes=tree_meshes,
                forest_canopy_meshes=forest_canopy_meshes,
            )
        )

        meshes.extend(
            vegetation_output["meshes"]
        )

        meshes.extend(water_meshes)

        meshes.extend(castle_wall_meshes)

        meshes.extend(castle_shell_meshes)

        meshes.extend(castle_tower_cap_meshes)

        triangle_count = AtlasDebugReporter.count_triangles(meshes)

        if debug:
            print("")
            print("=" * 70)
            print("FOUNDATION-FIRST FINAL REPORT")
            print("=" * 70)
            print("Terrain meshes     : 1")
            print(f"Building meshes    : " f"{len(building_meshes)}")
            print(f"Road meshes        : " f"{len(road_meshes)}")
            print(f"Park meshes        : " f"{len(park_meshes)}")
            print(
                f"Elevated areas     : "
                f"{len(elevated_area_meshes)}"
            )
            print(f"Artwork meshes     : " f"{len(artwork_meshes)}")
            print(f"Landmark meshes    : " f"{len(landmark_meshes)}")
            print(f"Tree meshes        : " f"{len(tree_meshes)}")
            print(
                f"Forest canopies    : "
                f"{len(forest_canopy_meshes)}"
            )
            print(f"Water meshes       : " f"{len(water_meshes)}")
            print(f"Castle wall meshes : " f"{len(castle_wall_meshes)}")
            print(f"Castle shell meshes: " f"{len(castle_shell_meshes)}")
            print(f"Castle tower caps  : " f"{len(castle_tower_cap_meshes)}")
            print(f"Total meshes       : " f"{len(meshes)}")
            print(f"Triangles          : " f"{triangle_count}")
            print(f"Castle focus       : " f"{use_castle_focus}")
            print(f"XY scale           : " f"1:{xy_scale:.2f}")

            if size_x_mm is not None:
                print(f"Terrain width      : " f"{size_x_mm:.2f} mm")

            if size_y_mm is not None:
                print(f"Terrain depth      : " f"{size_y_mm:.2f} mm")

            print("=" * 70)

        AtlasSTLWriter.write(
            meshes,
            output_path,
        )

        if debug:
            print("")
            print("=" * 70)
            print("ATLAS FOUNDATION-FIRST " "STL EXPORTED")
            print("=" * 70)
            print(f"Output    : {output_path}")
            print(f"XY scale  : 1:{xy_scale:.2f}")
            print(f"Meshes    : {len(meshes)}")
            print(f"Triangles : {triangle_count}")
            print("=" * 70)

        terrain_metadata = terrain_slab.get(
            "metadata",
            {},
        )

        result = {
            "output_path": output_path,
            "reader_buildings": len(raw_buildings),
            "reader_landmarks": len(landmarks),
            "reader_trees": len(trees),
            "reader_roads": len(roads),
            "reader_pedestrian_paths": len(pedestrian_paths),
            "reader_elevated_areas": len(elevated_areas),
            "reader_artworks": len(artworks),
            "reader_parks": len(parks),
            "reader_waters": len(waters),
            "reader_coastlines": len(coastlines),
            "reader_castles": len(castles),
            "reader_castle_walls": len(castle_walls),
            "reader_independent_castle_walls": len(independent_castle_walls),
            "reader_relation_castle_walls": len(relation_castle_walls),
            "reader_defensive_towers": len(defensive_towers),
            "buildings": len(building_meshes),
            "water_meshes": len(water_meshes),
            "elevated_area_meshes": len(elevated_area_meshes),
            "artwork_meshes": len(artwork_meshes),
            "landmark_meshes": len(landmark_meshes),
            "forest_canopy_meshes": len(
                forest_canopy_meshes
            ),
            "castle_wall_meshes": len(castle_wall_meshes),
            "castle_shell_meshes": len(castle_shell_meshes),
            "castle_tower_cap_meshes": len(castle_tower_cap_meshes),
            "meshes": len(meshes),
            "mesh_groups": {
                "terrain": [terrain_slab],
                "buildings": building_meshes,
                "roads": road_meshes,
                "parks": park_meshes,
                "elevated_areas": elevated_area_meshes,
                "artworks": artwork_meshes,
                "landmarks": landmark_meshes,
                "trees": (
                    vegetation_output["mesh_groups"]["trees"]
                ),
                "forest_canopies": (
                    vegetation_output[
                        "mesh_groups"
                    ]["forest_canopies"]
                ),
                "waters": water_meshes,
                "castle_walls": (castle_wall_meshes),
                "castle_shells": (castle_shell_meshes),
                "castle_tower_caps": (castle_tower_cap_meshes),
            },
            "triangles": triangle_count,
            "xy_scale": xy_scale,
            "source_bbox": source_bbox,
            "working_bbox": working_bbox,
            "castle_focus": use_castle_focus,
            "castle_focus_result": focus_result,
            "terrain_size_x_mm": (
                terrain_metadata.get(
                    "size_x_mm",
                    terrain_metadata.get("size_mm"),
                )
            ),
            "terrain_size_y_mm": (
                terrain_metadata.get(
                    "size_y_mm",
                    terrain_metadata.get("size_mm"),
                )
            ),
            "terrain_min_height_m": terrain_metadata.get(
                "min_height_m"
            ),
            "terrain_max_height_m": terrain_metadata.get(
                "max_height_m"
            ),
            "terrain_delta_height_m": terrain_metadata.get(
                "delta_height_m"
            ),
            "terrain_smoothing_passes": terrain_metadata.get(
                "smoothing_passes",
                0,
            ),
            "input_quality_report": input_quality_report,
            "mode": "foundation_first",
        }

        return (
            AtlasFoundationFirstEngine
            .attach_castle_semantic_architecture(
                result=result,
                castle_geometry=castle_geometry,
                include=(
                    include_castle_semantic_architecture
                ),
            )
        )
