# CORE/atlas_terrain_provider.py


class AtlasTerrainProvider:
    """
    ATLAS Terrain Provider Interface v1.0

    Terrain Engine yalnızca bu arayüzü bilir.

    Gerçek yükseklik kaynağı:
        - SRTM
        - OpenTopography
        - Copernicus
        - ALOS
        - LiDAR

    olabilir.

    Bu sınıf yalnızca ortak sözleşmeyi (interface) tanımlar.
    """

    def get_height(self, lat, lon):
        """
        Verilen koordinat için metre cinsinden yükseklik döndürür.

        Alt sınıflar bu metodu uygulamak zorundadır.
        """
        raise NotImplementedError("Terrain provider must implement get_height().")
