from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_product_area_engine import AtlasProductAreaEngine
from CORE.atlas_product_color_preview_obj_exporter import (
    AtlasProductColorPreviewOBJExporter,
)
from CORE.atlas_product_color_preview_renderer import (
    AtlasProductColorPreviewRenderer,
)
from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from Test.preview_koeln_paedagogische_fakultaet_wall_collection import (
    WallCollectionPreviewArguments,
    build_parser,
)


PBF_PATH = "Data/OSM/koeln-paedagogische-fakultaet-test.osm.pbf"

CITY_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "koeln_paedagogische_fakultaet_color_obj_city_134mm.stl"
)

OBJ_OUTPUT_PATH = (
    "OUTPUT/PREVIEW/"
    "koeln_paedagogische_fakultaet_competitor_comparison_v1.obj"
)

CENTER_LAT = 50.93428235
CENTER_LON = 6.91972655

PRODUCT_OUTER_SIZE_MM = 150.0
FRAME_WIDTH_MM = 8.0
FRAME_DEPTH_MM = 6.0
CITY_SIZE_MM = 134.0

SCALE_RATIO = 5500.0


def main(argv=None):
    arguments = build_parser().parse_args(
        argv,
        namespace=WallCollectionPreviewArguments(),
    )
    arguments.validate_label_text()

    primary_text = arguments.primary_text.strip()
    secondary_text = arguments.secondary_text.strip()

    label_plate_spec = None
    label_text_spec = None

    if primary_text:
        label_plate_spec = AtlasLabelPlateSpec()
        label_text_spec = AtlasLabelTextSpec(
            primary_text=primary_text,
            secondary_text=secondary_text,
        )

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

    scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=frame_spec,
        frame_depth_mm=FRAME_DEPTH_MM,
        material_profile=(
            AtlasProductPreviewMaterialProfile.competitor_comparison_v1()
        ),
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
    )

    result = AtlasProductColorPreviewOBJExporter.export(
        scene=scene,
        output_path=OBJ_OUTPUT_PATH,
    )

    print("")
    print("=" * 70)
    print("ATLAS INTERACTIVE COLOR PREVIEW — OBJ")
    print("=" * 70)
    print(f"Profile             : {result['profile_name']}")
    print(f"Triangles           : {result['triangle_count']}")
    print(f"OBJ                 : {result['obj_path']}")
    print(f"MTL                 : {result['mtl_path']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
