# Test/test_terrain_downloader.py

from CORE.atlas_terrain_downloader import AtlasTerrainDownloader


def main():
    lat = 39.925054
    lon = 32.836944

    AtlasTerrainDownloader.report_required_tile(
        lat=lat,
        lon=lon,
        data_dir="Data/TERRAIN/SRTM",
    )


if __name__ == "__main__":
    main()
