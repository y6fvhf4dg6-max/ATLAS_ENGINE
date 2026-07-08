# Test/test_srtm_grid.py

from CORE.atlas_srtm_provider import AtlasSRTMProvider


def main():
    provider = AtlasSRTMProvider(
        data_dir="Data/TERRAIN/SRTM",
        debug=False,
    )

    # Anıtkabir test bbox
    south = 39.92011328853755
    west = 32.83050142502186
    north = 39.929994711462456
    east = 32.84338657497815

    grid_size = 9

    heights = []

    print("")
    print("=" * 60)
    print("ATLAS SRTM GRID TEST")
    print("=" * 60)
    print(f"BBox      : {south}, {west}, {north}, {east}")
    print(f"Grid size : {grid_size} x {grid_size}")
    print("-" * 60)

    for row in range(grid_size):
        lat = south + (north - south) * (row / (grid_size - 1))
        row_values = []

        for col in range(grid_size):
            lon = west + (east - west) * (col / (grid_size - 1))
            height = provider.get_height(lat, lon)

            row_values.append(height)

            if height is not None:
                heights.append(height)

        print(row_values)

    print("-" * 60)

    if heights:
        print(f"Min height : {min(heights)} m")
        print(f"Max height : {max(heights)} m")
        print(f"Delta      : {max(heights) - min(heights)} m")
    else:
        print("No height values found.")

    print("=" * 60)
    print("")


if __name__ == "__main__":
    main()
