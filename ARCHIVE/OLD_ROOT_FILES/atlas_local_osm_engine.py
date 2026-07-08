"""
ATLAS Engine 2.0

Module : Local OSM Engine
Version: 1.0

Purpose:
Read local Geofabrik .osm.pbf files and extract buildings / roads
without using Overpass API.
"""

from pyrosm import OSM


PBF_PATH = "DATA/OSM/hessen-latest.osm.pbf"


def load_osm():
    print("Lokal OSM yükleniyor:", PBF_PATH)
    return OSM(PBF_PATH)


def extract_buildings():
    osm = load_osm()

    print("Binalar okunuyor...")
    buildings = osm.get_buildings()

    print("Bina sayısı:", len(buildings))
    print(buildings.head())

    return buildings


def extract_roads():
    osm = load_osm()

    print("Yollar okunuyor...")
    roads = osm.get_network(network_type="driving")

    print("Yol sayısı:", len(roads))
    print(roads.head())

    return roads


def main():
    print("=" * 60)
    print("ATLAS LOCAL OSM ENGINE v1.0")
    print("=" * 60)

    extract_buildings()
    print()
    extract_roads()

    print("=" * 60)
    print("LOCAL OSM TEST TAMAMLANDI ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()