# CORE/atlas_terrain_provider.py


class AtlasTerrainProvider:
    """
    ATLAS Terrain Provider Interface v0.1

    Terrain Engine bu sınıf üzerinden yükseklik ister.
    Gerçek veri kaynağı SRTM, Copernicus veya LiDAR olabilir.

    Ama Terrain Engine bunların hiçbirini doğrudan bilmez.
    """

    def get_height(self, lat, lon):
        """
        Returns elevation in meters for given latitude / longitude.
        """
        raise NotImplementedError("Terrain provider must implement get_height()")
