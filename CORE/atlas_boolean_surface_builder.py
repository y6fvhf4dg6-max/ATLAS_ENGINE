# CORE/atlas_boolean_surface_builder.py

from CORE.atlas_polygon_triangulator import AtlasPolygonTriangulator


class AtlasBooleanSurfaceBuilder:
    """
    ATLAS Boolean Surface Builder v1.3

    Bu sürüm:
    - Eski segment bazlı groove sistemini korur.
    - Yeni polygon bazlı groove sistemi ekler.
    - Road polygons -> tek parça groove mesh üretir.

    Hedef:
    Segment birleşimlerindeki üçgen fan / kapak problemini azaltmak.
    """

    BASE_TOP_Z = 0.80
    ROAD_BOTTOM_Z = 0.62

    @staticmethod
    def analyze_recess_plan(base_plate, road_footprints, debug=True):
        footprint_count = len(road_footprints)
        segment_count = 0

        for footprint in road_footprints:
            segment_count += len(footprint.get("segments", []))

        plan = {
            "type": "boolean_recess_plan",
            "base_plate_type": base_plate.get("type", "unknown"),
            "road_footprints": footprint_count,
            "road_segments": segment_count,
            "operation": "base_plate_minus_road_footprints",
            "status": "analysis_only",
        }

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS BOOLEAN SURFACE BUILDER REPORT")
            print("=" * 60)
            print(f"Base plate type : {plan['base_plate_type']}")
            print(f"Road footprints : {plan['road_footprints']}")
            print(f"Road segments   : {plan['road_segments']}")
            print(f"Operation       : {plan['operation']}")
            print(f"Status          : {plan['status']}")
            print("=" * 60)
            print("")

        return plan

    @staticmethod
    def build_road_polygon_groove_meshes(road_polygons, debug=True):
        meshes = []

        for road_polygon in road_polygons:
            mesh = AtlasBooleanSurfaceBuilder._build_groove_from_road_polygon(
                road_polygon
            )

            if mesh:
                meshes.append(mesh)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ROAD POLYGON GROOVE BUILDER REPORT")
            print("=" * 60)
            print(f"Input road polygons : {len(road_polygons)}")
            print(f"Groove meshes       : {len(meshes)}")
            print(
                f"Triangles           : {AtlasBooleanSurfaceBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_groove_from_road_polygon(road_polygon):
        points = road_polygon.get("points", [])

        if len(points) < 3:
            return None

        flat_triangles = AtlasPolygonTriangulator.triangulate(points)

        if not flat_triangles:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for x, y in points:
            bottom.append((x, y, AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z))
            top.append((x, y, AtlasBooleanSurfaceBuilder.BASE_TOP_Z))

        # Bottom surface
        for triangle in flat_triangles:
            p1, p2, p3 = triangle
            triangles.append(
                (
                    (p3[0], p3[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
                    (p2[0], p2[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
                    (p1[0], p1[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
                )
            )

        # Top opening surface
        for triangle in flat_triangles:
            p1, p2, p3 = triangle
            triangles.append(
                (
                    (p1[0], p1[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
                    (p2[0], p2[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
                    (p3[0], p3[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
                )
            )

        # Outer walls
        point_count = len(points)

        for index in range(point_count):
            next_index = (index + 1) % point_count

            b1 = bottom[index]
            b2 = bottom[next_index]
            t1 = top[index]
            t2 = top[next_index]

            walls.append((b1, b2, t2, t1))

            triangles.append((b1, b2, t2))
            triangles.append((b1, t2, t1))

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "type": "road_polygon_groove",
            "road_type": road_polygon.get("road_type"),
        }

    @staticmethod
    def build_road_groove_meshes(road_footprints, debug=True):
        """
        Eski segment bazlı sistem.
        Debug / karşılaştırma için korunur.
        """
        meshes = []

        for footprint in road_footprints:
            mesh = AtlasBooleanSurfaceBuilder._build_groove_from_footprint(footprint)

            if mesh:
                meshes.append(mesh)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ROAD GROOVE BUILDER REPORT")
            print("=" * 60)
            print(f"Input footprints : {len(road_footprints)}")
            print(f"Groove meshes    : {len(meshes)}")
            print(
                f"Triangles        : {AtlasBooleanSurfaceBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_groove_from_footprint(footprint):
        segments = footprint.get("segments", [])

        if not segments:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        last_index = len(segments) - 1

        for index, segment in enumerate(segments):
            polygon = segment.get("polygon", [])

            if len(polygon) != 4:
                continue

            include_start_cap = index == 0
            include_end_cap = index == last_index

            segment_mesh = AtlasBooleanSurfaceBuilder._build_groove_segment(
                polygon=polygon,
                include_start_cap=include_start_cap,
                include_end_cap=include_end_cap,
            )

            if not segment_mesh:
                continue

            bottom.extend(segment_mesh["bottom"])
            top.extend(segment_mesh["top"])
            walls.extend(segment_mesh["walls"])
            triangles.extend(segment_mesh["triangles"])

        if not triangles:
            return None

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "type": "road_groove",
            "road_type": footprint.get("road_type"),
        }

    @staticmethod
    def _build_groove_segment(polygon, include_start_cap, include_end_cap):
        p1, p2, p3, p4 = polygon

        bottom = [
            (p1[0], p1[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
            (p2[0], p2[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
            (p3[0], p3[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
            (p4[0], p4[1], AtlasBooleanSurfaceBuilder.ROAD_BOTTOM_Z),
        ]

        top = [
            (p1[0], p1[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
            (p2[0], p2[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
            (p3[0], p3[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
            (p4[0], p4[1], AtlasBooleanSurfaceBuilder.BASE_TOP_Z),
        ]

        triangles = []
        walls = []

        # Road bottom surface
        triangles.append((bottom[0], bottom[1], bottom[2]))
        triangles.append((bottom[0], bottom[2], bottom[3]))

        edges_to_build = [1, 3]

        if include_start_cap:
            edges_to_build.append(0)

        if include_end_cap:
            edges_to_build.append(2)

        for i in edges_to_build:
            j = (i + 1) % 4

            wall = (
                bottom[i],
                bottom[j],
                top[j],
                top[i],
            )

            walls.append(wall)

            triangles.append((bottom[i], bottom[j], top[j]))
            triangles.append((bottom[i], top[j], top[i]))

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "type": "road_groove_segment",
        }

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict) and mesh.get("triangles"):
                total += len(mesh["triangles"])

        return total
