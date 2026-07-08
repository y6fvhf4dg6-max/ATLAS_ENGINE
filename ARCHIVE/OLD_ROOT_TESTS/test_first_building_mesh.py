"""
ATLAS Engine

Module : First Building STL Test
Version: 0.4
Status : Development

Purpose:
Finds the first valid OSM building, triangulates it,
extrudes it into 3D, and writes it as an STL file.
"""

from atlas_area import calculate_area_bounds
from atlas_buildings import fetch_buildings_from_osm, is_building_way
from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT
from atlas_extrusion import extrusion_info
from atlas_geocoder import geocode_address
from atlas_geometry import (
    build_node_lookup,
    resolve_node_coordinates,
)
from atlas_mesh_builder import triangulate_polygon
from atlas_model_space import coordinates_to_model_points
from atlas_stl_writer import stl_writer_info


ADDRESS = "Frankfurt Römer"
TEST_AREA_SIZE_M = 500
MODEL_SIZE_MM = 200
TEST_BUILDING_HEIGHT_MM = 10
OUTPUT_PATH = "STL/ATLAS_FIRST_BUILDING.stl"


def main():
    product = PRODUCT_PROFILES[DEFAULT_PRODUCT]

    latitude, longitude = geocode_address(ADDRESS)

    bounds = calculate_area_bounds(
        latitude,
        longitude,
        TEST_AREA_SIZE_M
    )

    print("ATLAS First Building STL Test v0.4")
    print("----------------------------------")
    print("Adres :", ADDRESS)
    print("Ürün  :", product["name"])
    print("Test alanı:", TEST_AREA_SIZE_M, "m x", TEST_AREA_SIZE_M, "m")
    print("Model boyutu:", MODEL_SIZE_MM, "mm")
    print("Çıktı:", OUTPUT_PATH)
    print()

    print("OSM verisi indiriliyor...")

    osm_data = fetch_buildings_from_osm(bounds)
    node_lookup = build_node_lookup(osm_data)

    checked_count = 0
    skipped_count = 0

    for element in osm_data["elements"]:
        if not is_building_way(element):
            continue

        checked_count += 1

        coordinates = resolve_node_coordinates(
            element["nodes"],
            node_lookup
        )

        model_points = coordinates_to_model_points(
            coordinates,
            bounds,
            MODEL_SIZE_MM
        )

        try:
            print()
            print("Bina deneniyor")
            print("OSM ID :", element["id"])
            print("Tür    :", element["tags"]["building"])
            print("Node   :", len(element["nodes"]))

            polygon, vertices, triangles = triangulate_polygon(model_points)

            print("Polygon alanı:", round(polygon.area, 2), "mm²")
            print("Vertex sayısı:", len(vertices))
            print("Triangle sayısı:", len(triangles) // 3)

            points_3d, faces = extrusion_info(
                vertices,
                triangles,
                TEST_BUILDING_HEIGHT_MM
            )

            stl_writer_info(
                points_3d,
                faces,
                OUTPUT_PATH
            )

            print()
            print("ATLAS_FIRST_BUILDING.stl OLUŞTU ✅")
            print("OSM ID :", element["id"])
            print("Tür    :", element["tags"]["building"])
            print("3D nokta sayısı :", len(points_3d))
            print("3D yüzey sayısı :", len(faces))
            print("Denenen bina sayısı :", checked_count)
            print("Atlanan bina sayısı :", skipped_count)
            return

        except Exception as error:
            skipped_count += 1
            print("Geçersiz / atlandı:", error)

    print()
    print("Geçerli bina bulunamadı.")
    print("Denenen bina sayısı :", checked_count)
    print("Atlanan bina sayısı :", skipped_count)


if __name__ == "__main__":
    main()