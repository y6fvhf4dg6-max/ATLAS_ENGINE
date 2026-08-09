import pytest

from CORE.providers.atlas_opentopography_provider import (
    AtlasOpenTopographyProvider,
)


def test_height_from_grid_bilinearly_interpolates_between_samples():
    provider = object.__new__(
        AtlasOpenTopographyProvider
    )

    grid = {
        "ncols": 2,
        "nrows": 2,
        "west": 28.0,
        "south": 41.0,
        "east": 29.0,
        "north": 42.0,
        "cellsize": 1.0,
        "nodata_value": -9999.0,
        # AAIGrid rows start from north:
        # north-west=100, north-east=200
        # south-west=300, south-east=400
        "values": [
            [100.0, 200.0],
            [300.0, 400.0],
        ],
    }

    height = provider._height_from_grid(
        grid,
        lat=41.5,
        lon=28.5,
    )

    assert height == pytest.approx(
        250.0,
        abs=1e-9,
    )
