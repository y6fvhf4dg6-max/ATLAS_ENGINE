# CORE/atlas_terrain_engine.py

from CORE.atlas_flat_terrain_provider import AtlasFlatTerrainProvider


class AtlasTerrainEngine:
    """
    ATLAS Terrain Engine v0.1

    Terrain Engine yalnızca terrain provider ile konuşur.

    Veri kaynağı:
        - Flat
        - SRTM
        - Copernicus
        - LiDAR

    olabilir.

    Terrain Engine bunların hangisi olduğunu bilmez.
    """

    def __init__(self, provider=None):

        if provider is None:
            provider = AtlasFlatTerrainProvider()

        self.provider = provider

    def get_height(self, lat, lon):
        """
        Returns terrain elevation in meters.
        """

        return self.provider.get_height(lat, lon)
