# CORE/atlas_terrain_pipeline.py

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider
from CORE.providers.atlas_opentopography_provider import (
    AtlasOpenTopographyProvider,
)
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator


class AtlasTerrainPipeline:
    """
    ATLAS Terrain Pipeline v2.0
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
        terrain_provider_name="srtm",
        debug=True,
    ):
        if terrain_provider_name.lower() == "opentopography":
            terrain_provider = AtlasOpenTopographyProvider(
                dataset="AW3D30",
                debug=debug,
            )

            south, west, north, east = bbox
            terrain_provider.download_dem_bbox(
                south=south,
                west=west,
                north=north,
                east=east,
            )
        else:
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
