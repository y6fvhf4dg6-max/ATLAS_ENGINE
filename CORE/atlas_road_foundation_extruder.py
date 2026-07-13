# CORE/atlas_road_foundation_extruder.py

import math

from CORE.atlas_foundation_sampler import AtlasFoundationSampler


class AtlasRoadFoundationExtruder:
    """
    ATLAS Road Foundation Extruder v0.1

    Road mesh artık z=0 üzerinde doğmaz.
    Yol segmentleri terrain yüksekliğini örnekleyerek doğar.
    """

    DEFAULT_ROAD_HEIGHT_MM = 0.40

    @staticmethod
    def build_segment(
        p1,
        p2,
        terrain_mesh,
        width_mm,
        road_height_mm=DEFAULT_ROAD_HEIGHT_MM,
        include_start_cap=True,
        include_end_cap=True,
    ):
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

        corners_2d = [a, b, c, d]

        bottom = []
        top = []

        for x, y in corners_2d:
            terrain_z = AtlasFoundationSampler.terrain_z_at_xy(
                terrain_mesh=terrain_mesh,
                x=x,
                y=y,
            )

            bottom_z = terrain_z
            top_z = terrain_z + road_height_mm

            bottom.append((x, y, bottom_z))
            top.append((x, y, top_z))

        triangles = []

        triangles.append((bottom[2], bottom[1], bottom[0]))
        triangles.append((bottom[3], bottom[2], bottom[0]))

        triangles.append((top[0], top[1], top[2]))
        triangles.append((top[0], top[2], top[3]))

        walls = []

        for i in range(4):
            if i == 0 and not include_start_cap:
                continue

            if i == 2 and not include_end_cap:
                continue

            j = (i + 1) % 4

            wall = (
                bottom[i],
                bottom[j],
                top[j],
                top[i],
            )

            walls.append(wall)

            triangles.append(
                (
                    bottom[i],
                    bottom[j],
                    top[j],
                )
            )

            triangles.append(
                (
                    bottom[i],
                    top[j],
                    top[i],
                )
            )

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
            "triangles": triangles,
            "type": "road_foundation_segment",
        }
