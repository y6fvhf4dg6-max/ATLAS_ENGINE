# CORE/atlas_terrain_manager.py

from CORE.atlas_terrain_engine import AtlasTerrainEngine
from CORE.atlas_flat_terrain_provider import AtlasFlatTerrainProvider


class AtlasTerrainManager:
    """
    ATLAS Terrain Manager v0.1

    Görev:
    Uygun terrain provider seçimini merkezi olarak yönetir.

    Öncelik sırası ileride şöyle olacak:
    1. LiDAR
    2. Copernicus
    3. SRTM
    4. Flat fallback

    Şimdilik yalnızca Flat Provider döndürür.
    """

    @staticmethod
    def create_engine(
        bbox=None,
        preferred_source="auto",
        debug=True,
    ):
        provider = AtlasFlatTerrainProvider(height_m=0.0)

        if debug:
            print("")
            print("=" * 60)
            print("ATLAS TERRAIN MANAGER REPORT")
            print("=" * 60)
            print(f"Preferred source : {preferred_source}")
            print("Selected provider: flat")
            print("Status           : fallback_flat_terrain")
            print("=" * 60)
            print("")

        return AtlasTerrainEngine(provider=provider)
