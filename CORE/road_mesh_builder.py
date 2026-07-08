# CORE/road_mesh_builder.py

import math


class AtlasRoadMeshBuilder:
    """
    ATLAS Road Mesh Builder v1.1

    Görev:
    OSM highway çizgilerini yazdırılabilir yol yüzeylerine dönüştürür.

    Bu sürüm:
    - Her yol segmentini ayrı mesh yapmak yerine
    - Her road geometry için tek birleşik mesh üretir.
    """

    DEFAULT_WIDTHS_M = {
        "motorway": 12.0,
        "trunk": 10.0,
        "primary": 8.0,
        "secondary": 7.0,
        "tertiary": 6.0,
        "residential": 5.0,
        "service": 4.0,
        "living_street": 4.0,
        "unclassified": 5.0,
        "road": 5.0,
    }

    ROAD_HEIGHT_MM = 0.35

    @staticmethod
    def build_roads(roads, coordinate_engine, debug=True):
        meshes = []
        accepted = 0
        skipped = 0

        for road in roads:
            road_type = road.get("road_type") or road.get("tags", {}).get("highway")

            if road_type not in AtlasRoadMeshBuilder.DEFAULT_WIDTHS_M:
                skipped += 1
                continue

            geometry = road.get("geometry", [])

            if len(geometry) < 2:
                skipped += 1
                continue

            width_m = AtlasRoadMeshBuilder.DEFAULT_WIDTHS_M[road_type]
            width_mm = coordinate_engine.height_to_stl_mm(width_m)

            mesh = AtlasRoadMeshBuilder._build_polyline_mesh(
                geometry=geometry,
                coordinate_engine=coordinate_engine,
                width_mm=width_mm,
                road_type=road_type,
            )

            if mesh:
                meshes.append(mesh)
                accepted += 1
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS ROAD MESH BUILDER REPORT")
            print("=" * 60)
            print(f"Input roads      : {len(roads)}")
            print(f"Accepted roads   : {accepted}")
            print(f"Skipped roads    : {skipped}")
            print(f"Road meshes      : {len(meshes)}")
            print(f"Road triangles   : {AtlasRoadMeshBuilder._count_triangles(meshes)}")
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_polyline_mesh(geometry, coordinate_engine, width_mm, road_type):
        points = coordinate_engine.geometry_to_stl_mm(geometry)

        if len(points) < 2:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for index in range(len(points) - 1):
            p1 = points[index]
            p2 = points[index + 1]

            segment = AtlasRoadMeshBuilder._build_segment_mesh(
                p1=p1,
                p2=p2,
                width_mm=width_mm,
            )

            if not segment:
                continue

            bottom.extend(segment["bottom"])
            top.extend(segment["top"])
            walls.extend(segment["walls"])
            triangles.extend(segment["triangles"])

        if not triangles:
            return None

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "type": "road",
            "road_type": road_type,
        }

    @staticmethod
    def _build_segment_mesh(p1, p2, width_mm):
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1

        length = math.sqrt((dx * dx) + (dy * dy))

        if length <= 0:
            return None

        nx = -dy / length
        ny = dx / length

        half_width = width_mm / 2.0
        height = AtlasRoadMeshBuilder.ROAD_HEIGHT_MM

        a = (x1 + nx * half_width, y1 + ny * half_width)
        b = (x1 - nx * half_width, y1 - ny * half_width)
        c = (x2 - nx * half_width, y2 - ny * half_width)
        d = (x2 + nx * half_width, y2 + ny * half_width)

        bottom = [
            (a[0], a[1], 0.0),
            (b[0], b[1], 0.0),
            (c[0], c[1], 0.0),
            (d[0], d[1], 0.0),
        ]

        top = [
            (a[0], a[1], height),
            (b[0], b[1], height),
            (c[0], c[1], height),
            (d[0], d[1], height),
        ]

        triangles = []

        triangles.append((bottom[2], bottom[1], bottom[0]))
        triangles.append((bottom[3], bottom[2], bottom[0]))

        triangles.append((top[0], top[1], top[2]))
        triangles.append((top[0], top[2], top[3]))

        walls = []

        for i in range(4):
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
            "type": "road_segment",
        }

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict) and mesh.get("triangles"):
                total += len(mesh["triangles"])

        return total
