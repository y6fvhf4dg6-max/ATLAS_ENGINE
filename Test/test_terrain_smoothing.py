"""
ATLAS Terrain Smoothing Regression Tests

Ürün terrain profilinde mikro yükseklik gürültüsünün azaltılmasını,
ana grid yapısının ve düz yüzeylerin korunmasını doğrular.
"""

import pytest

from CORE.atlas_terrain_mesh_generator import (
    AtlasTerrainMeshGenerator,
)


def test_flat_height_grid_remains_unchanged():
    heights = [
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0],
        [100.0, 100.0, 100.0],
    ]

    smoothed = AtlasTerrainMeshGenerator.smooth_heights(
        heights=heights,
        passes=1,
    )

    assert smoothed == heights


def test_single_cell_spike_is_reduced():
    heights = [
        [100.0, 100.0, 100.0],
        [100.0, 130.0, 100.0],
        [100.0, 100.0, 100.0],
    ]

    smoothed = AtlasTerrainMeshGenerator.smooth_heights(
        heights=heights,
        passes=1,
    )

    assert smoothed[1][1] < 130.0
    assert smoothed[1][1] == pytest.approx(
        100.0 + (30.0 / 9.0)
    )


def test_smoothing_preserves_grid_dimensions():
    heights = [
        [100.0, 101.0, 102.0, 103.0],
        [104.0, 105.0, 106.0, 107.0],
        [108.0, 109.0, 110.0, 111.0],
    ]

    smoothed = AtlasTerrainMeshGenerator.smooth_heights(
        heights=heights,
        passes=2,
    )

    assert len(smoothed) == 3
    assert all(len(row) == 4 for row in smoothed)


class SpikeTerrainProvider:
    def get_height(
        self,
        lat,
        lon,
    ):
        if lat == pytest.approx(0.5) and lon == pytest.approx(0.5):
            return 130.0

        return 100.0


def test_surface_mesh_applies_optional_smoothing_and_updates_metadata():
    mesh = AtlasTerrainMeshGenerator.build_surface_mesh(
        terrain_provider=SpikeTerrainProvider(),
        bbox=(
            0.0,
            0.0,
            1.0,
            1.0,
        ),
        size_mm=100.0,
        grid_size=3,
        z_scale=5500.0,
        base_z=0.8,
        smoothing_passes=1,
    )

    height_grid = mesh["grid"]

    assert height_grid["heights"][1][1] == pytest.approx(
        100.0 + (30.0 / 9.0)
    )

    assert height_grid["max_height_m"] == pytest.approx(
        100.0 + (30.0 / 9.0)
    )

    assert height_grid["delta_height_m"] == pytest.approx(
        30.0 / 9.0
    )

    assert mesh["metadata"]["smoothing_passes"] == 1
