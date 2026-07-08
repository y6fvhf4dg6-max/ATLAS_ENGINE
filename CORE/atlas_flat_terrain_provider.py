# CORE/atlas_flat_terrain_provider.py

from CORE.atlas_terrain_provider import AtlasTerrainProvider


class AtlasFlatTerrainProvider(AtlasTerrainProvider):
    """
    ATLAS Flat Terrain Provider v0.1

    Fallback terrain provider.
    Gerçek DEM yoksa tüm noktalar için aynı yüksekliği döndürür.
    """

    def __init__(self, height_m=0.0):
        self.height_m = height_m

    def get_height(self, lat, lon):
        return self.height_m
