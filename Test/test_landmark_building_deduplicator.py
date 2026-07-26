from CORE.atlas_landmark_building_deduplicator import (
    AtlasLandmarkBuildingDeduplicator,
)


def _record(object_id, **tags):
    return {
        "id": object_id,
        "geometry": (
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ),
        "tags": tags,
    }


def test_removes_observation_tower_from_buildings_when_landmark_owns_same_osm_object():
    atakule = _record(
        72079962,
        man_made="tower",
        **{
            "tower:type": "observation",
            "building:part": "yes",
            "height": "125",
        },
    )

    result = AtlasLandmarkBuildingDeduplicator.filter_buildings(
        raw_buildings=[atakule],
        landmarks=[atakule],
    )

    assert result == []


def test_preserves_minaret_for_specialized_building_pipeline():
    minaret = _record(
        1267126578,
        man_made="tower",
        building="yes",
        **{"tower:type": "minaret"},
    )

    result = AtlasLandmarkBuildingDeduplicator.filter_buildings(
        raw_buildings=[minaret],
        landmarks=[minaret],
    )

    assert result == [minaret]


def test_preserves_building_owned_tower_profiles():
    records = [
        _record(
            1,
            man_made="tower",
            building="yes",
            **{"tower:type": "bell_tower"},
        ),
        _record(
            2,
            man_made="tower",
            building="yes",
            **{"tower:type": "staircase"},
        ),
        _record(
            3,
            man_made="tower",
            building="yes",
            **{"tower:type": "office"},
        ),
    ]

    result = AtlasLandmarkBuildingDeduplicator.filter_buildings(
        raw_buildings=records,
        landmarks=records,
    )

    assert result == records


def test_preserves_unrelated_normal_buildings():
    building = _record(
        99,
        building="house",
    )
    observation_tower = _record(
        100,
        man_made="tower",
        **{"tower:type": "observation"},
    )

    result = AtlasLandmarkBuildingDeduplicator.filter_buildings(
        raw_buildings=[building],
        landmarks=[observation_tower],
    )

    assert result == [building]
