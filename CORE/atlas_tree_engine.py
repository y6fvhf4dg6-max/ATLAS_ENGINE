"""
ATLAS Engine

Atlas Tree Engine v1.1
Creates simple printable tree meshes.
"""


class AtlasTreeEngine:
    @staticmethod
    def create_box(x, y, size, z_min, z_max):
        half = size / 2

        bottom = [
            (x - half, y - half, z_min),
            (x + half, y - half, z_min),
            (x + half, y + half, z_min),
            (x - half, y + half, z_min),
        ]

        top = [
            (x - half, y - half, z_max),
            (x + half, y - half, z_max),
            (x + half, y + half, z_max),
            (x - half, y + half, z_max),
        ]

        walls = []

        for i in range(4):
            walls.append(
                (
                    bottom[i],
                    bottom[(i + 1) % 4],
                    top[(i + 1) % 4],
                    top[i],
                )
            )

        return {
            "bottom": bottom,
            "top": top,
            "walls": walls,
        }

    @staticmethod
    def create_tree(x, y):
        trunk = AtlasTreeEngine.create_box(
            x=x,
            y=y,
            size=0.45,
            z_min=0.0,
            z_max=1.8,
        )

        crown = AtlasTreeEngine.create_box(
            x=x,
            y=y,
            size=1.8,
            z_min=1.8,
            z_max=4.2,
        )

        return [trunk, crown]
