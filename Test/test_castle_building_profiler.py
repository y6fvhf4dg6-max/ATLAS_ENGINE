from CORE.atlas_castle_building_profiler import (
    AtlasCastleBuildingProfiler,
)


def test_historic_city_gate_is_classified_as_gate_tower():
    raw_building = {
        "id": 1091855400,
        "geometry": [
            (48.0, 12.0),
            (48.0, 12.00005),
            (48.00005, 12.00005),
            (48.00005, 12.0),
        ],
        "tags": {
            "building": "yes",
            "historic": "city_gate",
            "name": "Georgstor",
        },
    }

    profile = AtlasCastleBuildingProfiler._classify(
        raw_building
    )

    assert profile == "gate_tower"


def test_generic_historic_building_remains_unknown():
    raw_building = {
        "id": 290215702,
        "geometry": [
            (48.0, 8.0),
            (48.0, 8.00005),
            (48.00005, 8.00005),
            (48.00005, 8.0),
        ],
        "tags": {
            "building": "yes",
            "historic": "yes",
        },
    }

    profile = AtlasCastleBuildingProfiler._classify(
        raw_building
    )

    assert profile == "unknown_castle_building"
