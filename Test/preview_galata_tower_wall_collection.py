from CORE.atlas_foundation_first_engine import (
    AtlasFoundationFirstEngine,
)
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


PBF_PATH = "Data/OSM/galata-tower-150mm-1-3000.osm.pbf"

CITY_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "galata_tower_square_city_150mm_1-3000.stl"
)

PRODUCT_OUTPUT_PATH = (
    "OUTPUT/STL/"
    "galata_tower_square_wall_collection_170mm_1-3000.stl"
)

MULTICOLOR_OUTPUT_DIRECTORY = (
    "OUTPUT/STL/"
    "galata_tower_square_multicolor_170mm_1-3000"
)

MULTICOLOR_PRODUCT_NAME = (
    "galata_tower_square_170mm_1-3000"
)

CENTER_LAT = 41.025636375873965
CENTER_LON = 28.974171693853222

GALATA_TOWER_SOURCE_ID = 23236783

PRODUCT_OUTER_SIZE_MM = 170.0
FRAME_WIDTH_MM = 10.0
FRAME_DEPTH_MM = 6.0
CITY_SIZE_MM = 150.0
SCALE_RATIO = 3000.0

PRIMARY_TEXT = "GALATATURM"
SECONDARY_TEXT = "ISTANBUL"


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
        debug=False,
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
    )

    multicolor_result = (
        AtlasWallCollectionMulticolorSTLExporter.export_scene(
            scene=color_scene,
            output_directory=MULTICOLOR_OUTPUT_DIRECTORY,
            product_name=MULTICOLOR_PRODUCT_NAME,
        )
    )

    mesh_groups = city_result.get(
        "mesh_groups",
        {},
    )

    landmarks = mesh_groups.get(
        "landmarks",
        [],
    )

    galata_mesh = next(
        (
            mesh
            for mesh in landmarks
            if (
                mesh.get("landmark_id")
                == GALATA_TOWER_SOURCE_ID
                or mesh.get("profile") == "galata"
            )
        ),
        None,
    )

    print("")
    print("=" * 76)
    print("ATLAS WALL COLLECTION — GALATATURM ISTANBUL")
    print("=" * 76)
    print("Location            : Galata, Istanbul")
    print("Landmark            : Galataturm")
    print(
        f"Center              : "
        f"{CENTER_LAT:.9f}, {CENTER_LON:.9f}"
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
    print(f"Primary label       : {PRIMARY_TEXT}")
    print(f"Secondary label     : {SECONDARY_TEXT}")
    print(
        f"Building meshes     : "
        f"{len(mesh_groups.get('buildings', []))}"
    )
    print(
        f"Road meshes         : "
        f"{len(mesh_groups.get('roads', []))}"
    )
    print(
        f"Tree meshes         : "
        f"{len(mesh_groups.get('trees', []))}"
    )
    print(f"Landmark meshes     : {len(landmarks)}")
    print(f"City triangles      : {city_result['triangles']}")

    if galata_mesh is None:
        print("Galata tower        : NOT FOUND")
    else:
        tower_points = [
            point
            for triangle in galata_mesh.get(
                "triangles",
                [],
            )
            for point in triangle
        ]

        print(
            f"Galata profile      : "
            f"{galata_mesh.get('profile')}"
        )
        print(
            f"Galata arches       : "
            f"{len(galata_mesh.get('galata_arch_niches', []))}"
        )

        if tower_points:
            min_z = min(
                float(point[2])
                for point in tower_points
            )
            max_z = max(
                float(point[2])
                for point in tower_points
            )

            print(
                f"Galata tower Z      : "
                f"{min_z:.3f}–{max_z:.3f} mm"
            )
            print(
                f"Galata tower height : "
                f"{max_z - min_z:.3f} mm"
            )

    print(f"City STL            : {CITY_OUTPUT_PATH}")
    print(f"Final product STL   : {PRODUCT_OUTPUT_PATH}")
    print(
        f"Multicolor parts    : "
        f"{multicolor_result['part_count']}"
    )

    for color_name, part in multicolor_result["parts"].items():
        print(
            f"  {color_name:<7}          : "
            f"{part['output_path']}"
        )

    print("=" * 76)


if __name__ == "__main__":
    main()
