# CORE/providers/atlas_srtm_provider.py

import math
import os

import numpy as np

from CORE.atlas_terrain_provider import AtlasTerrainProvider


class AtlasSRTMProvider(AtlasTerrainProvider):
    """
    ATLAS SRTM Provider v0.3

    Supports:
    - SRTM1: 3601 × 3601
    - SRTM3: 1201 × 1201
    """

    TILE_SIZE = 3601
    SUPPORTED_TILE_SIZES = (3601, 1201)
    NO_DATA_VALUE = -32768

    def __init__(self, data_dir="Data/TERRAIN/SRTM", debug=True):
        self.data_dir = data_dir
        self.debug = debug
        self.tile_cache = {}

    def get_height(self, lat, lon):
        tile_name = self._tile_name(lat, lon)
        tile_path = os.path.join(self.data_dir, f"{tile_name}.hgt")

        if not os.path.exists(tile_path):
            if self.debug:
                print(f"SRTM tile missing: {tile_path}")
            return None

        data = self._load_tile(tile_path)
        tile_size = int(data.shape[0])

        lat_floor = math.floor(lat)
        lon_floor = math.floor(lon)

        row = int(
            round(
                (lat_floor + 1.0 - lat)
                * (tile_size - 1)
            )
        )
        col = int(
            round(
                (lon - lon_floor)
                * (tile_size - 1)
            )
        )

        row = max(0, min(tile_size - 1, row))
        col = max(0, min(tile_size - 1, col))

        height = data[row, col]

        if height == self.NO_DATA_VALUE:
            return None

        return float(height)

    def _load_tile(self, tile_path):
        if tile_path in self.tile_cache:
            return self.tile_cache[tile_path]

        data = np.fromfile(tile_path, dtype=">i2")
        actual_values = int(data.size)

        tile_size = None
        for candidate in self.SUPPORTED_TILE_SIZES:
            if actual_values == candidate * candidate:
                tile_size = candidate
                break

        if tile_size is None:
            expected = ", ".join(
                str(size * size)
                for size in self.SUPPORTED_TILE_SIZES
            )
            raise ValueError(
                f"Invalid SRTM tile size: {tile_path} "
                f"expected one of [{expected}] values, "
                f"got {actual_values}"
            )

        data = data.reshape((tile_size, tile_size))
        self.tile_cache[tile_path] = data

        return data

    @staticmethod
    def _tile_name(lat, lon):
        lat_floor = math.floor(lat)
        lon_floor = math.floor(lon)

        ns = "N" if lat_floor >= 0 else "S"
        ew = "E" if lon_floor >= 0 else "W"

        return f"{ns}{abs(lat_floor):02d}{ew}{abs(lon_floor):03d}"
