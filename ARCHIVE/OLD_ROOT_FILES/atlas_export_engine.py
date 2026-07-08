"""
ATLAS Engine 2.0

Module : Export Engine
Version: 1.0
Status : Architecture Foundation

Purpose:
Central export system for ATLAS Engine.

Rule:
Only Export Engine writes final output files.
Other engines only generate mesh data.
"""

from atlas_stl_writer import write_stl


class AtlasExportEngine:

    def __init__(self, scene):
        self.scene = scene

    def export_stl(self, output_path, solid_name="ATLAS_MODEL"):
        if not self.scene.export_ready():
            raise ValueError("Scene export için hazır değil.")

        write_stl(
            self.scene.points,
            self.scene.faces,
            output_path,
            solid_name=solid_name
        )

        print()
        print("=" * 60)
        print("ATLAS EXPORT ENGINE v1.0")
        print("=" * 60)
        print("STL oluşturuldu:", output_path)
        print("Solid name:", solid_name)
        print("Nokta sayısı:", len(self.scene.points))
        print("Yüzey sayısı:", len(self.scene.faces))
        print("=" * 60)


def main():
    from atlas_scene_engine import AtlasSceneEngine

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
        layer_name="test_export"
    )

    exporter = AtlasExportEngine(scene)

    exporter.export_stl(
        "STL/ATLAS_EXPORT_ENGINE_TEST.stl",
        solid_name="ATLAS_EXPORT_TEST"
    )


if __name__ == "__main__":
    main()