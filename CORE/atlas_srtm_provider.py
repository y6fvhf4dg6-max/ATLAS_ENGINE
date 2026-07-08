# CORE/atlas_srtm_provider.py

import math
import os
import struct

from CORE.atlas_terrain_provider import AtlasTerrainProvider


class AtlasSRTMProvider(AtlasTerrainProvider):
    """
    ATLAS SRTM Provider v0.2

    Reads SRTM .hgt tiles.

    Expected file example:
    Data/TERRAIN/SRTM/N39E032.hgt
    """

    TILE_SIZE = 3601
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

        lat_floor = math.floor(lat)
        lon_floor = math.floor(lon)

        row = int(round((lat_floor + 1.0 - lat) * (self.TILE_SIZE - 1)))
        col = int(round((lon - lon_floor) * (self.TILE_SIZE - 1)))

        row = max(0, min(self.TILE_SIZE - 1, row))
        col = max(0, min(self.TILE_SIZE - 1, col))

        index = row * self.TILE_SIZE + col
        height = data[index]

        if height == self.NO_DATA_VALUE:
            return None

        return float(height)

    def _load_tile(self, tile_path):
        if tile_path in self.tile_cache:
            return self.tile_cache[tile_path]

        expected_values = self.TILE_SIZE * self.TILE_SIZE

        with open(tile_path, "rb") as file:
            raw = file.read()

        actual_values = len(raw) // 2

        if actual_values != expected_values:
            raise ValueError(
                f"Invalid SRTM tile size: {tile_path} "
                f"expected {expected_values} values, got {actual_values}"
            )

        data = struct.unpack(f">{expected_values}h", raw)
        self.tile_cache[tile_path] = data

        return data

    @staticmethod
    def _tile_name(lat, lon):
        lat_floor = math.floor(lat)
        lon_floor = math.floor(lon)

        ns = "N" if lat_floor >= 0 else "S"
        ew = "E" if lon_floor >= 0 else "W"

        return f"{ns}{abs(lat_floor):02d}{ew}{abs(lon_floor):03d}"
