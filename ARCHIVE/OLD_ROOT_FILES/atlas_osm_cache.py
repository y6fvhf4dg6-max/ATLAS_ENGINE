"""
ATLAS Engine 2.0

Module : OSM Cache
Version: 1.0
Purpose:
Save and load OSM API responses so ATLAS can continue working
when Overpass servers fail.
"""

import json
import os


CACHE_DIR = "CACHE"


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def save_osm_cache(filename, data):
    ensure_cache_dir()

    path = os.path.join(CACHE_DIR, filename)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)

    print("OSM cache kaydedildi:", path)


def load_osm_cache(filename):
    path = os.path.join(CACHE_DIR, filename)

    if not os.path.exists(path):
        print("OSM cache bulunamadı:", path)
        return None

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("OSM cache yüklendi:", path)
    return data


def main():
    print("=" * 60)
    print("ATLAS OSM CACHE v1.0")
    print("=" * 60)
    ensure_cache_dir()
    print("Cache klasörü hazır:", CACHE_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()