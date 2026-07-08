"""
ATLAS Engine

Module : First City Buildings STL Test
Version: 0.1
Status : Development

Purpose:
Converts multiple valid OSM buildings into one combined STL file.
"""

from atlas_area import calculate_area_bounds
from atlas_buildings import fetch_buildings_from_osm, is_building_way
from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT
from atlas_extrusion import extrude_mesh
from atlas_geocoder import geocode_address
from atlas_geometry import build_node_lookup, resolve_node_coordinates
from atlas_mesh_builder import triangulate_polygon
from atlas_model_space import coordinates_to_model_points
from atlas_stl_writer import stl_writer_info


ADDRESS = "Frankfurt Römer"
TEST_AREA_SIZE_M = 500
MODEL_SIZE_MM = 200
BUILDING_HEIGHT_MM = 8
MAX_BUILDINGS = 100

OUTPUT_PATH = "STL/ATLAS_FIRST_CITY_BUILDINGS.stl"


def main():
    product = PRODUCT_PROFILES[DEFAULT_PRODUCT]

    latitude, longitude = geocode_address(ADDRESS)

    bounds = calculate_area_bounds(
        latitude,
        longitude,
        TEST_AREA_SIZE_M
    )

    print("ATLAS First City Buildings STL Test v0.1")
    print("----------------------------------------")
    print("Adres :", ADDRESS)
    print("Ürün  :", product["name"])
    print("Alan  :", TEST_AREA_SIZE_M, "m x", TEST_AREA_SIZE_M, "m")
    print("Model :", MODEL_SIZE_MM, "mm")
    print("Çıktı :", OUTPUT_PATH)
    print()

    print("OSM verisi indiriliyor...")

    osm_data = fetch_buildings_from_osm(bounds)
    node_lookup = build_node_lookup(osm_data)

    all_points_3d = []
    all_faces = []

    checked_count = 0
    valid_count = 0
    skipped_count = 0

    for element in osm_data["elements"]:
        if not is_building_way(element):
            continue

        checked_count += 1

        if valid_count >= MAX_BUILDINGS:
            break

        try:
            coordinates = resolve_node_coordinates(
                element["nodes"],
                node_lookup
            )

            model_points = coordinates_to_model_points(
                coordinates,
                bounds,
                MODEL_SIZE_MM
            )

            polygon, vertices, triangles = triangulate_polygon(model_points)

            points_3d, faces = extrude_mesh(
                vertices,
                triangles,
                BUILDING_HEIGHT_MM
            )

            offset = len(all_points_3d)

            all_points_3d.extend(points_3d)

            for face in faces:
                all_faces.append((
                    face[0] + offset,
                    face[1] + offset,
                    face[2] + offset,
                ))

            valid_count += 1

            print(
                "OK:",
                valid_count,
                "| OSM:",
                element["id"],
                "| Tür:",
                element["tags"]["building"],
                "| Alan:",
                round(polygon.area, 2),
                "mm²"
            )

        except Exception as error:
            skipped_count += 1
            print("Atlandı:", element.get("id"), "|", error)

    print()
    print("Şehir bina mesh özeti")
    print("---------------------")
    print("Denenen bina sayısı :", checked_count)
    print("Geçerli bina sayısı :", valid_count)
    print("Atlanan bina sayısı :", skipped_count)
    print("3D nokta sayısı     :", len(all_points_3d))
    print("3D yüzey sayısı     :", len(all_faces))
    print()

    if not all_points_3d or not all_faces:
        print("STL oluşturulamadı.")
        return

    stl_writer_info(
        all_points_3d,
        all_faces,
        OUTPUT_PATH
    )

    print()
    print("ATLAS_FIRST_CITY_BUILDINGS.stl OLUŞTU ✅")


if __name__ == "__main__":
    main()