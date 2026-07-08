# CORE/atlas_construction_engine.py


class AtlasConstructionEngine:
    """
    ATLAS Construction Engine v0.1

    Görev:
    Bir yapının terrain ile nasıl ilişki kuracağını sınıflandırır.

    Bu motor doğrudan mesh üretmez.
    Önce karar verir.

    Placement types:
    - normal_embed
    - cut_fill_platform
    - terrain_following
    - cliff_attached
    - landmark_custom
    """

    TYPE_NORMAL_EMBED = "normal_embed"
    TYPE_CUT_FILL_PLATFORM = "cut_fill_platform"
    TYPE_TERRAIN_FOLLOWING = "terrain_following"
    TYPE_CLIFF_ATTACHED = "cliff_attached"
    TYPE_LANDMARK_CUSTOM = "landmark_custom"

    LARGE_BUILDING_AREA_MM2 = 80.0
    STEEP_TERRAIN_DELTA_MM = 4.0
    CLIFF_TERRAIN_DELTA_MM = 10.0

    @staticmethod
    def classify_mesh(
        mesh,
        terrain_values=None,
        is_landmark=False,
        landmark_type=None,
    ):
        if is_landmark:
            return {
                "placement_type": AtlasConstructionEngine.TYPE_LANDMARK_CUSTOM,
                "reason": "landmark_detected",
                "landmark_type": landmark_type,
            }

        bounds = AtlasConstructionEngine._mesh_xy_bounds(mesh)

        if bounds is None:
            return {
                "placement_type": AtlasConstructionEngine.TYPE_NORMAL_EMBED,
                "reason": "no_bounds",
            }

        width = bounds["max_x"] - bounds["min_x"]
        depth = bounds["max_y"] - bounds["min_y"]
        area = width * depth

        terrain_delta = 0.0

        if terrain_values:
            terrain_delta = max(terrain_values) - min(terrain_values)

        if terrain_delta >= AtlasConstructionEngine.CLIFF_TERRAIN_DELTA_MM:
            return {
                "placement_type": AtlasConstructionEngine.TYPE_CLIFF_ATTACHED,
                "reason": "cliff_like_terrain",
                "area_mm2": area,
                "terrain_delta_mm": terrain_delta,
            }

        if area >= AtlasConstructionEngine.LARGE_BUILDING_AREA_MM2:
            return {
                "placement_type": AtlasConstructionEngine.TYPE_CUT_FILL_PLATFORM,
                "reason": "large_building",
                "area_mm2": area,
                "terrain_delta_mm": terrain_delta,
            }

        if terrain_delta >= AtlasConstructionEngine.STEEP_TERRAIN_DELTA_MM:
            return {
                "placement_type": AtlasConstructionEngine.TYPE_TERRAIN_FOLLOWING,
                "reason": "steep_small_building",
                "area_mm2": area,
                "terrain_delta_mm": terrain_delta,
            }

        return {
            "placement_type": AtlasConstructionEngine.TYPE_NORMAL_EMBED,
            "reason": "default_small_building",
            "area_mm2": area,
            "terrain_delta_mm": terrain_delta,
        }

    @staticmethod
    def _mesh_xy_bounds(mesh):
        points = []

        points.extend(mesh.get("bottom", []))
        points.extend(mesh.get("top", []))

        for triangle in mesh.get("triangles", []):
            points.extend(triangle)

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
