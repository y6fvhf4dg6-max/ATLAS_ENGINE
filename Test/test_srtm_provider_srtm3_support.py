import numpy as np

from CORE.providers.atlas_srtm_provider import AtlasSRTMProvider


def test_accepts_srtm3_tile_size(tmp_path):
    tile_path = tmp_path / "N41E028.hgt"

    data = np.zeros((1201 * 1201,), dtype=">i2")
    data.tofile(tile_path)

    provider = AtlasSRTMProvider()

    loaded = provider._load_tile(tile_path)

    assert loaded.shape == (1201, 1201)
