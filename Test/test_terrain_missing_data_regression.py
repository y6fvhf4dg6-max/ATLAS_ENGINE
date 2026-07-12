import pytest

from CORE.atlas_terrain_mesh_generator import (
    AtlasTerrainMeshGenerator,
)


class MissingTerrainProvider:
    def get_height(
        self,
        lat,
        lon,
    ):
        return None


class PartiallyMissingTerrainProvider:
    def get_height(
        self,
        lat,
        lon,
    ):
        if lat > 0.5 and lon > 0.5:
            return None

        return 100.0 + lat + lon


def test_all_missing_terrain_data_stops_generation():
    provider = MissingTerrainProvider()

    with pytest.raises(
        RuntimeError,
        match="Terrain height data unavailable",
    ):
        AtlasTerrainMeshGenerator.build_height_grid(
            terrain_provider=provider,
            bbox=(
                0.0,
                0.0,
                1.0,
                1.0,
            ),
            grid_size=3,
        )


def test_partial_missing_terrain_data_uses_valid_fallback():
    provider = PartiallyMissingTerrainProvider()

    result = AtlasTerrainMeshGenerator.build_height_grid(
        terrain_provider=provider,
        bbox=(
            0.0,
            0.0,
            1.0,
            1.0,
        ),
        grid_size=3,
    )

    assert result["sample_count"] == 9
    assert result["missing_sample_count"] == 1

    assert result["min_height_m"] == pytest.approx(100.0)

    assert result["max_height_m"] == pytest.approx(101.5)

    assert result["delta_height_m"] == pytest.approx(1.5)

    assert all(height is not None for row in result["heights"] for height in row)

    assert result["heights"][2][2] == pytest.approx(result["min_height_m"])
