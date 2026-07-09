# CORE/atlas_foundation_surface_builder.py

from CORE.atlas_foundation_sampler import AtlasFoundationSampler


class AtlasFoundationSurfaceBuilder:
    """
    ATLAS Foundation Surface Builder v0.1

    Görev:
    - Bina footprint'i altındaki terrain'i örneklemek.
    - Foundation için güvenli referans kotunu üretmek.

    Bu sınıf mesh üretmez.
    Bu sınıf bina üretmez.
    """

    DEFAULT_SAMPLE_GRID = 5
    DEFAULT_EMBED_DEPTH_MM = 0.30

    @staticmethod
    def build_surface(
        terrain_mesh,
        bounds,
        sample_grid=DEFAULT_SAMPLE_GRID,
        embed_depth_mm=DEFAULT_EMBED_DEPTH_MM,
    ):
        terrain_values = AtlasFoundationSampler.sample_bounds(
            terrain_mesh=terrain_mesh,
            bounds=bounds,
            sample_grid=sample_grid,
        )

        if not terrain_values:
            return None

        terrain_values = sorted(terrain_values)

        highest = terrain_values[-1]
        lowest = terrain_values[0]
        average = sum(terrain_values) / len(terrain_values)

        foundation_z = lowest - embed_depth_mm

        return {
            "foundation_z": foundation_z,
            "highest_z": highest,
            "lowest_z": lowest,
            "average_z": average,
            "sample_count": len(terrain_values),
            "terrain_values": terrain_values,
        }
