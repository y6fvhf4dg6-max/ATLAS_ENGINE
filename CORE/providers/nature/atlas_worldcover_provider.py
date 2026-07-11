# CORE/providers/nature/atlas_worldcover_provider.py

"""
ATLAS ESA WorldCover Nature Provider v0.2

Gerçek ESA WorldCover 2021 v200 verisini okur.

Desteklenen sınıflar:
- 10: Tree cover
- 20: Shrubland
- 30: Grassland
- 80: Permanent water bodies

Çıktı:
- tree_cover
- forests
- grass
- scrub
- water
"""

import json
import math
from pathlib import Path

import rasterio
from rasterio.windows import from_bounds

from CORE.providers.nature.atlas_nature_provider import (
    AtlasNatureProvider,
)


class AtlasWorldCoverProvider(AtlasNatureProvider):
    PROVIDER_NAME = "worldcover"

    BASE_URL = (
        "https://esa-worldcover.s3.eu-central-1.amazonaws.com/"
        "v200/2021/map/"
        "ESA_WorldCover_10m_2021_v200_{tile_id}_Map.tif"
    )

    CACHE_DIR = Path("CACHE/LANDCOVER/WORLDCOVER")

    CLASS_TREE = 10
    CLASS_SHRUB = 20
    CLASS_GRASS = 30
    CLASS_WATER = 80

    def fetch(self, bbox):
        self.validate_bbox(bbox)
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        cache_path = self._cache_path(bbox)

        if cache_path.exists():
            with cache_path.open("r", encoding="utf-8") as file:
                return json.load(file)

        south, west, north, east = bbox

        result = self.empty_result(self.PROVIDER_NAME)
        result["metadata"].update(
            {
                "source_resolution_m": 10,
                "license": "CC BY 4.0",
                "status": "real_data",
                "dataset": "ESA WorldCover 2021 v200",
                "tiles_used": [],
                "confidence": {},
            }
        )

        tile_ids = self._tiles_for_bbox(bbox)

        for tile_id in tile_ids:
            tile_result = self._read_tile(
                tile_id=tile_id,
                bbox=bbox,
            )

            result["tree_cover"].extend(tile_result["tree_cover"])
            result["forests"].extend(tile_result["forests"])
            result["grass"].extend(tile_result["grass"])
            result["scrub"].extend(tile_result["scrub"])
            result["water"].extend(tile_result["water"])

            result["metadata"]["tiles_used"].append(tile_id)

        with cache_path.open("w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return result

    def _read_tile(self, tile_id, bbox):
        south, west, north, east = bbox

        url = self.BASE_URL.format(tile_id=tile_id)

        tile_result = {
            "tree_cover": [],
            "forests": [],
            "grass": [],
            "scrub": [],
            "water": [],
        }

        try:
            with rasterio.open(url) as dataset:
                dataset_bounds = dataset.bounds

                read_west = max(west, dataset_bounds.left)
                read_south = max(south, dataset_bounds.bottom)
                read_east = min(east, dataset_bounds.right)
                read_north = min(north, dataset_bounds.top)

                if read_west >= read_east or read_south >= read_north:
                    return tile_result

                window = from_bounds(
                    read_west,
                    read_south,
                    read_east,
                    read_north,
                    transform=dataset.transform,
                )

                window = window.round_offsets().round_lengths()

                data = dataset.read(
                    1,
                    window=window,
                    boundless=False,
                )

                transform = dataset.window_transform(window)

                for row in range(data.shape[0]):
                    for col in range(data.shape[1]):
                        class_id = int(data[row, col])

                        if class_id not in {
                            self.CLASS_TREE,
                            self.CLASS_SHRUB,
                            self.CLASS_GRASS,
                            self.CLASS_WATER,
                        }:
                            continue

                        lon, lat = rasterio.transform.xy(
                            transform,
                            row,
                            col,
                            offset="center",
                        )

                        item = {
                            "lat": float(lat),
                            "lon": float(lon),
                            "class_id": class_id,
                            "source": self.PROVIDER_NAME,
                            "resolution_m": 10,
                        }

                        if class_id == self.CLASS_TREE:
                            tile_result["tree_cover"].append(item)
                            tile_result["forests"].append(item)

                        elif class_id == self.CLASS_SHRUB:
                            tile_result["scrub"].append(item)

                        elif class_id == self.CLASS_GRASS:
                            tile_result["grass"].append(item)

                        elif class_id == self.CLASS_WATER:
                            tile_result["water"].append(item)

        except rasterio.errors.RasterioIOError as error:
            raise RuntimeError(
                f"WorldCover tile could not be read: {tile_id}\n"
                f"URL: {url}\n"
                f"Reason: {error}"
            ) from error

        return tile_result

    @staticmethod
    def _tiles_for_bbox(bbox):
        south, west, north, east = bbox

        south_tile = math.floor(south / 3.0) * 3
        north_tile = math.floor((north - 1e-12) / 3.0) * 3

        west_tile = math.floor(west / 3.0) * 3
        east_tile = math.floor((east - 1e-12) / 3.0) * 3

        tile_ids = []

        lat_value = south_tile

        while lat_value <= north_tile:
            lon_value = west_tile

            while lon_value <= east_tile:
                tile_ids.append(
                    AtlasWorldCoverProvider._tile_id(
                        lat_value,
                        lon_value,
                    )
                )

                lon_value += 3

            lat_value += 3

        return tile_ids

    @staticmethod
    def _tile_id(lat_value, lon_value):
        lat_prefix = "N" if lat_value >= 0 else "S"
        lon_prefix = "E" if lon_value >= 0 else "W"

        return (
            f"{lat_prefix}{abs(int(lat_value)):02d}"
            f"{lon_prefix}{abs(int(lon_value)):03d}"
        )

    def _cache_path(self, bbox):
        south, west, north, east = bbox

        name = f"worldcover_" f"{south:.6f}_{west:.6f}_" f"{north:.6f}_{east:.6f}.json"

        return self.CACHE_DIR / name
