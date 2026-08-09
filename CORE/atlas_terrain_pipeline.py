# CORE/atlas_terrain_pipeline.py

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider
from CORE.providers.atlas_opentopography_provider import (
    AtlasOpenTopographyProvider,
)
from CORE.atlas_terrain_mesh_generator import AtlasTerrainMeshGenerator
from CORE.atlas_terrain_terrace_builder import AtlasTerrainTerraceBuilder
from CORE.atlas_terrain_surface_texture import (
    AtlasTerrainSurfaceTexture,
)
from CORE.atlas_morphology_aware_terrain_product_resolver import (
    AtlasMorphologyAwareTerrainProductResolver,
)
from CORE.atlas_terrain_presentation_surface_regularizer import (
    AtlasTerrainPresentationSurfaceRegularizer,
)


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
        surface_texture_amplitude_mm=None,
        surface_texture_wavelength_x_mm=28.0,
        surface_texture_wavelength_y_mm=37.0,
        surface_texture_edge_fade_mm=8.0,
        scene_morphology=None,
        urban_density=None,
        landmark_present=None,
        terrain_minimum_printable_relief_mm=None,
        terrain_maximum_printable_relief_mm=None,
        presentation_regularization_passes=0,
        presentation_regularization_strength=0.50,
        debug=True,
    ):
        if terrace_step_mm is not None:
            terrace_step_mm = float(terrace_step_mm)

            if terrace_step_mm <= 0.0:
                raise ValueError(
                    "terrace_step_mm must be greater than zero"
                )

        if surface_texture_amplitude_mm is not None:
            surface_texture_amplitude_mm = float(
                surface_texture_amplitude_mm
            )

            if surface_texture_amplitude_mm < 0.0:
                raise ValueError(
                    "surface_texture_amplitude_mm must be "
                    "non-negative"
                )

            if (
                surface_texture_amplitude_mm > 0.0
                and terrace_step_mm is not None
            ):
                raise ValueError(
                    "surface texture and terracing cannot "
                    "be enabled together"
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

            mesh = AtlasTerrainPipeline._apply_surface_texture(
                mesh=mesh,
                amplitude_mm=surface_texture_amplitude_mm,
                wavelength_x_mm=(
                    surface_texture_wavelength_x_mm
                ),
                wavelength_y_mm=(
                    surface_texture_wavelength_y_mm
                ),
                edge_fade_mm=surface_texture_edge_fade_mm,
            )

            mesh = AtlasTerrainPipeline._apply_terracing(
                mesh=mesh,
                base_z=base_z,
                bottom_z=bottom_z,
                terrace_step_mm=terrace_step_mm,
            )

            mesh = AtlasTerrainPipeline._apply_presentation_regularization(
                mesh=mesh,
                passes=presentation_regularization_passes,
                strength=presentation_regularization_strength,
            )

            return AtlasTerrainPipeline._apply_morphology_product_profile(
                mesh=mesh,
                target_size_mm=target_size_mm,
                z_scale=z_scale,
                scene_morphology=scene_morphology,
                urban_density=urban_density,
                landmark_present=landmark_present,
                minimum_printable_relief_mm=(
                    terrain_minimum_printable_relief_mm
                ),
                maximum_printable_relief_mm=(
                    terrain_maximum_printable_relief_mm
                ),
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

        mesh = AtlasTerrainPipeline._apply_surface_texture(
            mesh=mesh,
            amplitude_mm=surface_texture_amplitude_mm,
            wavelength_x_mm=surface_texture_wavelength_x_mm,
            wavelength_y_mm=surface_texture_wavelength_y_mm,
            edge_fade_mm=surface_texture_edge_fade_mm,
        )

        mesh = AtlasTerrainPipeline._apply_terracing(
            mesh=mesh,
            base_z=base_z,
            bottom_z=bottom_z,
            terrace_step_mm=terrace_step_mm,
        )

        mesh = AtlasTerrainPipeline._apply_presentation_regularization(
            mesh=mesh,
            passes=presentation_regularization_passes,
            strength=presentation_regularization_strength,
        )

        return AtlasTerrainPipeline._apply_morphology_product_profile(
            mesh=mesh,
            target_size_mm=target_size_mm,
            z_scale=z_scale,
            scene_morphology=scene_morphology,
            urban_density=urban_density,
            landmark_present=landmark_present,
            minimum_printable_relief_mm=(
                terrain_minimum_printable_relief_mm
            ),
            maximum_printable_relief_mm=(
                terrain_maximum_printable_relief_mm
            ),
        )

    @staticmethod
    def _apply_presentation_regularization(
        *,
        mesh,
        passes,
        strength,
    ):
        passes = int(passes)

        if passes <= 0:
            return mesh

        return AtlasTerrainPresentationSurfaceRegularizer.regularize(
            mesh=mesh,
            passes=passes,
            strength=strength,
        )

    @staticmethod
    def _apply_morphology_product_profile(
        *,
        mesh,
        target_size_mm,
        z_scale,
        scene_morphology,
        urban_density,
        landmark_present,
        minimum_printable_relief_mm,
        maximum_printable_relief_mm,
    ):
        if scene_morphology is None:
            return mesh

        if urban_density is None:
            raise ValueError(
                "urban_density is required when "
                "scene_morphology is enabled"
            )

        if minimum_printable_relief_mm is None:
            raise ValueError(
                "terrain_minimum_printable_relief_mm is required "
                "when scene_morphology is enabled"
            )

        if maximum_printable_relief_mm is None:
            raise ValueError(
                "terrain_maximum_printable_relief_mm is required "
                "when scene_morphology is enabled"
            )

        metadata = dict(mesh.get("metadata", {}))
        grid = mesh.get("grid", {})

        delta_height_m = metadata.get(
            "delta_height_m",
            grid.get("delta_height_m"),
        )

        if delta_height_m is None:
            raise ValueError(
                "terrain product profile requires "
                "delta_height_m terrain truth"
            )

        terrain_z_scale = float(
            metadata.get("z_scale", z_scale)
        )

        if terrain_z_scale <= 0.0:
            raise ValueError(
                "terrain z_scale must be positive"
            )

        source_elevation_range_m = float(
            delta_height_m
        )

        physical_relief_range_mm = (
            source_elevation_range_m
            / terrain_z_scale
            * 1000.0
        )

        profile = (
            AtlasMorphologyAwareTerrainProductResolver.resolve(
                scene_morphology=scene_morphology,
                source_elevation_range_m=(
                    source_elevation_range_m
                ),
                product_size_mm=target_size_mm,
                urban_density=urban_density,
                landmark_present=landmark_present,
                physical_relief_range_mm=(
                    physical_relief_range_mm
                ),
                minimum_printable_relief_mm=(
                    minimum_printable_relief_mm
                ),
                maximum_printable_relief_mm=(
                    maximum_printable_relief_mm
                ),
            )
        )

        result = dict(mesh)
        metadata["terrain_product_profile"] = profile
        result["metadata"] = metadata

        return result

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
    def _apply_surface_texture(
        mesh,
        amplitude_mm,
        wavelength_x_mm,
        wavelength_y_mm,
        edge_fade_mm,
    ):
        if (
            amplitude_mm is None
            or float(amplitude_mm) <= 0.0
        ):
            return mesh

        top_points = mesh.get("top_points")
        bottom_points = mesh.get("bottom_points")
        metadata = dict(mesh.get("metadata", {}))

        if (
            not top_points
            or not bottom_points
        ):
            raise ValueError(
                "surface texture requires a closed terrain slab"
            )

        size_x_mm = float(
            metadata.get(
                "size_x_mm",
                metadata.get("size_mm"),
            )
        )
        size_y_mm = float(
            metadata.get(
                "size_y_mm",
                metadata.get("size_mm"),
            )
        )

        texture = AtlasTerrainSurfaceTexture(
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            amplitude_mm=amplitude_mm,
            wavelength_x_mm=wavelength_x_mm,
            wavelength_y_mm=wavelength_y_mm,
            edge_fade_mm=edge_fade_mm,
        )

        textured_top_points = [
            [
                (
                    float(x),
                    float(y),
                    float(z)
                    + texture.offset_at(
                        x=float(x),
                        y=float(y),
                    ),
                )
                for x, y, z in row
            ]
            for row in top_points
        ]

        grid_size = len(textured_top_points)

        triangles = []

        triangles.extend(
            AtlasTerrainMeshGenerator
            .build_surface_triangles(
                points=textured_top_points,
                grid_size=grid_size,
            )
        )

        triangles.extend(
            AtlasTerrainMeshGenerator
            .build_bottom_triangles(
                bottom_points=bottom_points,
                grid_size=grid_size,
            )
        )

        triangles.extend(
            AtlasTerrainMeshGenerator
            .build_side_wall_triangles(
                top_points=textured_top_points,
                bottom_points=bottom_points,
                grid_size=grid_size,
            )
        )

        metadata["triangle_count"] = len(
            triangles
        )
        metadata["surface_texture"] = {
            "enabled": True,
            "amplitude_mm": float(amplitude_mm),
            "wavelength_x_mm": float(
                wavelength_x_mm
            ),
            "wavelength_y_mm": float(
                wavelength_y_mm
            ),
            "edge_fade_mm": float(
                edge_fade_mm
            ),
        }

        return {
            **mesh,
            "triangles": triangles,
            "metadata": metadata,
            "top_points": textured_top_points,
            "bottom_points": bottom_points,
        }

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
