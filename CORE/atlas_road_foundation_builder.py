# CORE/atlas_road_foundation_builder.py

from CORE.atlas_road_foundation_extruder import AtlasRoadFoundationExtruder


class AtlasRoadFoundationBuilder:
    """
    ATLAS Road Foundation Builder v0.1

    Görev:
    - OSM road polyline verisini terrain'e oturan road mesh'e dönüştürmek.
    - Eski road_mesh_builder.py dosyasını bozmadan Foundation-First yol hattını kurmak.
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

    @staticmethod
    def build_roads(
        roads,
        coordinate_engine,
        terrain_mesh,
        debug=True,
    ):
        meshes = []
        accepted = 0
        skipped = 0

        for road in roads:
            road_type = road.get("road_type") or road.get("tags", {}).get("highway")

            if road_type not in AtlasRoadFoundationBuilder.DEFAULT_WIDTHS_M:
                skipped += 1
                continue

            geometry = road.get("geometry", [])

            if len(geometry) < 2:
                skipped += 1
                continue

            width_m = AtlasRoadFoundationBuilder.DEFAULT_WIDTHS_M[road_type]
            width_mm = coordinate_engine.height_to_stl_mm(width_m)

            mesh = AtlasRoadFoundationBuilder._build_polyline_mesh(
                geometry=geometry,
                coordinate_engine=coordinate_engine,
                terrain_mesh=terrain_mesh,
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
            print("ATLAS ROAD FOUNDATION BUILDER REPORT")
            print("=" * 60)
            print(f"Input roads      : {len(roads)}")
            print(f"Accepted roads   : {accepted}")
            print(f"Skipped roads    : {skipped}")
            print(f"Road meshes      : {len(meshes)}")
            print(
                f"Road triangles   : {AtlasRoadFoundationBuilder._count_triangles(meshes)}"
            )
            print("=" * 60)
            print("")

        return meshes

    @staticmethod
    def _build_polyline_mesh(
        geometry,
        coordinate_engine,
        terrain_mesh,
        width_mm,
        road_type,
    ):
        points = coordinate_engine.geometry_to_stl_mm(geometry)
        points = AtlasRoadFoundationBuilder._clip_points_to_bounds(
            points=points,
            min_x=0.0,
            max_x=200.0,
            min_y=0.0,
            max_y=200.0,
        )

        if len(points) < 2:
            return None

        bottom = []
        top = []
        walls = []
        triangles = []

        for index in range(len(points) - 1):
            p1 = points[index]
            p2 = points[index + 1]

            segment = AtlasRoadFoundationExtruder.build_segment(
                p1=p1,
                p2=p2,
                terrain_mesh=terrain_mesh,
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
            "type": "road_foundation",
            "road_type": road_type,
            "placement_mode": "foundation_first",
        }

    @staticmethod
    def _clip_points_to_bounds(points, min_x, max_x, min_y, max_y):
        clipped = []

        for x, y in points:
            if min_x <= x <= max_x and min_y <= y <= max_y:
                clipped.append((x, y))

        return clipped

    @staticmethod
    def _count_triangles(meshes):
        total = 0

        for mesh in meshes:
            if isinstance(mesh, dict) and mesh.get("triangles"):
                total += len(mesh["triangles"])

        return total
