"""
ATLAS Engine 2.0

Module : Scene Engine
Version: 1.0
Status : Architecture Foundation

Purpose:
Central scene container for ATLAS Engine.

Rule:
Engines do not export STL.
Engines add mesh data to the scene.
Only Export Engine writes final files.
"""


class AtlasSceneEngine:

    def __init__(self):
        self.points = []
        self.faces = []
        self.layers = []

    def create_scene(self):
        self.points = []
        self.faces = []
        self.layers = []

    def add_mesh(self, mesh_points, mesh_faces, layer_name="default"):
        offset = len(self.points)

        self.points.extend(mesh_points)

        for face in mesh_faces:
            self.faces.append(
                (
                    face[0] + offset,
                    face[1] + offset,
                    face[2] + offset
                )
            )

        self.layers.append(
            {
                "layer": layer_name,
                "points": len(mesh_points),
                "faces": len(mesh_faces),
            }
        )

    def statistics(self):
        return {
            "total_points": len(self.points),
            "total_faces": len(self.faces),
            "layers": self.layers,
        }

    def export_ready(self):
        return len(self.points) > 0 and len(self.faces) > 0

    def info(self):
        stats = self.statistics()

        print()
        print("=" * 60)
        print("ATLAS SCENE ENGINE v1.0")
        print("=" * 60)
        print("Toplam nokta:", stats["total_points"])
        print("Toplam yüzey:", stats["total_faces"])
        print()

        print("Katmanlar:")
        for layer in stats["layers"]:
            print(
                "-",
                layer["layer"],
                "| Points:",
                layer["points"],
                "| Faces:",
                layer["faces"]
            )

        print()
        print("Export hazır:", self.export_ready())
        print("=" * 60)


def main():
    scene = AtlasSceneEngine()

    sample_points = [
        (0, 0, 0),
        (20, 0, 0),
        (20, 20, 0),
        (0, 20, 0),
    ]

    sample_faces = [
        (0, 1, 2),
        (0, 2, 3),
    ]

    scene.add_mesh(
        sample_points,
        sample_faces,
        layer_name="test_layer"
    )

    scene.info()


if __name__ == "__main__":
    main()