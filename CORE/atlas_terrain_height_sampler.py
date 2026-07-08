# CORE/atlas_terrain_height_sampler.py


class AtlasTerrainHeightSampler:
    """
    ATLAS Terrain Height Sampler v0.1

    Görev:
    Terrain provider'dan gerçek yükseklik alır ve bunu STL z-mm değerine çevirir.

    Standart ölçek:
    XY = 1:5500
    Z  = 1:5500

    İlk sürüm:
    - lat/lon üzerinden terrain yüksekliği okur
    - bbox içindeki minimum yüksekliği referans alır
    - z değerini mm olarak döndürür
    """

    DEFAULT_Z_SCALE = 5500.0
    DEFAULT_BASE_Z = 0.80

    def __init__(
        self,
        terrain_provider,
        reference_height_m,
        z_scale=DEFAULT_Z_SCALE,
        base_z=DEFAULT_BASE_Z,
    ):
        self.terrain_provider = terrain_provider
        self.reference_height_m = reference_height_m
        self.z_scale = z_scale
        self.base_z = base_z

    def height_mm_at(self, lat, lon):
        height_m = self.terrain_provider.get_height(lat, lon)

        if height_m is None:
            height_m = self.reference_height_m

        return (
            self.base_z + ((height_m - self.reference_height_m) / self.z_scale) * 1000.0
        )
