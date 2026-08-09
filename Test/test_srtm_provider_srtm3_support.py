import numpy as np
import pytest

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider


def test_accepts_srtm3_tile_size(tmp_path):
    tile_path = tmp_path / "N41E028.hgt"

    data = np.zeros((1201 * 1201,), dtype=">i2")
    data.tofile(tile_path)

    provider = AtlasSRTMProvider()

    loaded = provider._load_tile(tile_path)

    assert loaded.shape == (1201, 1201)


def test_get_height_bilinearly_interpolates_between_srtm_samples(
    tmp_path,
):
    tile_path = tmp_path / "N41E028.hgt"

    data = np.zeros(
        (1201, 1201),
        dtype=">i2",
    )

    # Query point will land exactly halfway between
    # these four native raster samples.
    row0 = 600
    row1 = 601
    col0 = 600
    col1 = 601

    data[row0, col0] = 100
    data[row0, col1] = 200
    data[row1, col0] = 300
    data[row1, col1] = 400

    data.tofile(tile_path)

    provider = AtlasSRTMProvider(
        data_dir=str(tmp_path),
        debug=False,
    )

    tile_size = 1201
    denominator = tile_size - 1

    row_position = 600.5
    col_position = 600.5

    lat = (
        42.0
        - row_position / denominator
    )
    lon = (
        28.0
        + col_position / denominator
    )

    height = provider.get_height(
        lat,
        lon,
    )

    assert height == pytest.approx(250.0, abs=1e-9)
