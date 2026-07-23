"""
ATLAS Engine

Atlas Mesh Builder v3.4
Creates printable closed triangle meshes from AtlasBuilding objects.

v3.4:
- Adds foundation_z support.
- Buildings can now be born directly on a foundation level.
"""

from CORE.atlas_geometry_simplifier import AtlasGeometrySimplifier
from CORE.atlas_polygon_cleaner import AtlasPolygonCleaner
from CORE.atlas_polygon_validator import AtlasPolygonValidator
from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator
from CORE.atlas_mesh_validator import AtlasMeshValidator
from CORE.atlas_geometry_inspector import AtlasGeometryInspector


class AtlasMeshBuilder:
    MIN_HEIGHT_MM = 2.0
    MAX_HEIGHT_MM = 35.0
    MIN_BUILDING_AREA_M2 = 20.0
    MIN_MODEL_WIDTH_MM = 1.20
    MIN_MODEL_DEPTH_MM = 1.20
    MIN_BUILDING_PART_WIDTH_MM = 1.00
    MIN_BUILDING_PART_DEPTH_MM = 1.00
    MIN_POINT_COUNT = 4

    @staticmethod
    def calculate_height(building, coordinate_engine):
        height_mm = coordinate_engine.height_to_stl_mm(building.estimated_height)

        if height_mm < AtlasMeshBuilder.MIN_HEIGHT_MM:
            return AtlasMeshBuilder.MIN_HEIGHT_MM

        if height_mm > AtlasMeshBuilder.MAX_HEIGHT_MM:
            return AtlasMeshBuilder.MAX_HEIGHT_MM

        return height_mm

    @staticmethod
    def polygon_area(points):
        area = 0.0

        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]

            area += x1 * y2
            area -= x2 * y1

        return area / 2.0

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
    def prepare_geometry(
        building,
        coordinate_engine,
        diagnostics=None,
        debug=False,
    ):
        points = AtlasPolygonCleaner.clean(building.geometry)

        if len(points) < AtlasMeshBuilder.MIN_POINT_COUNT:
            return AtlasMeshBuilder._reject(
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
            < AtlasMeshBuilder.MIN_BUILDING_AREA_M2
            and not is_building_part
        ):
            return AtlasMeshBuilder._reject(
                diagnostics,
                "building_area_below_minimum",
                area_m2=building.area_m2,
                minimum_area_m2=AtlasMeshBuilder.MIN_BUILDING_AREA_M2,
            )

        points = AtlasGeometrySimplifier.simplify(points)

        if not AtlasPolygonValidator.validate(points):
            return AtlasMeshBuilder._reject(
                diagnostics,
                "invalid_polygon",
            )

        scaled_points = coordinate_engine.geometry_to_stl_mm(points)

        report = AtlasGeometryInspector.inspect_building(
            building,
            scaled_points,
        )

        if debug:
            AtlasGeometryInspector.print_report(report)

        bounds = AtlasMeshBuilder._bounds_2d(scaled_points)

        if bounds is None:
            return AtlasMeshBuilder._reject(
                diagnostics,
                "missing_scaled_bounds",
            )

        minimum_width_mm = (
            AtlasMeshBuilder.MIN_BUILDING_PART_WIDTH_MM
            if is_building_part
            else AtlasMeshBuilder.MIN_MODEL_WIDTH_MM
        )

        minimum_depth_mm = (
            AtlasMeshBuilder.MIN_BUILDING_PART_DEPTH_MM
            if is_building_part
            else AtlasMeshBuilder.MIN_MODEL_DEPTH_MM
        )

        if AtlasMeshBuilder._is_minaret(building):
            scaled_points = (
                AtlasMeshBuilder
                ._expand_to_minimum_dimensions(
                    points=scaled_points,
                    minimum_width_mm=minimum_width_mm,
                    minimum_depth_mm=minimum_depth_mm,
                )
            )

            bounds = AtlasMeshBuilder._bounds_2d(
                scaled_points
            )

        width_mm = bounds["max_x"] - bounds["min_x"]
        depth_mm = bounds["max_y"] - bounds["min_y"]

        if width_mm < minimum_width_mm:
            return AtlasMeshBuilder._reject(
                diagnostics,
                "model_width_below_minimum",
                model_width_mm=width_mm,
                minimum_width_mm=minimum_width_mm,
            )

        if depth_mm < minimum_depth_mm:
            return AtlasMeshBuilder._reject(
                diagnostics,
                "model_depth_below_minimum",
                model_depth_mm=depth_mm,
                minimum_depth_mm=minimum_depth_mm,
            )

        if len(scaled_points) < 3:
            return AtlasMeshBuilder._reject(
                diagnostics,
                "too_few_scaled_points",
                point_count=len(scaled_points),
            )

        if AtlasMeshBuilder.polygon_area(scaled_points) < 0:
            scaled_points.reverse()

        return scaled_points

    @staticmethod
    def _is_minaret(building):
        tags = getattr(
            building,
            "tags",
            {},
        ) or {}

        return (
            tags.get("tower:type") == "minaret"
            and (
                tags.get("man_made") == "tower"
                or tags.get("building:part") is not None
            )
        )

    @staticmethod
    def _expand_to_minimum_dimensions(
        points,
        minimum_width_mm,
        minimum_depth_mm,
    ):
        bounds = AtlasMeshBuilder._bounds_2d(
            points
        )

        if bounds is None:
            return points

        width_mm = bounds["max_x"] - bounds["min_x"]
        depth_mm = bounds["max_y"] - bounds["min_y"]

        if width_mm <= 0.0 or depth_mm <= 0.0:
            return points

        scale_x = max(
            1.0,
            minimum_width_mm / width_mm,
        )
        scale_y = max(
            1.0,
            minimum_depth_mm / depth_mm,
        )

        if scale_x == 1.0 and scale_y == 1.0:
            return points

        center_x = (
            bounds["min_x"] + bounds["max_x"]
        ) / 2.0
        center_y = (
            bounds["min_y"] + bounds["max_y"]
        ) / 2.0

        return [
            (
                center_x + (x - center_x) * scale_x,
                center_y + (y - center_y) * scale_y,
            )
            for x, y in points
        ]

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
    def _make_bottom_triangle(triangle, foundation_z):
        p1, p2, p3 = triangle

        return (
            (p3[0], p3[1], foundation_z),
            (p2[0], p2[1], foundation_z),
            (p1[0], p1[1], foundation_z),
        )

    @staticmethod
    def _make_top_triangle(triangle, height_mm, foundation_z):
        p1, p2, p3 = triangle

        top_z = foundation_z + height_mm

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

    @staticmethod
    def build_mesh(
        building,
        coordinate_engine,
        foundation_z=0.0,
        diagnostics=None,
        debug=False,
    ):
        scaled_points = AtlasMeshBuilder.prepare_geometry(
            building,
            coordinate_engine,
            diagnostics=diagnostics,
            debug=debug,
        )

        if scaled_points is None:
            return None

        height_mm = AtlasMeshBuilder.calculate_height(
            building,
            coordinate_engine,
        )

        flat_triangles = AtlasPolygonTriangulator.triangulate(scaled_points)

        if not flat_triangles:
            return AtlasMeshBuilder._reject(
                diagnostics,
                "triangulation_failed",
            )

        bottom_points = []
        top_points = []
        wall_quads = []
        triangles = []

        top_z = foundation_z + height_mm

        for x, y in scaled_points:
            bottom_points.append((x, y, foundation_z))
            top_points.append((x, y, top_z))

        for triangle in flat_triangles:
            triangles.append(
                AtlasMeshBuilder._make_bottom_triangle(
                    triangle,
                    foundation_z,
                )
            )

            triangles.append(
                AtlasMeshBuilder._make_top_triangle(
                    triangle,
                    height_mm,
                    foundation_z,
                )
            )

        point_count = len(scaled_points)

        for i in range(point_count):
            bottom_1 = bottom_points[i]
            bottom_2 = bottom_points[(i + 1) % point_count]
            top_1 = top_points[i]
            top_2 = top_points[(i + 1) % point_count]

            wall_quads.append((bottom_1, bottom_2, top_2, top_1))

            wall_triangles = AtlasMeshBuilder._make_wall_triangles(
                bottom_1,
                bottom_2,
                top_1,
                top_2,
            )

            triangles.extend(wall_triangles)

        mesh = {
            "bottom": bottom_points,
            "top": top_points,
            "walls": wall_quads,
            "triangles": triangles,
            "foundation_z": foundation_z,
        }

        report = AtlasMeshValidator.report(mesh)

        if not report["valid"]:
            print("")
            print("=" * 70)
            print("ATLAS INVALID BUILDING MESH")
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
