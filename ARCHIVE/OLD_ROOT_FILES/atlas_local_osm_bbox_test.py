from pyrosm import OSM
from atlas_bbox_engine import create_bbox

PBF_PATH = "DATA/OSM/hessen-latest.osm.pbf"


def main():
    print("=" * 60)
    print("ATLAS LOCAL BBOX TEST v1.0")
    print("=" * 60)

    latitude = 50.1136
    longitude = 8.6797
    radius_m = 300

    bbox = create_bbox(
        latitude,
        longitude,
        radius_m
    )

    print("BBOX:")
    print(bbox)
    print()

    osm = OSM(
        PBF_PATH,
        bounding_box=[
            bbox["west"],
            bbox["south"],
            bbox["east"],
            bbox["north"],
        ]
    )

    print("Binalar okunuyor...")
    buildings = osm.get_buildings()

    if buildings is None or buildings.empty:
        print("Bina bulunamadı.")
        return

    print(f"Bina sayısı: {len(buildings)}")
    print()

    print("İlk 20 bina:")
    print("-" * 60)

    for index, row in buildings.head(20).iterrows():
        osm_id = row.get("id", "None")
        name = row.get("name", "None")
        building = row.get("building", "None")
        amenity = row.get("amenity", "None")
        historic = row.get("historic", "None")
        tourism = row.get("tourism", "None")

        print(
            f"OSM: {osm_id} | "
            f"Name: {name} | "
            f"Building: {building} | "
            f"Amenity: {amenity} | "
            f"Historic: {historic} | "
            f"Tourism: {tourism}"
        )

    print()
    print("=" * 60)
    print("BBOX TEST TAMAMLANDI ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()