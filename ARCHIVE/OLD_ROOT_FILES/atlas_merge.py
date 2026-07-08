"""
ATLAS Engine

Module : Merge Engine
Version: 0.1
Status : Development

Purpose:
Merge existing STL files into one combined STL file.
"""

from stl import mesh
import numpy as np


INPUT_FILES = [
    "STL/ATLAS_CITY_BUILDER_v0_7_TERRAIN_OFFSET.stl",
    "STL/ATLAS_ROADS_v0_3.stl",
]

OUTPUT_FILE = "STL/ATLAS_CITY_v1_TEST.stl"


def load_stl(filename):
    print("Yükleniyor:", filename)
    return mesh.Mesh.from_file(filename)


def merge_meshes(meshes):
    print("Meshler birleştiriliyor...")

    all_data = np.concatenate(
        [single_mesh.data for single_mesh in meshes]
    )

    return mesh.Mesh(all_data.copy())


def save_stl(merged_mesh, output_file):
    merged_mesh.save(output_file)
    print("Oluşturuldu:", output_file)


def main():
    print()
    print("=" * 60)
    print("ATLAS MERGE ENGINE v0.1")
    print("=" * 60)

    meshes = []

    for filename in INPUT_FILES:
        meshes.append(load_stl(filename))

    merged = merge_meshes(meshes)

    print()
    print("Toplam üçgen sayısı:", len(merged.data))
    print()

    save_stl(merged, OUTPUT_FILE)

    print()
    print("ATLAS MERGE ENGINE v0.1 TAMAMLANDI ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()