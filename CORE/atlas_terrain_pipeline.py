# CORE/atlas_terrain_pipeline.py

from CORE.atlas_srtm_provider import AtlasSRTMProvider
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator


class AtlasTerrainPipeline:
    """
    ATLAS Terrain Pipeline v1.0

    Amaç:
    - Terrain provider oluşturmak.
    - Terrain slab mesh üretmek.
    - AtlasEngine içindeki terrain sorumluluğunu azaltmak.

    Bu sınıf bina üretmez.
    Placement yapmaz.
    STL yazmaz.
    Sadece terrain mesh üretim sürecini yönetir.
    """

    @staticmethod
    def build_terrain_slab(
        bbox,
        target_size_mm,
        z_scale,
        base_z,
        bottom_z=0.0,
        grid_size=25,
        data_dir="Data/TERRAIN/SRTM",
        debug=True,
    ):
        terrain_provider = AtlasSRTMProvider(
            data_dir=data_dir,
            debug=debug,
        )

        return AtlasTerrainMeshGenerator.build_closed_slab_mesh(
            terrain_provider=terrain_provider,
            bbox=bbox,
            size_mm=target_size_mm,
            grid_size=grid_size,
            z_scale=z_scale,
            base_z=base_z,
            bottom_z=bottom_z,
        )
