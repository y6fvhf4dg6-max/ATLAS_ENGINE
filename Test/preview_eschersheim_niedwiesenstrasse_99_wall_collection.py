from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_product_area_engine import AtlasProductAreaEngine
from CORE.atlas_product_color_preview_png_renderer import (
    AtlasProductColorPreviewPNGRenderer,
)
from CORE.atlas_product_color_preview_renderer import (
    AtlasProductColorPreviewRenderer,
)
from CORE.atlas_product_preview_material_profile import (
    AtlasProductPreviewMaterialProfile,
)
from CORE.atlas_wall_collection_multicolor_stl_exporter import (
    AtlasWallCollectionMulticolorSTLExporter,
)
from CORE.atlas_wall_collection_stl_exporter import (
    AtlasWallCollectionSTLExporter,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec


PBF_PATH = "Data/OSM/eschersheim_niedwiesenstrasse_99_5500.osm.pbf"

CITY_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "eschersheim_niedwiesenstrasse_99_city_200mm_3000_PREMIUM.stl"
)

PRODUCT_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "eschersheim_niedwiesenstrasse_99_wall_collection_220mm_3000_PREMIUM.stl"
)

MULTICOLOR_OUTPUT_DIRECTORY = (
    "OUTPUT/STL/"
    "eschersheim_niedwiesenstrasse_99_multicolor_220mm_3000_PREMIUM"
)

MULTICOLOR_PRODUCT_NAME = (
    "eschersheim_niedwiesenstrasse_99_220mm_3000_PREMIUM"
)

PREVIEW_OUTPUT_PATH = (
    "OUTPUT/REFERENCE/"
    "eschersheim_niedwiesenstrasse_99_220mm_3000_PREMIUM.png"
)

CENTER_LAT = 50.154221659638
CENTER_LON = 8.649900133395

PRODUCT_OUTER_SIZE_MM = 220.0
FRAME_WIDTH_MM = 10.0
FRAME_DEPTH_MM = 6.0
CITY_SIZE_MM = 200.0
SCALE_RATIO = 3000.0

# Current large building footprint corresponding to the working
# historical-address hypothesis around Niedwiesenstrasse 99.
# Current OSM address: Niedwiesenstrasse 103.
HIGHLIGHTED_BUILDING_SOURCE_ID = 29054040

PRIMARY_TEXT = "NIEDWIESENSTRASSE 99"
SECONDARY_TEXT = "ESCHERSHEIM · FRANKFURT AM MAIN"


def main():
    frame_spec = AtlasWallFrameSpec(
        outer_width_mm=PRODUCT_OUTER_SIZE_MM,
        outer_height_mm=PRODUCT_OUTER_SIZE_MM,
        frame_width_mm=FRAME_WIDTH_MM,
    )

    label_plate_spec = AtlasLabelPlateSpec(
        width_mm=118.0,
        height_mm=10.0,
        depth_mm=1.2,
    )

    label_text_spec = AtlasLabelTextSpec(
        primary_text=PRIMARY_TEXT,
        secondary_text=SECONDARY_TEXT,
        primary_height_mm=3.8,
        secondary_height_mm=2.4,
        depth_mm=0.6,
        max_width_mm=96.0,
        birthday_cake=False,
        home=False,
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
        road_minimum_printable_width_mm=0.80,
        cartographic_nozzle_diameter_mm=0.40,
        cartographic_lod_level=2,
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
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
    )

    material_profile = (
        AtlasProductPreviewMaterialProfile.koeln_premium_v1()
    )

    color_scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=frame_spec,
        frame_depth_mm=FRAME_DEPTH_MM,
        material_profile=material_profile,
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
        highlighted_building_source_ids={
            HIGHLIGHTED_BUILDING_SOURCE_ID,
        },
    )

    preview_result = AtlasProductColorPreviewPNGRenderer.render(
        scene=color_scene,
        output_path=PREVIEW_OUTPUT_PATH,
        image_width_px=1200,
        image_height_px=1200,
    )

    multicolor_result = (
        AtlasWallCollectionMulticolorSTLExporter.export_scene(
            scene=color_scene,
            output_directory=MULTICOLOR_OUTPUT_DIRECTORY,
            product_name=MULTICOLOR_PRODUCT_NAME,
        )
    )

    print("")
    print("=" * 72)
    print("ATLAS WALL COLLECTION — ESCHERSHEIM / NIEDWIESENSTRASSE 99")
    print("=" * 72)
    print("Scene basis         : current / modern OSM geometry")
    print("Historical address  : Niedwiesenstrasse 99")
    print("Highlighted OSM way : 29054040")
    print("Current address     : Niedwiesenstrasse 103")
    print(
        f"Center              : "
        f"{CENTER_LAT:.12f}, {CENTER_LON:.12f}"
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
    print(f"Frame width         : {FRAME_WIDTH_MM:.2f} mm")
    print(f"Frame depth         : {FRAME_DEPTH_MM:.2f} mm")
    print(f"Scale               : 1:{city_result['xy_scale']:.2f}")
    print(f"City meshes         : {city_result['meshes']}")
    print(f"City triangles      : {city_result['triangles']}")
    print(f"Product meshes      : {product_result['mesh_count']}")
    print(f"City STL            : {CITY_OUTPUT_PATH}")
    print(f"Product STL         : {PRODUCT_OUTPUT_PATH}")
    print(
        f"Color preview       : "
        f"{preview_result['output_path']} "
        f"({preview_result['triangle_count']} triangles)"
    )
    print(
        "Highlight applied   : "
        f"{color_scene['highlighting']['applied_building_source_ids']}"
    )
    print(
        f"Multicolor parts    : "
        f"{multicolor_result['part_count']}"
    )

    for color_name, part in multicolor_result["parts"].items():
        print(
            f"  {color_name:<7}          : "
            f"{part['output_path']}"
        )

    print("=" * 72)


if __name__ == "__main__":
    main()
