# CORE/atlas_terrain_downloader.py

import math
import os
import urllib.request


class AtlasTerrainDownloader:
    """
    ATLAS Terrain Downloader v0.1

    Görev:
    Verilen lat/lon için gerekli SRTM tile adını hesaplar.
    Eksikse Data/TERRAIN/SRTM içine indirmek için altyapı sağlar.

    Not:
    SRTM kaynak URL'leri sağlayıcıya göre değişebilir.
    Bu ilk sürüm güvenli iskelet ve tile hesaplama yapar.
    """

    DEFAULT_SRTM_DIR = "Data/TERRAIN/SRTM"

    @staticmethod
    def tile_name(lat, lon):
        lat_floor = math.floor(lat)
        lon_floor = math.floor(lon)

        ns = "N" if lat_floor >= 0 else "S"
        ew = "E" if lon_floor >= 0 else "W"

        return f"{ns}{abs(lat_floor):02d}{ew}{abs(lon_floor):03d}"

    @staticmethod
    def expected_hgt_path(lat, lon, data_dir=DEFAULT_SRTM_DIR):
        tile = AtlasTerrainDownloader.tile_name(lat, lon)
        return os.path.join(data_dir, f"{tile}.hgt")

    @staticmethod
    def has_tile(lat, lon, data_dir=DEFAULT_SRTM_DIR):
        path = AtlasTerrainDownloader.expected_hgt_path(
            lat=lat,
            lon=lon,
            data_dir=data_dir,
        )
        return os.path.exists(path)

    @staticmethod
    def report_required_tile(lat, lon, data_dir=DEFAULT_SRTM_DIR):
        tile = AtlasTerrainDownloader.tile_name(lat, lon)
        path = AtlasTerrainDownloader.expected_hgt_path(lat, lon, data_dir)

        print("")
        print("=" * 60)
        print("ATLAS TERRAIN DOWNLOADER REPORT")
        print("=" * 60)
        print(f"Lat/Lon       : {lat}, {lon}")
        print(f"Required tile : {tile}.hgt")
        print(f"Expected path : {path}")
        print(f"Exists        : {os.path.exists(path)}")
        print("=" * 60)
        print("")

        return {
            "tile": tile,
            "path": path,
            "exists": os.path.exists(path),
        }

    @staticmethod
    def download_file(url, output_path):
        """
        Generic downloader.

        Şimdilik URL dışarıdan verilir.
        SRTM sağlayıcı URL stratejisini sonraki sürümde ekleyeceğiz.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        print("")
        print("=" * 60)
        print("ATLAS TERRAIN DOWNLOAD")
        print("=" * 60)
        print(f"URL    : {url}")
        print(f"Output : {output_path}")
        print("=" * 60)
        print("")

        urllib.request.urlretrieve(url, output_path)

        return output_path
