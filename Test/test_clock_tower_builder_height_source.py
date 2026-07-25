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
        "height": "52",
    }


def test_clock_tower_prefers_height_tag():
    geometry = AtlasClockTowerBuilder.build(
        Landmark()
    )

    assert geometry.height_m == 52.0
