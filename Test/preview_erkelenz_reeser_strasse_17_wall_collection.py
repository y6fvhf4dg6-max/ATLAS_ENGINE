import argparse

from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_label_plate_spec import AtlasLabelPlateSpec
from CORE.atlas_label_text_spec import AtlasLabelTextSpec
from CORE.atlas_product_area_engine import AtlasProductAreaEngine
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


PBF_PATH = "Data/OSM/erkelenz-reeser-strasse-17-test.osm.pbf"

CITY_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "erkelenz_reeser_strasse_17_city_150mm_PREMIUM_V4.stl"
)

PRODUCT_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "erkelenz_reeser_strasse_17_wall_collection_170mm_PREMIUM_V4.stl"
)

MULTICOLOR_OUTPUT_DIRECTORY = (
    "OUTPUT/STL/"
    "erkelenz_reeser_strasse_17_multicolor_PREMIUM_V4"
)

MULTICOLOR_PRODUCT_NAME = (
    "erkelenz_reeser_strasse_17_170mm_PREMIUM_V4"
)

CENTER_LAT = 51.08060910
CENTER_LON = 6.29687500

PRODUCT_OUTER_SIZE_MM = 170.0
FRAME_WIDTH_MM = 10.0
FRAME_DEPTH_MM = 6.0
CITY_SIZE_MM = 150.0

SCALE_RATIO = 3000.0



class WallCollectionPreviewArguments(argparse.Namespace):
    primary_text: str
    secondary_text: str

    def validate_label_text(self) -> None:
        primary_text = str(self.primary_text).strip()
        secondary_text = str(self.secondary_text).strip()

        if secondary_text and not primary_text:
            raise ValueError(
                "secondary text requires primary text"
            )


class WallCollectionPreviewArgumentParser(
    argparse.ArgumentParser
):
    def parse_args(
        self,
        args=None,
        namespace=None,
    ):
        if namespace is None:
            namespace = WallCollectionPreviewArguments()

        return super().parse_args(
            args=args,
            namespace=namespace,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = WallCollectionPreviewArgumentParser(
        description=(
            "Generate the Erkelenz Reeser Strasse 17 wall collection preview "
            "with an optional customer label."
        ),
    )

    parser.add_argument(
        "--primary-text",
        default="",
        help="Optional primary label line.",
    )
    parser.add_argument(
        "--secondary-text",
        default="",
        help="Optional secondary label line.",
    )

    return parser


def main(argv=None):
    arguments = build_parser().parse_args(
        argv,
        namespace=WallCollectionPreviewArguments(),
    )
    arguments.validate_label_text()

    primary_text = arguments.primary_text.strip()
    secondary_text = arguments.secondary_text.strip()

    frame_spec = AtlasWallFrameSpec(
        outer_width_mm=PRODUCT_OUTER_SIZE_MM,
        outer_height_mm=PRODUCT_OUTER_SIZE_MM,
        frame_width_mm=FRAME_WIDTH_MM,
    )

    label_plate_spec = None
    label_text_spec = None

    if primary_text:
        label_plate_spec = AtlasLabelPlateSpec(
            width_mm=118.0,
            height_mm=10.0,
            depth_mm=1.2,
        )
        label_text_spec = AtlasLabelTextSpec(
            primary_text=primary_text,
            secondary_text=secondary_text,
            primary_height_mm=3.8,
            secondary_height_mm=2.4,
            depth_mm=0.6,
            max_width_mm=96.0,
            birthday_cake=False,
            home=True,
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
            172331106,
        },
    )

    multicolor_result = (
        AtlasWallCollectionMulticolorSTLExporter.export_scene(
            scene=color_scene,
            output_directory=MULTICOLOR_OUTPUT_DIRECTORY,
            product_name=MULTICOLOR_PRODUCT_NAME,
        )
    )

    print("")
    print("=" * 70)
    print("ATLAS WALL COLLECTION — ERKELENZ HOME MEMORY")
    print("=" * 70)
    print("Location            : Reeser Strasse 17, Erkelenz")
    print("Official building   : Home at Reeser Strasse 17")
    print("Address             : Reeser Strasse 17, 41812 Erkelenz")
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
    print(
        f"Multicolor profile  : "
        f"{multicolor_result['profile_name']}"
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

    print("=" * 70)


if __name__ == "__main__":
    main()
