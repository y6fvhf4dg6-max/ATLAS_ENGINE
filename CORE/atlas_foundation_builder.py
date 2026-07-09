# CORE/atlas_foundation_builder.py

from CORE.atlas_foundation_surface_builder import (
    AtlasFoundationSurfaceBuilder,
)


class AtlasFoundationBuilder:
    """
    ATLAS Foundation Builder v0.1

    Görev

    Terrain
        ↓
    Foundation Surface
        ↓
    Foundation Z

    Bu sınıf mesh üretmez.
    Bu sınıf bina üretmez.

    Sadece foundation oluşturur.
    """

    @staticmethod
    def build(
        terrain_mesh,
        bounds,
        sample_grid=5,
        embed_depth_mm=0.30,
    ):
        return AtlasFoundationSurfaceBuilder.build_surface(
            terrain_mesh=terrain_mesh,
            bounds=bounds,
            sample_grid=sample_grid,
            embed_depth_mm=embed_depth_mm,
        )
