# CORE/atlas_terrain_pipeline.py

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider
from CORE.providers.atlas_opentopography_provider import (
    AtlasOpenTopographyProvider,
)
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator
from CORE.atlas_terrain_terrace_builder import AtlasTerrainTerraceBuilder


class AtlasTerrainPipeline:
    """
    ATLAS Terrain Pipeline v2.2

    - Supports rectangular terrain dimensions.
    - Keeps legacy square target_size_mm behavior.
    - Optionally converts the normal terrain grid into a closed,
      cell-level terraced terrain slab.
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
        smoothing_passes=0,
        terrace_step_mm=None,
        debug=True,
    ):
        if terrace_step_mm is not None:
            terrace_step_mm = float(terrace_step_mm)

            if terrace_step_mm <= 0.0:
                raise ValueError(
                    "terrace_step_mm must be greater than zero"
                )

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

            mesh = AtlasTerrainPipeline._build_closed_mesh(
                terrain_provider=terrain_provider,
                bbox=bbox,
                target_size_mm=target_size_mm,
                size_x_mm=size_x_mm,
                size_y_mm=size_y_mm,
                grid_size=grid_size,
                z_scale=z_scale,
                base_z=base_z,
                bottom_z=bottom_z,
                smoothing_passes=smoothing_passes,
            )

            return AtlasTerrainPipeline._apply_terracing(
                mesh=mesh,
                base_z=base_z,
                bottom_z=bottom_z,
                terrace_step_mm=terrace_step_mm,
            )

        if provider_name != "srtm":
            raise ValueError(
                "Unsupported terrain provider: "
                f"{terrain_provider_name}"
            )

        srtm_provider = AtlasSRTMProvider(
            data_dir=data_dir,
            debug=debug,
        )

        try:
            mesh = AtlasTerrainPipeline._build_closed_mesh(
                terrain_provider=srtm_provider,
                bbox=bbox,
                target_size_mm=target_size_mm,
                size_x_mm=size_x_mm,
                size_y_mm=size_y_mm,
                grid_size=grid_size,
                z_scale=z_scale,
                base_z=base_z,
                bottom_z=bottom_z,
                smoothing_passes=smoothing_passes,
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

                mesh = AtlasTerrainPipeline._build_closed_mesh(
                    terrain_provider=opentopography_provider,
                    bbox=bbox,
                    target_size_mm=target_size_mm,
                    size_x_mm=size_x_mm,
                    size_y_mm=size_y_mm,
                    grid_size=grid_size,
                    z_scale=z_scale,
                    base_z=base_z,
                    bottom_z=bottom_z,
                    smoothing_passes=smoothing_passes,
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

        return AtlasTerrainPipeline._apply_terracing(
            mesh=mesh,
            base_z=base_z,
            bottom_z=bottom_z,
            terrace_step_mm=terrace_step_mm,
        )

    @staticmethod
    def _build_closed_mesh(
        terrain_provider,
        bbox,
        target_size_mm,
        size_x_mm,
        size_y_mm,
        grid_size,
        z_scale,
        base_z,
        bottom_z,
        smoothing_passes,
    ):
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
            smoothing_passes=smoothing_passes,
        )

    @staticmethod
    def _apply_terracing(
        mesh,
        base_z,
        bottom_z,
        terrace_step_mm,
    ):
        if terrace_step_mm is None:
            return mesh

        cell_levels = AtlasTerrainTerraceBuilder.build_cell_level_grid(
            top_points=mesh["top_points"],
            base_z=base_z,
            terrace_step_mm=terrace_step_mm,
        )

        terraced_mesh = (
            AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
                top_points=mesh["top_points"],
                cell_levels=cell_levels,
                bottom_z=bottom_z,
                terrace_step_mm=terrace_step_mm,
            )
        )

        metadata = dict(mesh.get("metadata", {}))
        metadata.update(terraced_mesh["metadata"])

        terraced_mesh["metadata"] = metadata
        terraced_mesh["grid"] = mesh["grid"]

        return terraced_mesh
