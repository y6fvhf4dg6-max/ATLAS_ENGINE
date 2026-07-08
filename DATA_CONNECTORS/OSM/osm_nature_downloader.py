"""
ATLAS Engine

OSM Nature Downloader v1.0

Downloads nature-related objects from OpenStreetMap.

Current support:
- Trees

Planned support:
- Forests
- Parks
- Grass
- Shrubs
- Orchards
- Vineyards
- Wetlands
- Natural Areas

Author:
ATLAS ENGINE
"""

import requests
from CORE.atlas_cache import AtlasCache


class OSMNatureDownloader:
    OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

    def download_trees(self, bbox):
        south, west, north, east = bbox

        cache_path = "CACHE/nature_trees_ulus.json"

        cached_data = AtlasCache.load(cache_path)

        if cached_data is not None:
            print("Loaded trees from cache.")
            return cached_data

        query = f"""
        [out:json][timeout:25];
        node["natural"="tree"]({south},{west},{north},{east});
        out;

        """

        response = requests.get(
            self.OVERPASS_URL,
            data={"data": query},
            timeout=60,
        )

        try:
            response.raise_for_status()
        except Exception as error:
            print("OSM nature download failed.")
            print(error)
            return {"elements": []}

        data = response.json()

        AtlasCache.save(cache_path, data)

        return data
