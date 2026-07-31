from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_product_area_engine import AtlasProductAreaEngine


PBF_PATH = "Data/OSM/galata-tower-test.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/galata_tower_200mm.stl"

CENTER_LAT = 41.025636
CENTER_LON = 28.974172

PRODUCT_SIZE_MM = 200.0
SCALE_RATIO = 5500.0


def main():
    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=CENTER_LAT,
        center_lon=CENTER_LON,
        product_size_mm=PRODUCT_SIZE_MM,
        scale_ratio=SCALE_RATIO,
        debug=False,
    )

    result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=bbox,
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
        fixed_xy_scale=SCALE_RATIO,
        use_fixed_xy_scale=True,
        debug=False,
    )

    print("")
    print("=" * 70)
    print("ATLAS PERSONALIZED MAP PRODUCT")
    print("=" * 70)
    print(f"Center              : {CENTER_LAT:.8f}, {CENTER_LON:.8f}")
    print(f"Requested size      : {PRODUCT_SIZE_MM:.2f} mm")
    print(f"Requested scale     : 1:{SCALE_RATIO:.0f}")
    print(f"Output              : {OUTPUT_PATH}")
    print(f"Resolved XY scale   : 1:{result['xy_scale']:.2f}")
    print(
        "Terrain size       : "
        f"{result['terrain_size_x_mm']:.2f} × "
        f"{result['terrain_size_y_mm']:.2f} mm"
    )
    print(
        "Terrain terracing  : "
        + (
            f"{result['terrain_terrace_step_mm']:.2f} mm"
            if result.get("terrain_terraced")
            else "disabled"
        )
    )
    print("=" * 70)
    print("")
    building_meshes = (
        result.get("mesh_groups", {})
        .get("buildings", [])
    )

    roof_profile_counts = {}
    roof_geometry_counts = {}
    gable_applied_count = 0
    hipped_applied_count = 0

    for mesh in building_meshes:
        profile = mesh.get(
            "building_roof_profile",
            "unknown",
        )
        roof_profile_counts[profile] = (
            roof_profile_counts.get(profile, 0)
            + 1
        )

        geometry = mesh.get(
            "roof_geometry",
            "flat",
        )
        roof_geometry_counts[geometry] = (
            roof_geometry_counts.get(geometry, 0)
            + 1
        )

        if mesh.get(
            "building_gable_roof_applied"
        ) is True:
            gable_applied_count += 1

        if mesh.get(
            "building_hipped_roof_applied"
        ) is True:
            hipped_applied_count += 1

    quality = result.get(
        "input_quality_report",
        {},
    )
    geometry_quality = quality.get(
        "geometry",
        {},
    )
    terrain_quality = quality.get(
        "terrain",
        {},
    )

    print("PRODUCT GEOMETRY SUMMARY")
    print("-" * 70)
    print(
        f"Total triangles     : "
        f"{result.get('triangles', 0)}"
    )
    print(
        f"Building meshes     : "
        f"{len(building_meshes)}"
    )
    print(
        f"Tree meshes         : "
        f"{len(result.get('mesh_groups', {}).get('trees', []))}"
    )
    print(
        f"Green-area trees    : "
        f"{result.get('green_area_tree_samples', 0)}"
    )
    print(
        f"WorldCover grass    : "
        f"{result.get('worldcover_grass_surfaces', 0)} surfaces / "
        f"{result.get('worldcover_grass_cells', 0)} cells"
    )
    park_meshes = (
        result.get("mesh_groups", {})
        .get("parks", [])
    )

    print(
        f"Park inputs         : "
        f"{result.get('reader_parks', 0)}"
    )
    print(
        f"Park meshes         : "
        f"{len(park_meshes)}"
    )
    print(
        f"Landcover meshes    : "
        f"{len(result.get('mesh_groups', {}).get('landcover', []))}"
    )

    park_type_counts = {}

    for mesh in park_meshes:
        park_type = mesh.get(
            "park_type",
            "unknown",
        )

        park_type_counts[park_type] = (
            park_type_counts.get(park_type, 0)
            + 1
        )

    print(
        f"Park mesh types     : "
        f"{dict(sorted(park_type_counts.items()))}"
    )

    tree_source_counts = {}
    green_area_type_counts = {}

    for mesh in result.get("mesh_groups", {}).get("trees", []):
        source = mesh.get("source")

        if source is None:
            source = (
                mesh.get("tags", {})
                .get("source", "unknown")
            )

        tree_source_counts[source] = (
            tree_source_counts.get(source, 0) + 1
        )

        park_type = (
            mesh.get("tags", {})
            .get("park_type")
        )

        if park_type:
            green_area_type_counts[park_type] = (
                green_area_type_counts.get(park_type, 0) + 1
            )

    print(
        f"Tree sources        : "
        f"{dict(sorted(tree_source_counts.items()))}"
    )
    print(
        f"Green-area types    : "
        f"{dict(sorted(green_area_type_counts.items()))}"
    )
    print(
        f"Roof profiles       : "
        f"{dict(sorted(roof_profile_counts.items()))}"
    )
    print(
        f"Roof geometries     : "
        f"{dict(sorted(roof_geometry_counts.items()))}"
    )
    print(
        f"Gable roofs applied : "
        f"{gable_applied_count}"
    )
    print(
        f"Hipped roofs applied: "
        f"{hipped_applied_count}"
    )
    print(
        f"Valid OSM geometry  : "
        f"{geometry_quality.get('valid_count', 0)}/"
        f"{geometry_quality.get('total_count', 0)}"
    )
    print(
        f"Terrain coverage    : "
        f"{terrain_quality.get('coverage_percent', 0.0):.2f}%"
    )
    print(
        f"Terrain elevation   : "
        f"{result.get('terrain_min_height_m', 0.0):.2f}–"
        f"{result.get('terrain_max_height_m', 0.0):.2f} m"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
