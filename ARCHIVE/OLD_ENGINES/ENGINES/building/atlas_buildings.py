import requests

from atlas_osm_cache import save_osm_cache, load_osm_cache


BUILDINGS_CACHE_FILE = "buildings_cache.json"


def fetch_buildings_from_osm(bounds):
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.openstreetmap.ru/api/interpreter",
    ]

    south = bounds["south"]
    west = bounds["west"]
    north = bounds["north"]
    east = bounds["east"]

    query = f"""
[out:json][timeout:25];
(
  way["building"]({south},{west},{north},{east});
  relation["building"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""

    headers = {
        "User-Agent": "ATLAS_ENGINE/0.5"
    }

    last_error = None

    for overpass_url in overpass_urls:
        try:
            print("Overpass deneniyor:", overpass_url)

            response = requests.post(
                overpass_url,
                data=query.encode("utf-8"),
                headers=headers,
                timeout=20,
            )

            response.raise_for_status()

            data = response.json()

            save_osm_cache(
                BUILDINGS_CACHE_FILE,
                data
            )

            print("Overpass başarılı:", overpass_url)
            return data

        except Exception as error:
            last_error = error
            print("Overpass başarısız:", overpass_url)
            print("Hata:", error)
            print()

    print("Canlı Overpass başarısız.")
    print("Buildings cache deneniyor...")

    cached = load_osm_cache(BUILDINGS_CACHE_FILE)

    if cached is not None:
        print("Buildings cache kullanılıyor.")
        return cached

    raise RuntimeError(
        f"Tüm Overpass sunucuları başarısız oldu ve buildings cache bulunamadı. Son hata: {last_error}"
    )


def is_building_way(element):
    return (
        element.get("type") == "way"
        and "tags" in element
        and "building" in element["tags"]
        and "nodes" in element
    )


def count_building_ways(osm_data):
    count = 0

    for element in osm_data["elements"]:
        if is_building_way(element):
            count += 1

    return count