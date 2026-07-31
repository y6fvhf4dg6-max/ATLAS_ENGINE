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
from CORE.atlas_wall_collection_product_builder import (
    AtlasWallCollectionProductBuilder,
)
from CORE.atlas_wall_frame_spec import AtlasWallFrameSpec
from EXPORT.atlas_stl_writer import AtlasSTLWriter


PBF_PATH = "Data/OSM/dalyan-kaunos-workarea.osm.pbf"

CITY_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "dalyan_kaunos_city_134mm.stl"
)

PRODUCT_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "dalyan_kaunos_wall_collection_150mm.stl"
)

MULTICOLOR_OUTPUT_DIRECTORY = (
    "OUTPUT/STL/"
    "dalyan_kaunos_multicolor"
)

MULTICOLOR_PRODUCT_NAME = "dalyan_kaunos_150mm"

CENTER_LAT = 36.83501760
CENTER_LON = 28.64177419

PRODUCT_OUTER_SIZE_MM = 150.0
FRAME_WIDTH_MM = 8.0
FRAME_DEPTH_MM = 6.0
CITY_SIZE_MM = 134.0

SCALE_RATIO = 5500.0

KAUNOS_THEATRE_SOURCE_ID = 512288944
KAUNOS_THEATRE_CENTER_LAT = 36.82539937
KAUNOS_THEATRE_CENTER_LON = 28.62360716
KAUNOS_THEATRE_TARGET_X_MM = 21.5
KAUNOS_THEATRE_TARGET_Y_MM = 44.0
KAUNOS_THEATRE_SOURCE_OUTPUT_PATH = (
    "/tmp/atlas_kaunos_theatre_source_5500.stl"
)


def _mesh_points(mesh):
    return [
        point
        for triangle in mesh.get("triangles", ())
        for point in triangle
    ]


def _terrain_meshes(city_result):
    terrain = city_result["mesh_groups"].get("terrain", [])

    if isinstance(terrain, dict):
        return [terrain]

    return list(terrain)


def _relocate_kaunos_theatre(city_result):
    source_bbox = AtlasProductAreaEngine.build_bbox_from_center(
        center_lat=KAUNOS_THEATRE_CENTER_LAT,
        center_lon=KAUNOS_THEATRE_CENTER_LON,
        product_size_mm=CITY_SIZE_MM,
        scale_ratio=SCALE_RATIO,
        debug=False,
    )

    source_result = AtlasFoundationFirstEngine.generate_city_stl(
        pbf_path=PBF_PATH,
        bbox=source_bbox,
        output_path=KAUNOS_THEATRE_SOURCE_OUTPUT_PATH,
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

    theatre_meshes = [
        mesh
        for mesh in source_result["mesh_groups"]["buildings"]
        if mesh.get("source_id") == KAUNOS_THEATRE_SOURCE_ID
    ]

    if len(theatre_meshes) != 4:
        raise RuntimeError(
            "expected four Kaunos theatre component meshes, "
            f"received {len(theatre_meshes)}"
        )

    source_points = [
        point
        for mesh in theatre_meshes
        for point in _mesh_points(mesh)
    ]
    source_xs = [float(point[0]) for point in source_points]
    source_ys = [float(point[1]) for point in source_points]
    source_zs = [float(point[2]) for point in source_points]

    source_center_x = (min(source_xs) + max(source_xs)) / 2.0
    source_center_y = (min(source_ys) + max(source_ys)) / 2.0
    offset_x = KAUNOS_THEATRE_TARGET_X_MM - source_center_x
    offset_y = KAUNOS_THEATRE_TARGET_Y_MM - source_center_y

    target_min_x = min(source_xs) + offset_x
    target_max_x = max(source_xs) + offset_x
    target_min_y = min(source_ys) + offset_y
    target_max_y = max(source_ys) + offset_y

    terrain_points = [
        point
        for mesh in _terrain_meshes(city_result)
        for point in _mesh_points(mesh)
        if target_min_x <= float(point[0]) <= target_max_x
        and target_min_y <= float(point[1]) <= target_max_y
    ]

    if not terrain_points:
        raise RuntimeError(
            "no Dalyan terrain samples beneath relocated theatre"
        )

    target_foundation_z = max(
        float(point[2])
        for point in terrain_points
    )
    source_foundation_z = min(source_zs)
    offset_z = target_foundation_z - source_foundation_z

    relocated_meshes = []

    for mesh in theatre_meshes:
        relocated = AtlasWallCollectionProductBuilder._translate_mesh(
            mesh,
            offset_x,
            offset_y,
            offset_z,
        )
        relocated["composition_role"] = (
            "relocated_kaunos_ancient_theatre"
        )
        relocated["source_center_lat"] = (
            KAUNOS_THEATRE_CENTER_LAT
        )
        relocated["source_center_lon"] = (
            KAUNOS_THEATRE_CENTER_LON
        )
        relocated_meshes.append(relocated)

    city_result["mesh_groups"]["buildings"].extend(
        relocated_meshes
    )
    city_result["meshes"] += len(relocated_meshes)
    city_result["triangles"] += sum(
        len(mesh.get("triangles", ()))
        for mesh in relocated_meshes
    )

    AtlasSTLWriter.write(
        meshes=[
            mesh
            for group in city_result["mesh_groups"].values()
            for mesh in group
        ],
        output_path=CITY_OUTPUT_PATH,
        solid_name="ATLAS_DALYAN_COMPOSED_CITY",
    )

    print("")
    print("=" * 70)
    print("KAUNOS THEATRE — COMPOSITION RELOCATION")
    print("=" * 70)
    print(f"Component meshes     : {len(relocated_meshes)}")
    print(
        "Source center       : "
        f"X={source_center_x:.3f}, Y={source_center_y:.3f} mm"
    )
    print(
        "Target center       : "
        f"X={KAUNOS_THEATRE_TARGET_X_MM:.3f}, "
        f"Y={KAUNOS_THEATRE_TARGET_Y_MM:.3f} mm"
    )
    print(
        "Translation         : "
        f"dX={offset_x:.3f}, dY={offset_y:.3f}, "
        f"dZ={offset_z:.3f} mm"
    )
    print(
        "Target footprint    : "
        f"X={target_min_x:.3f}..{target_max_x:.3f}, "
        f"Y={target_min_y:.3f}..{target_max_y:.3f} mm"
    )
    print(
        "Foundation Z       : "
        f"{target_foundation_z:.3f} mm"
    )
    print("=" * 70)


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
            "Generate the Kaunos wall collection preview "
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
        label_plate_spec = AtlasLabelPlateSpec()
        label_text_spec = AtlasLabelTextSpec(
            primary_text=primary_text,
            secondary_text=secondary_text,
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
        AtlasProductPreviewMaterialProfile.dalyan_kaunos_premium_v1()
    )

    color_scene = AtlasProductColorPreviewRenderer.build_scene(
        city_result=city_result,
        frame_spec=frame_spec,
        frame_depth_mm=FRAME_DEPTH_MM,
        material_profile=material_profile,
        label_plate_spec=label_plate_spec,
        label_text_spec=label_text_spec,
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
    print("ATLAS WALL COLLECTION — KAUNOS ANCIENT THEATRE")
    print("=" * 70)
    print("Location            : Kaunos Ancient Theatre")
    print("OSM way             : 512288944")
    print("Region              : Dalyan, Muğla, Türkiye")
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
            f"  {color_name:<12}     : "
            f"{part['output_path']}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
