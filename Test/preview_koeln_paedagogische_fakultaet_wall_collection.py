from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_product_area_engine import AtlasProductAreaEngine
from CORE.atlas_wall_collection_stl_exporter import (
    AtlasWallCollectionSTLExporter,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


PBF_PATH = "Data/OSM/koeln-paedagogische-fakultaet-test.osm.pbf"

CITY_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "koeln_paedagogische_fakultaet_city_134mm.stl"
)

PRODUCT_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "koeln_paedagogische_fakultaet_wall_collection_150mm.stl"
)

CENTER_LAT = 50.93428235
CENTER_LON = 6.91972655

PRODUCT_OUTER_SIZE_MM = 150.0
FRAME_WIDTH_MM = 8.0
FRAME_DEPTH_MM = 6.0
CITY_SIZE_MM = 134.0

SCALE_RATIO = 5500.0


def main():
    frame_spec = AtlasWallFrameSpec(
        outer_width_mm=PRODUCT_OUTER_SIZE_MM,
        outer_height_mm=PRODUCT_OUTER_SIZE_MM,
        frame_width_mm=FRAME_WIDTH_MM,
    )

    bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=CENTER_LAT,
        center_lon=CENTER_LON,
        product_size_mm=CITY_SIZE_MM,
        scale_ratio=SCALE_RATIO,
        debug=False,
    )

    city_result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=bbox,
        output_path=CITY_OUTPUT_PATH,
        target_size_mm=CITY_SIZE_MM,
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

    print(
        "Generated terrain    : "
        f"{city_result['terrain_size_x_mm']:.6f} × "
        f"{city_result['terrain_size_y_mm']:.6f} mm"
    )
    print(
        "Frame opening        : "
        f"{frame_spec.inner_width_mm:.6f} × "
        f"{frame_spec.inner_height_mm:.6f} mm"
    )

    product_result = AtlasWallCollectionSTLExporter.export(
        city_result=city_result,
        output_path=PRODUCT_OUTPUT_PATH,
        frame_spec=frame_spec,
        frame_depth_mm=FRAME_DEPTH_MM,
    )

    print("")
    print("=" * 70)
    print("ATLAS WALL COLLECTION — FIRST REAL PRODUCT")
    print("=" * 70)
    print("Location            : Pädagogische Fakultät Köln")
    print("Official building   : 216")
    print("Address             : Gronewaldstraße 2, 50931 Köln")
    print(
        f"Center              : "
        f"{CENTER_LAT:.8f}, {CENTER_LON:.8f}"
    )
    print(
        f"Outer product       : "
        f"{product_result['outer_width_mm']:.2f} × "
        f"{product_result['outer_height_mm']:.2f} mm"
    )
    print(
        f"Map opening         : "
        f"{product_result['opening_width_mm']:.2f} × "
        f"{product_result['opening_height_mm']:.2f} mm"
    )
    print(
        f"Terrain             : "
        f"{city_result['terrain_size_x_mm']:.2f} × "
        f"{city_result['terrain_size_y_mm']:.2f} mm"
    )
    print(f"Frame width         : {FRAME_WIDTH_MM:.2f} mm")
    print(f"Frame depth         : {FRAME_DEPTH_MM:.2f} mm")
    print(f"Scale               : 1:{city_result['xy_scale']:.2f}")
    print(f"City meshes         : {city_result['meshes']}")
    print(f"Product meshes      : {product_result['mesh_count']}")
    print(f"City triangles      : {city_result['triangles']}")
    print(f"Intermediate STL    : {CITY_OUTPUT_PATH}")
    print(f"Final product STL   : {PRODUCT_OUTPUT_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
