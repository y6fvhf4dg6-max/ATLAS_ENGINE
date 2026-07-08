"""
ATLAS Engine 2.0

Module : Local OSM Downloader
Version: 1.0

Purpose:
Download regional OSM PBF extracts from Geofabrik.
This removes dependency on Overpass API for production workflows.
"""

import os
import requests


DATA_DIR = "DATA/OSM"

REGIONS = {
    "hessen": {
        "name": "Hessen / Germany",
        "url": "https://download.geofabrik.de/europe/germany/hessen-latest.osm.pbf",
        "filename": "hessen-latest.osm.pbf",
    },
    "germany": {
        "name": "Germany",
        "url": "https://download.geofabrik.de/europe/germany-latest.osm.pbf",
        "filename": "germany-latest.osm.pbf",
    },
    "turkey": {
        "name": "Turkey",
        "url": "https://download.geofabrik.de/europe/turkey-latest.osm.pbf",
        "filename": "turkey-latest.osm.pbf",
    },
}


DEFAULT_REGION = "hessen"


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def download_file(url, output_path):
    print("İndiriliyor:", url)
    print("Kayıt yeri :", output_path)

    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue

                file.write(chunk)
                downloaded += len(chunk)

                if total > 0:
                    percent = downloaded * 100 / total
                    print(f"\rİlerleme: {percent:.1f}%", end="")

    print()
    print("İndirme tamamlandı.")


def download_region(region_key=DEFAULT_REGION, force=False):
    ensure_data_dir()

    if region_key not in REGIONS:
        raise ValueError(f"Bilinmeyen region: {region_key}")

    region = REGIONS[region_key]
    output_path = os.path.join(DATA_DIR, region["filename"])

    print()
    print("=" * 60)
    print("ATLAS LOCAL OSM DOWNLOADER v1.0")
    print("=" * 60)
    print("Region:", region["name"])
    print("File  :", output_path)
    print()

    if os.path.exists(output_path) and not force:
        print("Dosya zaten var. Tekrar indirilmedi.")
        print("Yeniden indirmek için force=True kullanılmalı.")
        print("=" * 60)
        return output_path

    download_file(region["url"], output_path)

    print("=" * 60)
    return output_path


def main():
    download_region(DEFAULT_REGION)


if __name__ == "__main__":
    main()