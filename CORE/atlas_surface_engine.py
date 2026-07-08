# CORE/atlas_surface_engine.py

import math


class AtlasSurfaceEngine:
    """
    ATLAS Surface Engine v2.1

    Görev:
    ATLAS sahnesindeki yüzey katmanlarını merkezi olarak yönetir.

    Ana prensip:
    - Roads are recessed, not raised.
    - Yollar çıkıntılı değil, tabana gömülü / oyuk yüzeylerdir.

    Bu sürüm:
    - Road footprint üretir.
    - Road footprint'lerden düşük seviyeli recessed road surface mesh üretir.
    - Henüz gerçek boolean cut yapmaz.
    """

    BASE_PLATE_HEIGHT_MM = 0.80
    ROAD_RECESS_DEPTH_MM = 0.18

    SIDEWALK_LEVEL_MM = BASE_PLATE_HEIGHT_MM
    ROAD_LEVEL_MM = BASE_PLATE_HEIGHT_MM - ROAD_RECESS_DEPTH_MM
    WATER_LEVEL_MM = BASE_PLATE_HEIGHT_MM - 0.35
    CANAL_LEVEL_MM = BASE_PLATE_HEIGHT_MM - 0.60

    ROAD_SURFACE_THICKNESS_MM = 0.05

    DEFAULT_ROAD_WIDTHS_M = {
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

    @staticmethod
    def get_base_plate_height():
        return AtlasSurfaceEngine.BASE_PLATE_HEIGHT_MM

    @staticmethod
    def get_road_level():
        return AtlasSurfaceEngine.ROAD_LEVEL_MM

    @staticmethod
    def get_sidewalk_level():
        return AtlasSurfaceEngine.SIDEWALK_LEVEL_MM

    @staticmethod
    def get_water_level():
        return AtlasSurfaceEngine.WATER_LEVEL_MM

    @staticmethod
    def get_canal_level():
        return AtlasSurfaceEngine.CANAL_LEVEL_MM

    @staticmethod
    def build_road_footprints(roads, coordinate_engine, debug=True):
        footprints = []
        accepted = 0
        skipped = 0

        for road in roads:
            road_type = road.get("road_type") or road.get("tags", {}).get("highway")

            if road_type not in AtlasSurfaceEngine.DEFAULT_ROAD_WIDTHS_M:
                skipped += 1
                continue

            geometry = road.get("geometry", [])

            if len(geometry) < 2:
                skipped += 1
                continue

            width_m = AtlasSurfaceEngine.DEFAULT_ROAD_WIDTHS_M[road_type]
            width_mm = coordinate_engine.height_to_stl_mm(width_m)
            points = coordinate_engine.geometry_to_stl_mm(geometry)

            footprint = AtlasSurfaceEngine._build_polyline_footprint(
                points=points,
                width_mm=width_mm,
                road_type=road_type,
            )

            if footprint:
                footprints.append(footprint)
                accepted += 1
            else:
                skipped += 1

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS SURFACE ENGINE ROAD FOOTPRINT REPORT")
            print("=" * 60)
            print(f"Input roads       : {len(roads)}")
            print(f"Accepted roads    : {accepted}")
            print(f"Skipped roads     : {skipped}")
            print(f"Road footprints   : {len(footprints)}")
            print("=" * 60)
            print("")

        return footprints

    @staticmethod
    def build_recessed_road_surfaces(road_footprints, debug=True):
        meshes = []

        for footprint in road_footprints:
            mesh = AtlasSurfaceEngine._build_recessed_surface_from_footprint(footprint)

            if mesh:
                meshes.append(mesh)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS SURFACE ENGINE RECESSED ROAD REPORT")
            print("=" * 60)
            print(f"Input footprints       : {len(road_footprints)}")
            print(f"Recessed road surfaces : {len(meshes)}")
            print(
                f"Triangles              : {AtlasSurfaceEngine._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_recessed_surface_from_footprint(footprint):
        segments = footprint.get("segments", [])

        if not segments:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for segment in segments:
            polygon = segment.get("polygon", [])

            if len(polygon) != 4:
                continue

            segment_mesh = AtlasSurfaceEngine._build_recessed_segment_surface(polygon)

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
            "type": "recessed_road",
            "road_type": footprint.get("road_type"),
        }

    @staticmethod
    def _build_recessed_segment_surface(polygon):
        road_top_z = AtlasSurfaceEngine.ROAD_LEVEL_MM
        road_bottom_z = road_top_z - AtlasSurfaceEngine.ROAD_SURFACE_THICKNESS_MM

        p1, p2, p3, p4 = polygon

        bottom = [
            (p1[0], p1[1], road_bottom_z),
            (p2[0], p2[1], road_bottom_z),
            (p3[0], p3[1], road_bottom_z),
            (p4[0], p4[1], road_bottom_z),
        ]

        top = [
            (p1[0], p1[1], road_top_z),
            (p2[0], p2[1], road_top_z),
            (p3[0], p3[1], road_top_z),
            (p4[0], p4[1], road_top_z),
        ]

        triangles = []

        # bottom
        triangles.append((bottom[2], bottom[1], bottom[0]))
        triangles.append((bottom[3], bottom[2], bottom[0]))

        # top
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
            "type": "recessed_road_segment",
        }

    @staticmethod
    def _build_polyline_footprint(points, width_mm, road_type):
        if len(points) < 2:
            return None

        segments = []

        for index in range(len(points) - 1):
            segment = AtlasSurfaceEngine._build_segment_footprint(
                p1=points[index],
                p2=points[index + 1],
                width_mm=width_mm,
            )

            if segment:
                segments.append(segment)

        if not segments:
            return None

        return {
            "type": "road_footprint",
            "road_type": road_type,
            "width_mm": width_mm,
            "level_mm": AtlasSurfaceEngine.ROAD_LEVEL_MM,
            "recess_depth_mm": AtlasSurfaceEngine.ROAD_RECESS_DEPTH_MM,
            "segments": segments,
        }

    @staticmethod
    def _build_segment_footprint(p1, p2, width_mm):
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

        a = (x1 + nx * half_width, y1 + ny * half_width)
        b = (x1 - nx * half_width, y1 - ny * half_width)
        c = (x2 - nx * half_width, y2 - ny * half_width)
        d = (x2 + nx * half_width, y2 + ny * half_width)

        return {
            "type": "road_segment_footprint",
            "polygon": [a, b, c, d],
            "centerline": [p1, p2],
            "width_mm": width_mm,
        }

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict) and mesh.get("triangles"):
                total += len(mesh["triangles"])

        return total

    @staticmethod
    def describe(debug=True):
        info = {
            "base_plate_height_mm": AtlasSurfaceEngine.BASE_PLATE_HEIGHT_MM,
            "road_recess_depth_mm": AtlasSurfaceEngine.ROAD_RECESS_DEPTH_MM,
            "road_level_mm": AtlasSurfaceEngine.ROAD_LEVEL_MM,
            "sidewalk_level_mm": AtlasSurfaceEngine.SIDEWALK_LEVEL_MM,
            "water_level_mm": AtlasSurfaceEngine.WATER_LEVEL_MM,
            "canal_level_mm": AtlasSurfaceEngine.CANAL_LEVEL_MM,
            "principle": "roads_are_recessed_not_raised",
        }

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS SURFACE ENGINE REPORT")
            print("=" * 60)
            print(f"Base plate height : {info['base_plate_height_mm']:.2f} mm")
            print(f"Road recess depth : {info['road_recess_depth_mm']:.2f} mm")
            print(f"Road level        : {info['road_level_mm']:.2f} mm")
            print(f"Sidewalk level    : {info['sidewalk_level_mm']:.2f} mm")
            print(f"Water level       : {info['water_level_mm']:.2f} mm")
            print(f"Canal level       : {info['canal_level_mm']:.2f} mm")
            print(f"Principle         : {info['principle']}")
            print("=" * 60)
            print("")

        return info
