# CORE/providers/nature/atlas_provider_selector.py

"""
ATLAS Nature Provider Selector v0.4

Aktif Nature Provider'ları merkezi olarak yönetir.

Sabit plan:
1. OSM
2. Dynamic World
3. Copernicus
4. WorldCover
"""

from CORE.providers.nature.atlas_osm_nature_provider import (
    AtlasOSMProvider,
)

from CORE.providers.nature.atlas_dynamic_world_provider import (
    AtlasDynamicWorldProvider,
)

from CORE.providers.nature.atlas_copernicus_provider import (
    AtlasCopernicusProvider,
)

from CORE.providers.nature.atlas_worldcover_provider import (
    AtlasWorldCoverProvider,
)


class AtlasNatureProviderSelector:
    DEFAULT_PROVIDER_ORDER = (
        "osm",
        "dynamic_world",
        "copernicus",
        "worldcover",
    )

    @staticmethod
    def build_providers(provider_names=None):
        if provider_names is None:
            provider_names = AtlasNatureProviderSelector.DEFAULT_PROVIDER_ORDER

        providers = []

        for provider_name in provider_names:
            provider = AtlasNatureProviderSelector._build_provider(provider_name)

            if provider is not None:
                providers.append(provider)

        return providers

    @staticmethod
    def _build_provider(provider_name):
        if provider_name == "osm":
            return AtlasOSMProvider()

        if provider_name == "dynamic_world":
            return AtlasDynamicWorldProvider()

        if provider_name == "copernicus":
            return AtlasCopernicusProvider()

        if provider_name == "worldcover":
            return AtlasWorldCoverProvider()

        return None
