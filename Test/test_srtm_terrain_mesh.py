# Test/test_srtm_terrain_mesh.py

from CORE.atlas_srtm_provider import AtlasSRTMProvider
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator
from EXPORT.atlas_stl_writer import AtlasSTLWriter


def main():
    provider = AtlasSRTMProvider(
        data_dir="Data/TERRAIN/SRTM",
        debug=False,
    )

    bbox = (
        39.92011328853755,
        32.83050142502186,
        39.929994711462456,
        32.84338657497815,
    )

    mesh = AtlasTerrainMeshGenerator.build_closed_slab_mesh(
        terrain_provider=provider,
        bbox=bbox,
        size_mm=200.0,
        grid_size=25,
        z_scale=5500.0,
        base_z=0.80,
        bottom_z=0.0,
    )

    output_path = "OUTPUT/STL/terrain_test.stl"

    AtlasSTLWriter.write(
        meshes=[mesh],
        output_path=output_path,
        solid_name="ATLAS_TERRAIN_CLOSED_TEST",
    )

    metadata = mesh["metadata"]

    print("")
    print("=" * 60)
    print("ATLAS SRTM TERRAIN CLOSED SLAB TEST")
    print("=" * 60)
    print(f"Grid size  : {metadata['grid_size']} x {metadata['grid_size']}")
    print(f"Min height : {metadata['min_height_m']} m")
    print(f"Max height : {metadata['max_height_m']} m")
    print(f"Delta      : {metadata['delta_height_m']} m")
    print(f"Closed     : {metadata['closed']}")
    print(f"Triangles  : {metadata['triangle_count']}")
    print(f"Output     : {output_path}")
    print("=" * 60)
    print("")


if __name__ == "__main__":
    main()
