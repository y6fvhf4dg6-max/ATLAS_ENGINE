# CORE/atlas_nature_pipeline.py

"""
ATLAS Nature Pipeline v0.2

Aktif sağlayıcıları çalıştırır ve sonuçları ortak yapıda birleştirir.

MVP davranışı:
- OSM, WorldCover ve Copernicus kullanılır
- Dynamic World pasiftir
- WorldCover tree-cover pikselleri baskıya uygun sayıda
  temsili ağaç noktasına dönüştürülür
- Ağaçlar yalnızca gerçek tree-cover piksellerinden seçilir
"""

import math

from CORE.providers.nature.atlas_provider_selector import (
    AtlasNatureProviderSelector,
)


class AtlasNaturePipeline:
    DEFAULT_PROVIDER_NAMES = (
        "osm",
        "worldcover",
        "copernicus",
    )

    MAX_WORLDCOVER_TREES = 300

    @staticmethod
    def fetch(
        bbox,
        provider_names=None,
        debug=True,
    ):
        if provider_names is None:
            provider_names = AtlasNaturePipeline.DEFAULT_PROVIDER_NAMES

        providers = AtlasNatureProviderSelector.build_providers(
            provider_names=provider_names,
        )

        result = {
            "trees": [],
            "tree_rows": [],
            "tree_cover": [],
            "forests": [],
            "grass": [],
            "scrub": [],
            "water": [],
            "metadata": {
                "providers_used": [],
                "worldcover_tree_samples": 0,
            },
        }

        for provider in providers:
            provider_result = provider.fetch(bbox)

            result["trees"].extend(provider_result.get("trees", []))
            result["tree_rows"].extend(provider_result.get("tree_rows", []))
            result["tree_cover"].extend(provider_result.get("tree_cover", []))
            result["forests"].extend(provider_result.get("forests", []))
            result["grass"].extend(provider_result.get("grass", []))
            result["scrub"].extend(provider_result.get("scrub", []))
            result["water"].extend(provider_result.get("water", []))

            provider_name = provider_result.get("metadata", {}).get(
                "provider",
                provider.PROVIDER_NAME,
            )

            result["metadata"]["providers_used"].append(provider_name)

        worldcover_trees = AtlasNaturePipeline._sample_tree_cover(
            result["tree_cover"],
            max_trees=AtlasNaturePipeline.MAX_WORLDCOVER_TREES,
        )

        result["trees"].extend(worldcover_trees)
        result["metadata"]["worldcover_tree_samples"] = len(worldcover_trees)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS NATURE PIPELINE REPORT")
            print("=" * 60)
            print(f"Providers used          : {result['metadata']['providers_used']}")
            print(f"Trees                    : {len(result['trees'])}")
            print(f"WorldCover tree samples  : {len(worldcover_trees)}")
            print(f"Tree rows                : {len(result['tree_rows'])}")
            print(f"Tree cover pixels        : {len(result['tree_cover'])}")
            print(f"Forests                  : {len(result['forests'])}")
            print(f"Grass                    : {len(result['grass'])}")
            print(f"Scrub                    : {len(result['scrub'])}")
            print(f"Water                    : {len(result['water'])}")
            print("=" * 60)
            print("")

        return result

    @staticmethod
    def _sample_tree_cover(tree_cover, max_trees):
        if not tree_cover or max_trees <= 0:
            return []

        step = max(1, math.ceil(len(tree_cover) / max_trees))
        selected = tree_cover[::step][:max_trees]

        trees = []

        for index, item in enumerate(selected):
            trees.append(
                {
                    "id": f"worldcover_{index}",
                    "lat": item["lat"],
                    "lon": item["lon"],
                    "tree_type": "tree",
                    "tags": {
                        "source": "worldcover",
                        "class_id": item.get("class_id"),
                        "resolution_m": item.get("resolution_m", 10),
                    },
                }
            )

        return trees
