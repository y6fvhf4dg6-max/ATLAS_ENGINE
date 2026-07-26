from CORE.atlas_bridge_landmark_deduplicator import (
    AtlasBridgeLandmarkDeduplicator,
)


def test_prefers_man_made_bridge_over_same_wikidata_centerline():
    landmarks = [
        {
            "id": 4885624,
            "tags": {
                "bridge": "yes",
                "highway": "primary",
                "name": "Galata Köprüsü",
                "wikidata": "Q81523",
            },
        },
        {
            "id": 280961352,
            "tags": {
                "man_made": "bridge",
                "name": "Galata Köprüsü",
                "wikidata": "Q81523",
            },
        },
    ]

    filtered = AtlasBridgeLandmarkDeduplicator.filter_landmarks(
        landmarks
    )

    assert [item["id"] for item in filtered] == [280961352]


def test_keeps_bridges_with_different_wikidata_ids():
    landmarks = [
        {
            "id": 280961352,
            "tags": {
                "man_made": "bridge",
                "name": "Galata Köprüsü",
                "wikidata": "Q81523",
            },
        },
        {
            "id": 619249707,
            "tags": {
                "man_made": "bridge",
                "name": "Atatürk Köprüsü",
                "wikidata": "Q4812886",
            },
        },
    ]

    filtered = AtlasBridgeLandmarkDeduplicator.filter_landmarks(
        landmarks
    )

    assert [item["id"] for item in filtered] == [
        280961352,
        619249707,
    ]


def test_keeps_non_bridge_landmarks_unchanged():
    landmarks = [
        {
            "id": 72079962,
            "tags": {
                "man_made": "tower",
                "tower:type": "observation",
            },
        },
    ]

    filtered = AtlasBridgeLandmarkDeduplicator.filter_landmarks(
        landmarks
    )

    assert filtered == landmarks


def test_uses_normalized_name_when_wikidata_is_missing():
    landmarks = [
        {
            "id": 101,
            "tags": {
                "bridge": "yes",
                "highway": "primary",
                "name": "Galata Köprüsü",
            },
        },
        {
            "id": 102,
            "tags": {
                "man_made": "bridge",
                "name": "  galata köprüsü  ",
            },
        },
    ]

    filtered = AtlasBridgeLandmarkDeduplicator.filter_landmarks(
        landmarks
    )

    assert [item["id"] for item in filtered] == [102]
