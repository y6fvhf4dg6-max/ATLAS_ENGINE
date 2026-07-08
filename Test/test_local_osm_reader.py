from CORE.atlas_local_osm_reader import AtlasLocalOSMReader


def main():
    pbf_path = "Data/OSM/hessen-latest.osm.pbf"

    bbox = (
        50.1000,
        8.6500,
        50.1300,
        8.6900,
    )

    data = AtlasLocalOSMReader.read(pbf_path, bbox)

    print()
    print("=" * 60)
    print("LOCAL OSM DATABASE TEST")
    print("=" * 60)
    print("Buildings:", len(data["buildings"]))
    print("Trees    :", len(data["trees"]))

    print()
    print("First trees:")
    for tree in data["trees"][:5]:
        print(tree)


if __name__ == "__main__":
    main()
