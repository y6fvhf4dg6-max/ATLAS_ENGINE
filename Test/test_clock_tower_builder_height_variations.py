from CORE.atlas_clock_tower_builder import (
    AtlasClockTowerBuilder,
)


class Landmark:
    geometry = [
        (0.0, 0.0),
        (2.0, 0.0),
        (2.0, 2.0),
        (0.0, 2.0),
    ]

    tags = {
        "height": "about 50m",
        "min_height": "18",
    }


def test_clock_tower_uses_min_height_when_height_invalid():
    geometry = AtlasClockTowerBuilder.build(
        Landmark()
    )

    assert geometry.height_m == 18.0
