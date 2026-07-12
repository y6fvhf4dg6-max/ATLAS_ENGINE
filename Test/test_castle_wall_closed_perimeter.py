"""
ATLAS Castle Wall Closed Perimeter Regression Test

Classifier tarafından inferred perimeter olarak işaretlenen
kale sınırlarının Wall Builder tarafından fiziksel olarak
kapalı kabul edilmesini doğrular.
"""

from CORE.atlas_castle_wall_builder import (
    AtlasCastleWallBuilder,
)


def test_inferred_perimeter_wall_is_closed():
    wall = {
        "id": 68741063,
        "inferred": True,
        "wall_type": "inferred_castle_perimeter",
        "geometry": [
            (48.1564993, 12.8288699),
            (48.1568000, 12.8295000),
            (48.1571000, 12.8287000),
            (48.1564860, 12.8289046),
        ],
        "tags": {
            "historic": "castle",
        },
    }

    points = [
        (10.0, 10.0),
        (20.0, 10.0),
        (20.0, 20.0),
        (10.2, 10.1),
    ]

    result = AtlasCastleWallBuilder._is_closed_wall(
        wall=wall,
        points=points,
    )

    assert result is True


if __name__ == "__main__":
    test_inferred_perimeter_wall_is_closed()

    print("PASS: " "test_inferred_perimeter_wall_is_closed")


def test_historic_castle_wall_tag_is_recognized():
    from CORE.atlas_local_osm_reader import (
        AtlasLocalOSMReader,
    )

    assert (
        AtlasLocalOSMReader._is_castle_wall(
            {
                "building": "yes",
                "historic": "castle_wall",
            }
        )
        is True
    )


def test_existing_city_wall_tags_remain_supported():
    from CORE.atlas_local_osm_reader import (
        AtlasLocalOSMReader,
    )

    assert (
        AtlasLocalOSMReader._is_castle_wall(
            {
                "barrier": "city_wall",
            }
        )
        is True
    )

    assert (
        AtlasLocalOSMReader._is_castle_wall(
            {
                "historic": "citywalls",
            }
        )
        is True
    )


def test_regular_building_is_not_castle_wall():
    from CORE.atlas_local_osm_reader import (
        AtlasLocalOSMReader,
    )

    assert (
        AtlasLocalOSMReader._is_castle_wall(
            {
                "building": "yes",
            }
        )
        is False
    )
