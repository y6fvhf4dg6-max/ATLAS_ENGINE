"""
ATLAS Engine 2.0

Module : Landmark Probe
Version: 1.0

Purpose:
Inspect OSM tags in the current ATLAS area.
Used to discover how landmark, religious, public and social places
are tagged in real OSM data.
"""

from atlas_area import calculate_area_bounds
from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT
from atlas_geocoder import geocode_address
from atlas_local_osm import get_buildings_and_lookup
from atlas_tag_analyzer import describe_tags


ADDRESS = "Fulda Domplatz"


IMPORTANT_KEYS = [
    "name",
    "building",
    "amenity",
    "historic",
    "tourism",
    "leisure",
    "religion",
    "denomination",
    "wikidata",
    "wikipedia",
]


def short_tags(tags):
    return {
        key: tags.get(key)
        for key in IMPORTANT_KEYS
        if tags.get(key) is not None
    }


def main():
    print("=" * 60)
    print("ATLAS LANDMARK PROBE v1.0")
    print("=" * 60)

    product = PRODUCT_PROFILES[DEFAULT_PRODUCT]

    latitude, longitude = geocode_address(ADDRESS)

    bounds = calculate_area_bounds(
        latitude,
        longitude,
        product["real_size_m"]
    )

    print("Address:", ADDRESS)
    print("Latitude :", latitude)
    print("Longitude:", longitude)
    print("Real size:", product["real_size_m"], "m")
    print("Bounds:", bounds)
    print()

    osm_building_data, node_lookup = get_buildings_and_lookup(bounds)

    elements = osm_building_data.get("elements", [])

    print("Toplam bina elementi:", len(elements))
    print()

    found = 0

    for element in elements:
        tags = element.get("tags", {})
        info = describe_tags(tags)

        interesting = (
            info["landmark"]
            or tags.get("name")
            or tags.get("amenity")
            or tags.get("historic")
            or tags.get("tourism")
            or tags.get("religion")
            or tags.get("leisure")
        )

        if not interesting:
            continue

        found += 1

        print("-" * 60)
        print("OSM ID:", element.get("id"))
        print("Short tags:", short_tags(tags))
        print("Analysis:", info)

    print()
    print("Önemli / isimli yapı sayısı:", found)
    print("=" * 60)


if __name__ == "__main__":
    main()