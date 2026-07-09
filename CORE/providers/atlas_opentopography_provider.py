# CORE/providers/atlas_opentopography_provider.py

import os
import urllib.parse
import urllib.request

from CORE.atlas_terrain_provider import AtlasTerrainProvider


class AtlasOpenTopographyProvider(AtlasTerrainProvider):
    """
    ATLAS OpenTopography Provider v0.3

    - COP30 DEM'i bbox ile indirir.
    - AAIGrid (.asc) olarak cacheler.
    - Cachelenen DEM üzerinden lat/lon için yükseklik döndürür.
    """

    BASE_URL = "https://portal.opentopography.org/API/globaldem"
    DEFAULT_DATASET = "COP30"

    def __init__(self, dataset=DEFAULT_DATASET, cache_dir="CACHE/DEM", debug=True):
        self.dataset = dataset
        self.cache_dir = cache_dir
        self.debug = debug
        self.api_key = self._load_api_key()
        self.grid_cache = {}

        if not self.api_key:
            raise ValueError("OPENTOPOGRAPHY_API_KEY .env içinde bulunamadı.")

        os.makedirs(self.cache_dir, exist_ok=True)

    def get_height(self, lat, lon):
        grid = self._find_grid_for_point(lat, lon)

        if grid is None:
            raise ValueError(
                f"Bu nokta için cachelenmiş OpenTopography DEM yok: {lat}, {lon}"
            )

        return self._height_from_grid(grid, lat, lon)

    def download_dem_bbox(self, south, west, north, east):
        output_path = self._cache_path(south, west, north, east)

        if os.path.exists(output_path):
            if self.debug:
                print(f"OpenTopography cache hit: {output_path}")
            return output_path

        params = {
            "demtype": self.dataset,
            "south": south,
            "north": north,
            "west": west,
            "east": east,
            "outputFormat": "AAIGrid",
            "API_Key": self.api_key,
        }

        url = self.BASE_URL + "?" + urllib.parse.urlencode(params)

        if self.debug:
            print(f"OpenTopography DEM download: {self.dataset}")
            print(f"BBOX: {south}, {west}, {north}, {east}")
            print(f"Saving to: {output_path}")

        urllib.request.urlretrieve(url, output_path)

        return output_path

    def _find_grid_for_point(self, lat, lon):
        for filename in os.listdir(self.cache_dir):
            if not filename.startswith(self.dataset):
                continue

            if not filename.endswith("_asc"):
                continue

            path = os.path.join(self.cache_dir, filename)
            grid = self._load_ascii_grid(path)

            tolerance = grid["cellsize"] * 2

        if (
            grid["south"] - tolerance <= lat <= grid["north"] + tolerance
            and grid["west"] - tolerance <= lon <= grid["east"] + tolerance
        ):
            return grid

        return None

    def _load_ascii_grid(self, path):
        if path in self.grid_cache:
            return self.grid_cache[path]

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        header = {}

        data_start_index = 0

        for index, line in enumerate(lines):
            parts = line.strip().split()

            if len(parts) < 2:
                continue

            key = parts[0].lower()

            if key in {
                "ncols",
                "nrows",
                "xllcorner",
                "yllcorner",
                "cellsize",
                "nodata_value",
            }:
                header[key] = float(parts[1])
                data_start_index = index + 1
            else:
                break

        ncols = int(header["ncols"])
        nrows = int(header["nrows"])
        west = header["xllcorner"]
        south = header["yllcorner"]
        cellsize = header["cellsize"]
        nodata_value = header.get("nodata_value")

        values = []

        for line in lines[data_start_index:]:
            row_values = [float(value) for value in line.strip().split()]

            if row_values:
                values.append(row_values)

        if len(values) != nrows:
            raise ValueError(
                f"Invalid AAIGrid row count: expected {nrows}, got {len(values)}"
            )

        for row in values:
            if len(row) != ncols:
                raise ValueError(
                    f"Invalid AAIGrid col count: expected {ncols}, got {len(row)}"
                )

        grid = {
            "path": path,
            "ncols": ncols,
            "nrows": nrows,
            "west": west,
            "south": south,
            "east": west + (ncols - 1) * cellsize,
            "north": south + (nrows - 1) * cellsize,
            "cellsize": cellsize,
            "nodata_value": nodata_value,
            "values": values,
        }

        self.grid_cache[path] = grid

        return grid

    def _height_from_grid(self, grid, lat, lon):
        col = round((lon - grid["west"]) / grid["cellsize"])
        row_from_south = round((lat - grid["south"]) / grid["cellsize"])

        col = max(0, min(grid["ncols"] - 1, col))
        row_from_south = max(0, min(grid["nrows"] - 1, row_from_south))

        # AAIGrid data rows start from north.
        row = (grid["nrows"] - 1) - row_from_south

        value = grid["values"][row][col]

        if grid["nodata_value"] is not None and value == grid["nodata_value"]:
            return None

        return float(value)

    def _cache_path(self, south, west, north, east):
        safe_name = (
            f"{self.dataset}_" f"{south:.6f}_{west:.6f}_{north:.6f}_{east:.6f}.asc"
        )
        safe_name = safe_name.replace("-", "m").replace(".", "_")
        return os.path.join(self.cache_dir, safe_name)

    @staticmethod
    def _load_api_key():
        key = os.environ.get("OPENTOPOGRAPHY_API_KEY")
        if key:
            return key.strip()

        env_path = ".env"

        if not os.path.exists(env_path):
            return None

        with open(env_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.startswith("OPENTOPOGRAPHY_API_KEY="):
                    return line.split("=", 1)[1].strip()

        return None
