from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)


PBF_PATH = "Data/OSM/galata-bridge-test.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/galata_bridge_halic_scene_1_5500.stl"

BBOX = (
    41.01476522,
    28.96589663,
    41.02563478,
    28.98030337,
)

PRODUCT_SIZE_MM = 220.0
SCALE_RATIO = 5500.0


def main():
    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=BBOX,
        output_path=OUTPUT_PATH,
        target_size_mm=PRODUCT_SIZE_MM,
        bed_width_mm=256,
        bed_depth_mm=256,
        margin_mm=15,
        max_buildings=None,
        min_points=4,
        max_points=300,
        z_scale=SCALE_RATIO,
        terrain_provider_name="srtm",
        terrain_smoothing_passes=0,
        strict_input_quality=False,
        nature_provider_names=(),
        fixed_xy_scale=SCALE_RATIO,
        use_fixed_xy_scale=True,
        debug=True,
    )

    groups = result.get("mesh_groups", {})

    print()
    print("=" * 72)
    print("GALATA BRIDGE — HALIC CONTEXT SCENE")
    print("=" * 72)
    print("Output             :", OUTPUT_PATH)
    print("XY scale           :", f"1:{result['xy_scale']:.2f}")
    print(
        "Terrain size       :",
        f"{result['terrain_size_x_mm']:.2f} × "
        f"{result['terrain_size_y_mm']:.2f} mm",
    )
    print("Total triangles    :", result.get("triangles", 0))
    print("Reader buildings   :", result.get("reader_buildings", 0))
    print("Reader landmarks   :", result.get("reader_landmarks", 0))
    print("Reader coastlines  :", result.get("reader_coastlines", 0))
    print("Building meshes    :", len(groups.get("buildings", ())))
    print("Road meshes        :", len(groups.get("roads", ())))
    print("Landmark meshes    :", len(groups.get("landmarks", ())))
    print("Water meshes       :", len(groups.get("water", ())))
    print()

    for mesh in groups.get("landmarks", ()):
        tags = mesh.get("tags", {}) or {}

        print(
            "LANDMARK:",
            mesh.get("landmark_id"),
            "|",
            tags.get("name"),
            "| man_made =",
            tags.get("man_made"),
            "| wikidata =",
            tags.get("wikidata"),
            "| triangles =",
            len(mesh.get("triangles", ())),
        )

    print("=" * 72)


if __name__ == "__main__":
    main()
