# CORE/atlas_terrain_pipeline.py

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider
from CORE.providers.atlas_opentopography_provider import (
    AtlasOpenTopographyProvider,
)
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator


class AtlasTerrainPipeline:
    """
    ATLAS Terrain Pipeline v2.1

    v2.1:
    - Supports rectangular terrain dimensions
    - Keeps legacy square target_size_mm behavior
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
        size_x_mm=None,
        size_y_mm=None,
        debug=True,
    ):
        provider_name = terrain_provider_name.lower()

        if provider_name == "opentopography":
            terrain_provider = AtlasOpenTopographyProvider(
                dataset="COP30",
                debug=debug,
            )

            south, west, north, east = bbox

            terrain_provider.download_dem_bbox(
                south=south,
                west=west,
                north=north,
                east=east,
            )

            return AtlasTerrainMeshGenerator.build_closed_slab_mesh(
                terrain_provider=terrain_provider,
                bbox=bbox,
                size_mm=target_size_mm,
                size_x_mm=size_x_mm,
                size_y_mm=size_y_mm,
                grid_size=grid_size,
                z_scale=z_scale,
                base_z=base_z,
                bottom_z=bottom_z,
            )

        if provider_name != "srtm":
            raise ValueError(
                "Unsupported terrain provider: " f"{terrain_provider_name}"
            )

        srtm_provider = AtlasSRTMProvider(
            data_dir=data_dir,
            debug=debug,
        )

        try:
            return AtlasTerrainMeshGenerator.build_closed_slab_mesh(
                terrain_provider=srtm_provider,
                bbox=bbox,
                size_mm=target_size_mm,
                size_x_mm=size_x_mm,
                size_y_mm=size_y_mm,
                grid_size=grid_size,
                z_scale=z_scale,
                base_z=base_z,
                bottom_z=bottom_z,
            )

        except RuntimeError as error:
            if "Terrain height data unavailable" not in str(error):
                raise

            if debug:
                print("")
                print("=" * 72)
                print("ATLAS TERRAIN PROVIDER FALLBACK")
                print("=" * 72)
                print("Local SRTM data unavailable.")
                print("Falling back to OpenTopography COP30.")
                print(f"BBOX: {bbox}")
                print("=" * 72)
                print("")

            try:
                opentopography_provider = AtlasOpenTopographyProvider(
                    dataset="COP30",
                    debug=debug,
                )

                south, west, north, east = bbox

                opentopography_provider.download_dem_bbox(
                    south=south,
                    west=west,
                    north=north,
                    east=east,
                )

                return AtlasTerrainMeshGenerator.build_closed_slab_mesh(
                    terrain_provider=opentopography_provider,
                    bbox=bbox,
                    size_mm=target_size_mm,
                    size_x_mm=size_x_mm,
                    size_y_mm=size_y_mm,
                    grid_size=grid_size,
                    z_scale=z_scale,
                    base_z=base_z,
                    bottom_z=bottom_z,
                )

            except Exception as fallback_error:
                raise RuntimeError(
                    "Terrain generation failed. "
                    "Local SRTM data is unavailable and "
                    "OpenTopography fallback also failed. "
                    f"BBOX={bbox}. "
                    f"SRTM error: {error}. "
                    f"OpenTopography error: {fallback_error}"
                ) from fallback_error
