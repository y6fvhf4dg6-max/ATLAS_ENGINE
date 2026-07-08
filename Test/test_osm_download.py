from DATA_CONNECTORS.OSM.osm_downloader import OSMDownloader
from DATA_CONNECTORS.OSM.osm_building_report import OSMBuildingReport
from CORE.atlas_data_manager import AtlasDataManager
from DATA_CONNECTORS.OSM.osm_building_parser import OSMBuildingParser
from CORE.atlas_extrusion_engine import AtlasExtrusionEngine
from EXPORT.atlas_stl_writer import AtlasSTLWriter
from CORE.atlas_coordinate_engine import AtlasCoordinateEngine


def main():
    # Ankara - Ulus bölgesi
    bbox = (39.9350, 32.8450, 39.9400, 32.8550)

    downloader = OSMDownloader()
    data = downloader.download_buildings(bbox)

    print()
    print("=" * 60)
    print("DOWNLOAD SUCCESS")
    print("=" * 60)
    print("Elements :", len(data["elements"]))

    report = OSMBuildingReport(data)
    report_data = report.analyze()
    report.print_report()

    manager = AtlasDataManager()
    candidate = manager.create_candidate_from_report("OSM", report_data)

    print()
    print("Candidate")
    print(candidate)

    best = manager.select_best_building_source({"OSM": candidate})

    print()
    print("=" * 60)
    print("REAL DATA DECISION")
    print("=" * 60)
    print("Best provider :", best["provider"])
    print("Score         :", best["score"])

    print()
    print("=" * 60)
    print("BUILDING PARSER")
    print("=" * 60)

    parser = OSMBuildingParser(data)
    buildings = parser.parse()

    print("Atlas Buildings :", len(buildings))
    print()

    for building in buildings[:5]:
        summary = building.summary()
        print(
            "ID:",
            summary["id"],
            "| Area:",
            summary["area_m2"],
            "| Perimeter:",
            summary["perimeter_m"],
            "| Height:",
            summary["estimated_height"],
            "| Quality:",
            summary["quality"],
        )

    selected_buildings = buildings[:5]

    all_points = []

    for building in selected_buildings:
        all_points.extend(building.geometry)

    origin_lat = sum(point[0] for point in all_points) / len(all_points)
    origin_lon = sum(point[1] for point in all_points) / len(all_points)

    coordinate_engine = AtlasCoordinateEngine(
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        xy_scale=5000,
        z_scale=500,
    )

    meshes = []

    for building in selected_buildings:
        mesh = AtlasExtrusionEngine.extrude(
            building,
            coordinate_engine=coordinate_engine,
        )
        meshes.append(mesh)

    output_file = AtlasSTLWriter.write_many(
        meshes,
        "atlas_first_5_buildings.stl",
        "atlas_first_5_buildings",
    )

    print()
    print("=" * 60)
    print("MULTI BUILDING STL CREATED")
    print("=" * 60)
    print("Buildings :", len(selected_buildings))
    print(output_file)


if __name__ == "__main__":
    main()
