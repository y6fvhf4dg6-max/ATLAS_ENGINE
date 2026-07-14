# CORE/atlas_foundation_mesh_extruder.py

from CORE.atlas_geometry_simplifier import AtlasGeometrySimplifier
from CORE.atlas_polygon_cleaner import AtlasPolygonCleaner
from CORE.atlas_polygon_validator import AtlasPolygonValidator
from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator
from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_geometry_inspector import AtlasGeometryInspector


class AtlasFoundationMeshExtruder:
    """
    ATLAS Foundation Mesh Extruder v1.0

    Foundation-first bina üretim motoru.

    Eski sistem:
        bottom_z = 0.0

    Yeni sistem:
        bottom_z = foundation_z
        top_z    = foundation_z + height_mm
    """

    MIN_HEIGHT_MM = 2.0
    MAX_HEIGHT_MM = 35.0
    MIN_VERTICAL_PART_THICKNESS_MM = 0.80

    CASTLE_HEIGHT_MULTIPLIERS = {
        "main_tower": 2.00,
        "defensive_tower": 1.80,
        "gate_tower": 1.70,
        "chapel": 1.50,
        "castle_wing": 1.40,
        "service_building": 1.10,
        "unknown_castle_building": 1.25,
    }

    CASTLE_MIN_HEIGHTS_MM = {
        "main_tower": 18.0,
        "defensive_tower": 12.0,
        "gate_tower": 10.0,
        "chapel": 8.0,
        "castle_wing": 6.0,
        "service_building": 3.0,
        "unknown_castle_building": 5.0,
    }
    MIN_BUILDING_AREA_M2 = 20.0
    MIN_MODEL_WIDTH_MM = 1.20
    MIN_MODEL_DEPTH_MM = 1.20
    MIN_BUILDING_PART_WIDTH_MM = 1.00
    MIN_BUILDING_PART_DEPTH_MM = 1.00
    MIN_POINT_COUNT = 4

    @staticmethod
    def extrude(
        building,
        coordinate_engine,
        foundation_z,
        diagnostics=None,
    ):
        scaled_points = AtlasFoundationMeshExtruder._prepare_geometry(
            building,
            coordinate_engine,
            diagnostics=diagnostics,
        )

        if scaled_points is None:
            return None

        height_mm = AtlasFoundationMeshExtruder._calculate_height(
            building,
            coordinate_engine,
        )

        base_offset_mm = (
            AtlasFoundationMeshExtruder._calculate_base_offset(
                building,
                coordinate_engine,
            )
        )

        if base_offset_mm >= height_mm:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "invalid_vertical_range",
                base_offset_mm=base_offset_mm,
                top_offset_mm=height_mm,
            )

        flat_triangles = AtlasPolygonTriangulator.triangulate(scaled_points)

        if not flat_triangles:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "triangulation_failed",
            )

        bottom_z = foundation_z + base_offset_mm
        top_z = foundation_z + height_mm

        vertical_part_thickness_mm = top_z - bottom_z
        vertical_part_thickness_adjusted = False

        if (
            base_offset_mm > 0.0
            and vertical_part_thickness_mm
            < AtlasFoundationMeshExtruder.MIN_VERTICAL_PART_THICKNESS_MM
        ):
            bottom_z = max(
                foundation_z,
                top_z
                - AtlasFoundationMeshExtruder.MIN_VERTICAL_PART_THICKNESS_MM,
            )

            base_offset_mm = bottom_z - foundation_z
            vertical_part_thickness_mm = top_z - bottom_z
            vertical_part_thickness_adjusted = True

        bottom_points = []
        top_points = []
        wall_quads = []
        triangles = []

        for x, y in scaled_points:
            bottom_points.append((x, y, bottom_z))
            top_points.append((x, y, top_z))

        for triangle in flat_triangles:
            triangles.append(
                AtlasFoundationMeshExtruder._make_bottom_triangle(
                    triangle,
                    bottom_z,
                )
            )

            triangles.append(
                AtlasFoundationMeshExtruder._make_top_triangle(
                    triangle,
                    top_z,
                )
            )

        point_count = len(scaled_points)

        for i in range(point_count):
            bottom_1 = bottom_points[i]
            bottom_2 = bottom_points[(i + 1) % point_count]
            top_1 = top_points[i]
            top_2 = top_points[(i + 1) % point_count]

            wall_quads.append((bottom_1, bottom_2, top_2, top_1))

            triangles.extend(
                AtlasFoundationMeshExtruder._make_wall_triangles(
                    bottom_1,
                    bottom_2,
                    top_1,
                    top_2,
                )
            )

        mesh = {
            "type": "building",
            "bottom": bottom_points,
            "top": top_points,
            "walls": wall_quads,
            "triangles": triangles,
            "foundation_z": foundation_z,
            "base_offset_mm": base_offset_mm,
            "bottom_z": bottom_z,
            "top_z": top_z,
            "vertical_part_thickness_mm": (
                vertical_part_thickness_mm
            ),
            "vertical_part_thickness_adjusted": (
                vertical_part_thickness_adjusted
            ),
            "placement_mode": "foundation_first",
        }

        report = AtlasMeshValidator.report(mesh)

        if diagnostics is not None:
            diagnostics.clear()
            diagnostics.update(
                {
                    "accepted": True,
                    "reason": None,
                    "point_count": len(scaled_points),
                    "triangle_count": len(triangles),
                }
            )

        if not report["valid"]:
            print("")
            print("=" * 70)
            print("ATLAS INVALID FOUNDATION-FIRST BUILDING MESH")
            print("=" * 70)
            print(f"OSM ID        : {getattr(building, 'osm_id', 'unknown')}")
            print(f"Name          : {getattr(building, 'name', '-')}")
            print(f"Height        : {building.estimated_height:.2f} m")
            print(f"Foundation Z  : {foundation_z:.3f} mm")
            print(f"Triangles     : {report.get('triangles', 0)}")
            print(f"Open edges    : {report.get('open_edge_count', 0)}")
            print(f"Non manifold  : {report.get('non_manifold_edge_count', 0)}")
            print(f"Reason        : {report.get('reason', '-')}")
            print("=" * 70)
            print("")

        return mesh

    @staticmethod
    def _calculate_base_offset(building, coordinate_engine):
        min_height = getattr(
            building,
            "min_height",
            None,
        )

        if min_height is not None and min_height > 0.0:
            return coordinate_engine.height_to_stl_mm(
                min_height
            )

        min_level = getattr(
            building,
            "min_level",
            None,
        )

        if min_level is not None and min_level > 0:
            min_level_height_m = (
                min_level
                * 3.0
            )

            return coordinate_engine.height_to_stl_mm(
                min_level_height_m
            )

        return 0.0

    @staticmethod
    def _calculate_height(building, coordinate_engine):
        height_mm = coordinate_engine.height_to_stl_mm(
            building.estimated_height
        )

        if getattr(building, "is_castle_building", False):
            castle_profile = getattr(
                building,
                "castle_profile",
                None,
            )

            multiplier = (
                AtlasFoundationMeshExtruder
                .CASTLE_HEIGHT_MULTIPLIERS
                .get(castle_profile, 1.25)
            )

            height_mm *= multiplier

            minimum_castle_height_mm = (
                AtlasFoundationMeshExtruder
                .CASTLE_MIN_HEIGHTS_MM
                .get(castle_profile, 5.0)
            )

            height_mm = max(
                height_mm,
                minimum_castle_height_mm,
            )

        if height_mm < AtlasFoundationMeshExtruder.MIN_HEIGHT_MM:
            return AtlasFoundationMeshExtruder.MIN_HEIGHT_MM

        if height_mm > AtlasFoundationMeshExtruder.MAX_HEIGHT_MM:
            return AtlasFoundationMeshExtruder.MAX_HEIGHT_MM

        return height_mm

    @staticmethod
    def _prepare_geometry(
        building,
        coordinate_engine,
        diagnostics=None,
    ):
        points = AtlasPolygonCleaner.clean(building.geometry)

        if len(points) < AtlasFoundationMeshExtruder.MIN_POINT_COUNT:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "too_few_points_after_cleaning",
                point_count=len(points),
            )

        is_building_part = bool(
            getattr(
                building,
                "is_building_part",
                False,
            )
        )

        if (
            building.area_m2
            < AtlasFoundationMeshExtruder.MIN_BUILDING_AREA_M2
            and not is_building_part
        ):
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "building_area_below_minimum",
                area_m2=building.area_m2,
                minimum_area_m2=(
                    AtlasFoundationMeshExtruder.MIN_BUILDING_AREA_M2
                ),
            )

        points = AtlasGeometrySimplifier.simplify(points)

        if not AtlasPolygonValidator.validate(points):
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "invalid_polygon",
            )

        scaled_points = coordinate_engine.geometry_to_stl_mm(points)

        report = AtlasGeometryInspector.inspect_building(
            building,
            scaled_points,
        )

        AtlasGeometryInspector.print_report(report)

        bounds = AtlasFoundationMeshExtruder._bounds_2d(scaled_points)

        if bounds is None:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "missing_scaled_bounds",
            )

        width_mm = bounds["max_x"] - bounds["min_x"]
        depth_mm = bounds["max_y"] - bounds["min_y"]

        minimum_width_mm = (
            AtlasFoundationMeshExtruder.MIN_BUILDING_PART_WIDTH_MM
            if is_building_part
            else AtlasFoundationMeshExtruder.MIN_MODEL_WIDTH_MM
        )

        minimum_depth_mm = (
            AtlasFoundationMeshExtruder.MIN_BUILDING_PART_DEPTH_MM
            if is_building_part
            else AtlasFoundationMeshExtruder.MIN_MODEL_DEPTH_MM
        )

        if width_mm < minimum_width_mm:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "model_width_below_minimum",
                model_width_mm=width_mm,
                minimum_width_mm=minimum_width_mm,
            )

        if depth_mm < minimum_depth_mm:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "model_depth_below_minimum",
                model_depth_mm=depth_mm,
                minimum_depth_mm=minimum_depth_mm,
            )

        if len(scaled_points) < 3:
            return AtlasFoundationMeshExtruder._reject(
                diagnostics,
                "too_few_scaled_points",
                point_count=len(scaled_points),
            )

        if AtlasFoundationMeshExtruder._polygon_area(scaled_points) < 0:
            scaled_points.reverse()

        return scaled_points

    @staticmethod
    def _reject(diagnostics, reason, **details):
        if diagnostics is not None:
            diagnostics.clear()
            diagnostics.update(
                {
                    "accepted": False,
                    "reason": reason,
                }
            )
            diagnostics.update(details)

        return None

    @staticmethod
    def _bounds_2d(points):
        if not points:
            return None

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        return {
            "min_x": min(xs),
            "max_x": max(xs),
            "min_y": min(ys),
            "max_y": max(ys),
        }

    @staticmethod
    def _polygon_area(points):
        area = 0.0

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

    @staticmethod
    def _make_bottom_triangle(triangle, bottom_z):
        p1, p2, p3 = triangle

        return (
            (p3[0], p3[1], bottom_z),
            (p2[0], p2[1], bottom_z),
            (p1[0], p1[1], bottom_z),
        )

    @staticmethod
    def _make_top_triangle(triangle, top_z):
        p1, p2, p3 = triangle

        return (
            (p1[0], p1[1], top_z),
            (p2[0], p2[1], top_z),
            (p3[0], p3[1], top_z),
        )

    @staticmethod
    def _make_wall_triangles(bottom_1, bottom_2, top_1, top_2):
        return [
            (bottom_1, bottom_2, top_2),
            (bottom_1, top_2, top_1),
        ]
