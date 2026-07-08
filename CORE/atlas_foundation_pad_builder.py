# CORE/atlas_foundation_pad_builder.py


class AtlasFoundationPadBuilder:
    """
    ATLAS Foundation Pad Builder v0.1

    Görev:
    Büyük binaların altında düz platform üretmek.

    v0.1:
    - Mesh XY bounds alır
    - Etrafına margin ekler
    - Verilen z seviyesinde ince dikdörtgen platform üretir
    - Platform terrain'i kesmez, terrain üstüne oturur

    Not:
    Bu ilk sürüm genel amaçlıdır.
    Anıtkabir'e özel değildir.
    """

    DEFAULT_MARGIN_MM = 0.60
    DEFAULT_THICKNESS_MM = 0.35

    @staticmethod
    def build_pad_for_mesh(
        mesh,
        foundation_z,
        margin_mm=DEFAULT_MARGIN_MM,
        thickness_mm=DEFAULT_THICKNESS_MM,
    ):
        bounds = AtlasFoundationPadBuilder._mesh_xy_bounds(mesh)

        if bounds is None:
            return None

        min_x = bounds["min_x"] - margin_mm
        max_x = bounds["max_x"] + margin_mm
        min_y = bounds["min_y"] - margin_mm
        max_y = bounds["max_y"] + margin_mm

        bottom_z = max(0.0, foundation_z - thickness_mm)
        top_z = foundation_z

        p000 = (min_x, min_y, bottom_z)
        p100 = (max_x, min_y, bottom_z)
        p110 = (max_x, max_y, bottom_z)
        p010 = (min_x, max_y, bottom_z)

        p001 = (min_x, min_y, top_z)
        p101 = (max_x, min_y, top_z)
        p111 = (max_x, max_y, top_z)
        p011 = (min_x, max_y, top_z)

        triangles = []

        # bottom
        triangles.append((p000, p110, p100))
        triangles.append((p000, p010, p110))

        # top
        triangles.append((p001, p101, p111))
        triangles.append((p001, p111, p011))

        # front
        triangles.append((p000, p100, p101))
        triangles.append((p000, p101, p001))

        # right
        triangles.append((p100, p110, p111))
        triangles.append((p100, p111, p101))

        # back
        triangles.append((p110, p010, p011))
        triangles.append((p110, p011, p111))

        # left
        triangles.append((p010, p000, p001))
        triangles.append((p010, p001, p011))

        return {
            "type": "foundation_pad",
            "triangles": triangles,
            "metadata": {
                "foundation_z": foundation_z,
                "margin_mm": margin_mm,
                "thickness_mm": thickness_mm,
                "bounds": {
                    "min_x": min_x,
                    "max_x": max_x,
                    "min_y": min_y,
                    "max_y": max_y,
                },
            },
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
