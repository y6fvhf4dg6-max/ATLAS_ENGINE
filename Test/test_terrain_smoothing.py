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
