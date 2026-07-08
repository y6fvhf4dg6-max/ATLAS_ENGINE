import requests

from atlas_osm_cache import save_osm_cache, load_osm_cache


ROADS_CACHE_FILE = "roads_cache.json"


def fetch_roads_from_osm(bounds):
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
  way["highway"]({south},{west},{north},{east});
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
            print("Overpass roads deneniyor:", overpass_url)

            response = requests.post(
                overpass_url,
                data=query.encode("utf-8"),
                headers=headers,
                timeout=20,
            )

            response.raise_for_status()

            data = response.json()

            save_osm_cache(
                ROADS_CACHE_FILE,
                data
            )

            print("Overpass roads başarılı:", overpass_url)
            return data

        except Exception as error:
            last_error = error
            print("Overpass roads başarısız:", overpass_url)
            print("Hata:", error)
            print()

    print("Canlı Overpass roads başarısız.")
    print("Roads cache deneniyor...")

    cached = load_osm_cache(ROADS_CACHE_FILE)

    if cached is not None:
        print("Roads cache kullanılıyor.")
        return cached

    raise RuntimeError(
        f"Tüm Overpass roads sunucuları başarısız oldu ve roads cache bulunamadı. Son hata: {last_error}"
    )


def is_road_way(element):
    return (
        element.get("type") == "way"
        and "tags" in element
        and "highway" in element["tags"]
        and "nodes" in element
    )


def count_road_ways(osm_data):
    count = 0

    for element in osm_data["elements"]:
        if is_road_way(element):
            count += 1

    return count