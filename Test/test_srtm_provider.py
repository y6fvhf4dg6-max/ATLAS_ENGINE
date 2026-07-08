# Test/test_srtm_provider.py

from CORE.atlas_srtm_provider import AtlasSRTMProvider


def main():
    provider = AtlasSRTMProvider(
        data_dir="Data/TERRAIN/SRTM",
        debug=True,
    )

    lat = 39.925054
    lon = 32.836944

    height = provider.get_height(lat, lon)

    print("")
    print("=" * 60)
    print("ATLAS SRTM PROVIDER TEST")
    print("=" * 60)
    print(f"Lat/Lon : {lat}, {lon}")
    print(f"Height  : {height}")
    print("=" * 60)
    print("")


if __name__ == "__main__":
    main()
