from CORE.atlas_local_osm_reader import AtlasLocalOSMReader
from CORE.atlas_building import AtlasBuilding
from CORE.atlas_building_analyzer import AtlasBuildingAnalyzer


def main():

    pbf_path = "Data/OSM/hessen-latest.osm.pbf"

    bbox = (
        50.109500,
        8.671500,
        50.113500,
        8.676500,
    )

    data = AtlasLocalOSMReader.read(pbf_path, bbox)

    print()
    print("=" * 70)
    print("ATLAS BUILDING ANALYZER")
    print("=" * 70)

    for item in data["buildings"][:10]:

        building = AtlasBuilding(
            building_id=item["id"],
            source="LOCAL_OSM",
            geometry=item["geometry"],
            tags=item["tags"],
        )

        info = AtlasBuildingAnalyzer.analyze(building)

        print()
        print("-" * 70)

        for key, value in info.items():
            print(f"{key:15}: {value}")


if __name__ == "__main__":
    main()
