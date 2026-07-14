# CORE/atlas_foundation_surface_builder.py

from CORE.atlas_foundation_sampler import AtlasFoundationSampler


class AtlasFoundationSurfaceBuilder:
    """
    ATLAS Foundation Surface Builder v0.2

    Görev:
    - Bina footprint'i altındaki terrain'i örneklemek.
    - Foundation için güvenli referans kotunu üretmek.

    Bu sınıf mesh üretmez.
    Bu sınıf bina üretmez.
    """

    DEFAULT_SAMPLE_GRID = 5
    DEFAULT_EMBED_DEPTH_MM = 0.30
    DEFAULT_PLACEMENT_PERCENTILE = 0.10

    @staticmethod
    def build_surface(
        terrain_mesh,
        bounds,
        footprint_points=None,
        sample_grid=DEFAULT_SAMPLE_GRID,
        embed_depth_mm=DEFAULT_EMBED_DEPTH_MM,
        placement_percentile=DEFAULT_PLACEMENT_PERCENTILE,
    ):
        if footprint_points:
            terrain_values = AtlasFoundationSampler.sample_polygon(
                terrain_mesh=terrain_mesh,
                footprint_points=footprint_points,
                sample_grid=sample_grid,
            )

            sample_mode = "footprint"
        else:
            terrain_values = AtlasFoundationSampler.sample_bounds(
                terrain_mesh=terrain_mesh,
                bounds=bounds,
                sample_grid=sample_grid,
            )

            sample_mode = "bounds"

        if not terrain_values:
            return None

        terrain_values = sorted(terrain_values)

        highest = terrain_values[-1]
        lowest = terrain_values[0]
        average = sum(terrain_values) / len(terrain_values)

        placement_percentile = max(
            0.0,
            min(
                1.0,
                float(placement_percentile),
            ),
        )

        reference_index = round(
            (len(terrain_values) - 1)
            * placement_percentile
        )

        reference_z = terrain_values[reference_index]
        foundation_z = reference_z - embed_depth_mm

        return {
            "foundation_z": foundation_z,
            "reference_z": reference_z,
            "placement_percentile": placement_percentile,
            "sample_mode": sample_mode,
            "highest_z": highest,
            "lowest_z": lowest,
            "average_z": average,
            "sample_count": len(terrain_values),
            "terrain_values": terrain_values,
        }
