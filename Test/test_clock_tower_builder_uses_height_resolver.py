from unittest.mock import patch

from CORE.atlas_clock_tower_builder import (
    AtlasClockTowerBuilder,
)


class Landmark:
    geometry = [
        (0.0, 0.0),
        (1.0, 0.0),
        (1.0, 1.0),
        (0.0, 1.0),
    ]

    tags = {}


def test_clock_tower_builder_uses_height_resolver():
    with patch(
        "CORE.atlas_clock_tower_builder.AtlasLandmarkHeightResolver.resolve",
        return_value=77.0,
    ) as resolve:

        geometry = AtlasClockTowerBuilder.build(
            Landmark()
        )

    resolve.assert_called_once()
    assert geometry.height_m == 77.0
