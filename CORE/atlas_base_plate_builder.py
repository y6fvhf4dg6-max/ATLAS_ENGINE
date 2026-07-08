# CORE/atlas_base_plate_builder.py


class AtlasBasePlateBuilder:
    """
    ATLAS Base Plate Builder v1.0

    Görev:
    Seçilen ürün alanı için yazdırılabilir zemin plakası üretir.

    İlk sürüm:
    - Dikdörtgen base plate üretir.
    - Modelin tüm sahnesini taşıyacak temel katmandır.
    """

    DEFAULT_HEIGHT_MM = 0.80

    @staticmethod
    def build(
        width_mm,
        depth_mm,
        height_mm=DEFAULT_HEIGHT_MM,
        origin_x=0.0,
        origin_y=0.0,
    ):
        bottom = [
            (origin_x, origin_y, 0.0),
            (origin_x + width_mm, origin_y, 0.0),
            (origin_x + width_mm, origin_y + depth_mm, 0.0),
            (origin_x, origin_y + depth_mm, 0.0),
        ]

        top = [
            (origin_x, origin_y, height_mm),
            (origin_x + width_mm, origin_y, height_mm),
            (origin_x + width_mm, origin_y + depth_mm, height_mm),
            (origin_x, origin_y + depth_mm, height_mm),
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
            "type": "base_plate",
        }
