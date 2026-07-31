import math

from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine
from CORE.atlas_product_area_engine import AtlasProductAreaEngine

PBF_PATH = "Data/OSM/atakule-test.osm.pbf"
OUTPUT_PATH = "OUTPUT/STL/atakule_preview_200mm.stl"

CENTER_LAT = 39.8860
CENTER_LON = 32.8578

PRODUCT_SIZE_MM = 200.0
SCALE_RATIO = 5500.0


def _ring_measurements(ring):
    center_x = sum(point[0] for point in ring) / len(ring)
    center_y = sum(point[1] for point in ring) / len(ring)

    radii = tuple(
        math.hypot(x - center_x, y - center_y)
        for x, y, _ in ring
    )
    z_values = tuple(point[2] for point in ring)

    return {
        "radius_mm": sum(radii) / len(radii),
        "z_min_mm": min(z_values),
        "z_max_mm": max(z_values),
        "z_mean_mm": sum(z_values) / len(z_values),
    }


def _print_landmark_diagnostics(result):
    landmark_meshes = result["mesh_groups"]["landmarks"]

    print("")
    print("=" * 70)
    print("ATAKULE LANDMARK GEOMETRY DIAGNOSTICS")
    print("=" * 70)
    print(f"Landmark mesh count : {len(landmark_meshes)}")

    for mesh_index, mesh in enumerate(landmark_meshes, start=1):
        rings = tuple(mesh.get("rings", ()))
        triangles = tuple(mesh.get("triangles", ()))

        print("")
        print(f"Landmark mesh       : {mesh_index}")
        print(f"Landmark id         : {mesh.get('landmark_id')}")
        print(f"Profile             : {mesh.get('profile')}")
        print(f"Triangle count      : {len(triangles)}")
        print(f"Ring count          : {len(rings)}")

        if not rings:
            continue

        measurements = tuple(
            _ring_measurements(ring)
            for ring in rings
        )

        base_radius_mm = measurements[0]["radius_mm"]
        all_z_values = tuple(
            point[2]
            for ring in rings
            for point in ring
        )

        print(f"Footprint radius    : {base_radius_mm:.6f} mm")
        print(f"Footprint diameter  : {2.0 * base_radius_mm:.6f} mm")
        print(
            "Total STL height    : "
            f"{max(all_z_values) - min(all_z_values):.6f} mm"
        )

        print("")
        print("Observation rings:")
        for ring_index, measurement in enumerate(
            measurements,
            start=1,
        ):
            print(
                f"  Ring {ring_index}: "
                f"radius={measurement['radius_mm']:.6f} mm, "
                f"z_mean={measurement['z_mean_mm']:.6f} mm, "
                f"z_range="
                f"{measurement['z_min_mm']:.6f}.."
                f"{measurement['z_max_mm']:.6f} mm"
            )

    print("=" * 70)


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
    print("ATAKULE PREVIEW")
    print("=" * 70)
    print(result)

    _print_landmark_diagnostics(result)


if __name__ == "__main__":
    main()
