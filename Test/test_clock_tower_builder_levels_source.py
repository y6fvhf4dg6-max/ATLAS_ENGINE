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
        "building:levels": "12",
    }


def test_clock_tower_uses_building_levels_when_height_missing():
    geometry = AtlasClockTowerBuilder.build(
        Landmark()
    )

    assert geometry.height_m == (
        12 * AtlasClockTowerBuilder.FLOOR_HEIGHT_M
    )
