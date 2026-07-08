# CORE/atlas_engine.py

from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_scale_engine import AtlasScaleEngine
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine
from CORE.atlas_scene_builder import AtlasSceneBuilder
from CORE.atlas_scene_normalizer import AtlasSceneNormalizer
from CORE.atlas_scene_fitter import AtlasSceneFitter
from CORE.atlas_surface_engine import AtlasSurfaceEngine
from CORE.atlas_boolean_surface_builder import AtlasBooleanSurfaceBuilder
from CORE.atlas_road_polygon_builder import AtlasRoadPolygonBuilder
from CORE.atlas_srtm_provider import AtlasSRTMProvider
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator
from EXPORT.atlas_stl_writer import AtlasSTLWriter
from CORE.atlas_foundation_engine import AtlasFoundationEngine
from CORE.atlas_construction_engine import AtlasConstructionEngine
from CORE.atlas_debug_reporter import AtlasDebugReporter


class AtlasEngine:
    BASE_PLATE_HEIGHT_MM = AtlasSurfaceEngine.get_base_plate_height()
    CITY_Z_OFFSET_MM = AtlasSurfaceEngine.get_sidewalk_level()

    @staticmethod
    def generate_city_stl(
        pbf_path,
        bbox,
        output_path,
        target_size_mm=180,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=None,
        min_points=4,
        max_points=80,
        z_scale=5500,
        debug=True,
        use_raised_roads=False,
        use_recessed_roads=False,
    ):
        if debug:
            AtlasDebugReporter.print_header()

        data = AtlasLocalOSMReader.read(pbf_path, bbox)

        raw_buildings = data.get("buildings", [])
        trees = data.get("trees", [])
        roads = data.get("roads", [])
        pedestrian_paths = data.get("pedestrian_paths", [])

        if debug:
            print(f"Reader buildings        : {len(raw_buildings)}")
            print(f"Reader trees            : {len(trees)}")
            print(f"Reader roads            : {len(roads)}")
            print(f"Reader pedestrian paths : {len(pedestrian_paths)}")

        xy_scale = AtlasScaleEngine.calculate_xy_scale_from_bbox(
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            debug=debug,
        )

        south, west, _north, _east = bbox

        coordinate_engine = AtlasCoordinateEngine(
            origin_lat=south,
            origin_lon=west,
            xy_scale=xy_scale,
            z_scale=z_scale,
        )

        road_footprints = AtlasSurfaceEngine.build_road_footprints(
            roads=roads,
            coordinate_engine=coordinate_engine,
            debug=debug,
        )

        road_polygons = AtlasRoadPolygonBuilder.build_road_polygons(
            road_footprints=road_footprints,
            debug=debug,
            clip_bounds={
                "min_x": 0.0,
                "max_x": target_size_mm,
                "min_y": 0.0,
                "max_y": target_size_mm,
            },
        )

        road_groove_meshes = (
            AtlasBooleanSurfaceBuilder.build_road_polygon_groove_meshes(
                road_polygons,
                debug=debug,
            )
        )

        scene = AtlasSceneBuilder.build_scene(
            raw_buildings=raw_buildings,
            coordinate_engine=coordinate_engine,
            roads=roads if use_raised_roads else [],
            bbox=bbox,
            target_size_mm=target_size_mm,
            bed_width_mm=bed_width_mm,
            bed_depth_mm=bed_depth_mm,
            margin_mm=margin_mm,
            xy_scale=xy_scale,
            z_scale=z_scale,
            max_buildings=max_buildings,
            min_points=min_points,
            max_points=max_points,
            debug=debug,
        )

        if debug:
            scene.print_summary()

        meshes = scene.get_all_meshes()

        if debug:
            print(f"Raw scene meshes    : {len(meshes)}")
            print(f"Raw scene triangles : {AtlasDebugReporter.count_triangles(meshes)}")
            print(f"Raw road groove meshes    : {len(road_groove_meshes)}")
            print(
                f"Raw road groove triangles : "
                f"{AtlasDebugReporter.count_triangles(road_groove_meshes)}"
            )

        normalize_transform = AtlasSceneNormalizer.calculate_transform(meshes)

        meshes = AtlasSceneNormalizer.apply_transform(
            meshes,
            normalize_transform,
        )

        road_groove_meshes = AtlasSceneNormalizer.apply_transform(
            road_groove_meshes,
            normalize_transform,
        )

        if debug:
            print(f"After normalize meshes    : {len(meshes)}")
            print(
                f"After normalize triangles : {AtlasDebugReporter.count_triangles(meshes)}"
            )
            print(f"After normalize road grooves    : {len(road_groove_meshes)}")
            print(
                f"After normalize road groove triangles : "
                f"{AtlasDebugReporter.count_triangles(road_groove_meshes)}"
            )

        fit_transform = AtlasSceneFitter.calculate_transform(
            meshes,
            bed_width=target_size_mm,
            bed_depth=target_size_mm,
            margin=0,
        )

        meshes = AtlasSceneFitter.apply_transform(
            meshes,
            fit_transform,
        )

        road_groove_meshes = AtlasSceneFitter.apply_transform(
            road_groove_meshes,
            fit_transform,
        )

        if debug:
            print(f"After fit meshes    : {len(meshes)}")
            print(f"After fit triangles : {AtlasDebugReporter.count_triangles(meshes)}")
            print(f"After fit road grooves    : {len(road_groove_meshes)}")
            print(
                f"After fit road groove triangles : "
                f"{AtlasDebugReporter.count_triangles(road_groove_meshes)}"
            )

        # Temporary terrain integration:
        # Lift buildings above terrain so they are visible.
        # Next step: per-building terrain placement.

        meshes = AtlasEngine._offset_meshes_z(
            meshes,
            AtlasEngine.CITY_Z_OFFSET_MM,
        )

        road_groove_meshes = AtlasEngine._offset_meshes_z(
            road_groove_meshes,
            AtlasEngine.CITY_Z_OFFSET_MM,
        )

        if debug:
            print(f"After city z-offset meshes    : {len(meshes)}")
            print(
                f"After city z-offset triangles : "
                f"{AtlasDebugReporter.count_triangles(meshes)}"
            )

        scene_origin_x = (bed_width_mm - target_size_mm) / 2.0
        scene_origin_y = (bed_depth_mm - target_size_mm) / 2.0

        xy_offset = {
            "min_x": 0.0,
            "min_y": 0.0,
            "min_z": 0.0,
            "scale": 1.0,
            "offset_x": scene_origin_x,
            "offset_y": scene_origin_y,
        }

        meshes = AtlasSceneFitter.apply_transform(
            meshes,
            xy_offset,
        )

        road_groove_meshes = AtlasSceneFitter.apply_transform(
            road_groove_meshes,
            xy_offset,
        )

        if use_recessed_roads:
            road_groove_meshes = AtlasEngine._filter_meshes_inside_xy_bounds(
                road_groove_meshes,
                min_x=scene_origin_x,
                max_x=scene_origin_x + target_size_mm,
                min_y=scene_origin_y,
                max_y=scene_origin_y + target_size_mm,
                tolerance=0.50,
            )

            # meshes.extend(road_groove_meshes)

        terrain_provider = AtlasSRTMProvider(
            data_dir="Data/TERRAIN/SRTM",
            debug=debug,
        )

        terrain_slab = AtlasTerrainMeshGenerator.build_closed_slab_mesh(
            terrain_provider=terrain_provider,
            bbox=bbox,
            size_mm=target_size_mm,
            grid_size=25,
            z_scale=z_scale,
            base_z=AtlasEngine.BASE_PLATE_HEIGHT_MM,
            bottom_z=0.0,
        )
        meshes = AtlasEngine._place_meshes_on_terrain(
            meshes=meshes,
            terrain_mesh=terrain_slab,
            scene_origin_x=scene_origin_x,
            scene_origin_y=scene_origin_y,
        )

        terrain_slab = AtlasSceneFitter.apply_transform(
            [terrain_slab],
            {
                "min_x": 0.0,
                "min_y": 0.0,
                "min_z": 0.0,
                "scale": 1.0,
                "offset_x": scene_origin_x,
                "offset_y": scene_origin_y,
            },
        )[0]

        meshes.insert(0, terrain_slab)

        AtlasEngine._print_xy_report(
            meshes,
            "ATLAS FINAL XY REPORT BEFORE STL WRITE",
        )
        AtlasEngine._print_mesh_debug_report(
            meshes,
            "ATLAS FINAL MESH DEBUG REPORT BEFORE STL WRITE",
        )

        print("DEBUG >>> _print_z_report çağrılıyor")
        AtlasEngine._print_z_report(
            meshes,
            "ATLAS FINAL Z REPORT BEFORE STL WRITE",
        )

        if debug:
            print(f"After terrain meshes       : {len(meshes)}")
            print(
                f"After terrain triangles    : {AtlasDebugReporter.count_triangles(meshes)}"
            )

        AtlasSTLWriter.write(meshes, output_path)

        if debug:
            AtlasDebugReporter.print_footer(
                output_path=output_path,
                xy_scale=xy_scale,
                meshes=meshes,
                buildings=scene.count_layer_meshes("buildings"),
                roads=scene.count_layer_meshes("roads"),
            )

        return {
            "output_path": output_path,
            "reader_buildings": len(raw_buildings),
            "reader_trees": len(trees),
            "reader_roads": len(roads),
            "reader_pedestrian_paths": len(pedestrian_paths),
            "scene": scene.summary(),
            "meshes": len(meshes),
            "triangles": AtlasDebugReporter.count_triangles(meshes),
            "xy_scale": xy_scale,
            "mode": "area_first_scene_first_product",
        }

    @staticmethod
    def _place_meshes_on_terrain(
        meshes,
        terrain_mesh,
        scene_origin_x,
        scene_origin_y,
    ):
        placed_meshes = []

        for mesh in meshes:
            foundation_z = AtlasFoundationEngine.calculate_foundation_z(
                mesh=mesh,
                terrain_mesh=terrain_mesh,
                scene_origin_x=scene_origin_x,
                scene_origin_y=scene_origin_y,
                embed_depth_mm=0.30,
                sample_grid=5,
            )

            placed_meshes.append(AtlasEngine._offset_mesh_z(mesh, foundation_z))

        return placed_meshes

    @staticmethod
    def _mesh_centroid_xy(mesh):
        points = []

        points.extend(mesh.get("bottom", []))
        points.extend(mesh.get("top", []))

        for triangle in mesh.get("triangles", []):
            points.extend(triangle)

        if not points:
            return 0.0, 0.0

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        return sum(xs) / len(xs), sum(ys) / len(ys)

    @staticmethod
    def _terrain_z_at_xy(terrain_mesh, x, y):
        top_points = terrain_mesh.get("top_points")

        if not top_points:
            return 0.0

        grid_size = len(top_points)
        size_mm = terrain_mesh.get("metadata", {}).get("size_mm", 200.0)

        x = max(0.0, min(size_mm, x))
        y = max(0.0, min(size_mm, y))

        gx = (x / size_mm) * (grid_size - 1)
        gy = (y / size_mm) * (grid_size - 1)

        x0 = int(gx)
        y0 = int(gy)

        x1 = min(x0 + 1, grid_size - 1)
        y1 = min(y0 + 1, grid_size - 1)

        tx = gx - x0
        ty = gy - y0

        z00 = top_points[y0][x0][2]
        z10 = top_points[y0][x1][2]
        z01 = top_points[y1][x0][2]
        z11 = top_points[y1][x1][2]

        z0 = z00 * (1.0 - tx) + z10 * tx
        z1 = z01 * (1.0 - tx) + z11 * tx

        return z0 * (1.0 - ty) + z1 * ty

    @staticmethod
    def _offset_meshes_z(meshes, offset_z):
        return [AtlasEngine._offset_mesh_z(mesh, offset_z) for mesh in meshes]

    @staticmethod
    def _offset_mesh_z(mesh, offset_z):
        if not mesh:
            return mesh

        new_mesh = {
            "bottom": [],
            "top": [],
            "walls": [],
            "triangles": [],
        }

        for key, value in mesh.items():
            if key not in new_mesh:
                new_mesh[key] = value

        for point in mesh.get("bottom", []):
            new_mesh["bottom"].append(AtlasEngine._offset_point_z(point, offset_z))

        for point in mesh.get("top", []):
            new_mesh["top"].append(AtlasEngine._offset_point_z(point, offset_z))

        for wall in mesh.get("walls", []):
            new_wall = []
            for point in wall:
                new_wall.append(AtlasEngine._offset_point_z(point, offset_z))
            new_mesh["walls"].append(tuple(new_wall))

        for triangle in mesh.get("triangles", []):
            new_triangle = []
            for point in triangle:
                new_triangle.append(AtlasEngine._offset_point_z(point, offset_z))
            new_mesh["triangles"].append(tuple(new_triangle))

        return new_mesh

    @staticmethod
    def _offset_point_z(point, offset_z):
        x, y, z = point
        return (x, y, z + offset_z)

    @staticmethod
    def _print_z_report(meshes, title):
        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)

        for index, mesh in enumerate(meshes):
            mesh_type = mesh.get("type", "unknown")
            zs = []

            for tri in mesh.get("triangles", []):
                for point in tri:
                    zs.append(point[2])

            if not zs:
                continue

            print(
                f"{index:03d} | {mesh_type:20s} | "
                f"min_z={min(zs):.3f} | max_z={max(zs):.3f}"
            )

        print("=" * 60)

    @staticmethod
    def _print_xy_report(meshes, title):
        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)

        for index, mesh in enumerate(meshes):
            mesh_type = mesh.get("type", "unknown")
            points = []

            points.extend(mesh.get("bottom", []))
            points.extend(mesh.get("top", []))

            for triangle in mesh.get("triangles", []):
                points.extend(triangle)

            if not points:
                continue

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            print(
                f"{index:03d} | {mesh_type:20s} | "
                f"x={min(xs):.2f}..{max(xs):.2f} | "
                f"y={min(ys):.2f}..{max(ys):.2f}"
            )

        print("=" * 60)

    @staticmethod
    def _print_mesh_debug_report(meshes, title):
        print("")
        print("=" * 60)
        print(title)
        print("=" * 60)

        for index, mesh in enumerate(meshes):
            mesh_type = mesh.get("type", "unknown")
            triangles = mesh.get("triangles", [])

            zs = []
            xs = []
            ys = []

            for triangle in triangles:
                for point in triangle:
                    xs.append(point[0])
                    ys.append(point[1])
                    zs.append(point[2])

            if not triangles:
                print(f"{index:03d} | {mesh_type:20s} | " f"tri=0 | no triangle data")
                continue

            print(
                f"{index:03d} | {mesh_type:20s} | "
                f"tri={len(triangles):5d} | "
                f"x={min(xs):7.2f}..{max(xs):7.2f} | "
                f"y={min(ys):7.2f}..{max(ys):7.2f} | "
                f"z={min(zs):7.2f}..{max(zs):7.2f}"
            )

        print("=" * 60)

    @staticmethod
    def _filter_meshes_inside_xy_bounds(
        meshes,
        min_x,
        max_x,
        min_y,
        max_y,
        tolerance=0.0,
    ):
        filtered = []

        for mesh in meshes:
            points = []

            points.extend(mesh.get("bottom", []))
            points.extend(mesh.get("top", []))

            for triangle in mesh.get("triangles", []):
                points.extend(triangle)

            if not points:
                continue

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            if (
                min(xs) >= min_x - tolerance
                and max(xs) <= max_x + tolerance
                and min(ys) >= min_y - tolerance
                and max(ys) <= max_y + tolerance
            ):
                filtered.append(mesh)

        return filtered

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict):
                if mesh.get("triangles"):
                    total += len(mesh["triangles"])
                elif mesh.get("faces"):
                    total += len(mesh["faces"])

        return total

    @staticmethod
    def _print_header():
        print("")
        print("=" * 60)
        print("ATLAS ENGINE AREA-FIRST / SCENE-FIRST MODE")
        print("=" * 60)

    @staticmethod
    def _print_footer(output_path, xy_scale, meshes, buildings, roads):
        print("")
        print("=" * 60)
        print("ATLAS ENGINE STL EXPORTED")
        print("=" * 60)
        print("Mode      : area_first_scene_first_product")
        print(f"XY scale  : {xy_scale:.2f}")
        print(f"Meshes    : {len(meshes)}")
        print(f"Triangles : {AtlasEngine._count_triangles(meshes)}")
        print(f"Buildings : {buildings}")
        print(f"Roads     : {roads}")
        print(output_path)
        print("=" * 60)
        print("")
