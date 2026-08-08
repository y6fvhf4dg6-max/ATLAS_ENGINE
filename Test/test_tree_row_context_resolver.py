from CORE.atlas_tree_row_context_resolver import (
    AtlasTreeRowContextResolver,
)


def test_context_resolver_matches_nearby_parallel_road():
    tree_row = {
        "source_id": 100,
        "semantic_role": "tree_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00030, 7.00000),
        ),
    }

    roads = [
        {
            "id": 200,
            "geometry": [
                (50.00000, 7.00005),
                (50.00030, 7.00005),
            ],
            "tags": {
                "highway": "residential",
            },
        },
    ]

    result = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=roads,
        pedestrian_paths=[],
    )

    assert result["adjacent_feature_type"] == "road"
    assert result["adjacent_feature_id"] == 200
    assert result["relationship"] == "parallel"
    assert result["distance_m"] < 10.0


def test_context_resolver_matches_nearby_parallel_pedestrian_path():
    tree_row = {
        "source_id": 101,
        "semantic_role": "tree_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00030, 7.00000),
        ),
    }

    paths = [
        {
            "id": 300,
            "geometry": [
                (50.00000, 7.00004),
                (50.00030, 7.00004),
            ],
            "tags": {
                "highway": "footway",
            },
        },
    ]

    result = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=[],
        pedestrian_paths=paths,
    )

    assert result["adjacent_feature_type"] == "pedestrian_path"
    assert result["adjacent_feature_id"] == 300
    assert result["relationship"] == "parallel"
    assert result["distance_m"] < 10.0


def test_context_resolver_rejects_distant_feature():
    tree_row = {
        "source_id": 102,
        "semantic_role": "tree_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00030, 7.00000),
        ),
    }

    roads = [
        {
            "id": 400,
            "geometry": [
                (50.00000, 7.01000),
                (50.00030, 7.01000),
            ],
        },
    ]

    result = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=roads,
        pedestrian_paths=[],
    )

    assert result["adjacent_feature_type"] is None
    assert result["adjacent_feature_id"] is None
    assert result["relationship"] is None


def test_context_resolver_is_deterministic_for_equal_candidates():
    tree_row = {
        "source_id": 103,
        "semantic_role": "tree_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00030, 7.00000),
        ),
    }

    roads = [
        {
            "id": 500,
            "geometry": [
                (50.00000, 7.00005),
                (50.00030, 7.00005),
            ],
        },
        {
            "id": 200,
            "geometry": [
                (50.00000, 6.99995),
                (50.00030, 6.99995),
            ],
        },
    ]

    first = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=roads,
        pedestrian_paths=[],
    )

    second = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=list(reversed(roads)),
        pedestrian_paths=[],
    )

    assert first["adjacent_feature_id"] == 200
    assert second["adjacent_feature_id"] == 200


def test_context_resolver_prefers_parallel_structure_over_closer_crossing_path():
    tree_row = {
        "source_id": 104,
        "semantic_role": "tree_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00030, 7.00000),
        ),
    }

    pedestrian_paths = [
        {
            "id": 600,
            "geometry": [
                (50.00015, 6.99998),
                (50.00015, 7.00002),
            ],
        },
        {
            "id": 700,
            "geometry": [
                (50.00000, 7.00010),
                (50.00030, 7.00010),
            ],
        },
    ]

    result = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=[],
        pedestrian_paths=pedestrian_paths,
    )

    assert result["adjacent_feature_id"] == 700
    assert result["relationship"] == "parallel"
    assert result["direction_cosine"] >= 0.95


def test_context_resolver_rejects_only_crossing_structure():
    tree_row = {
        "source_id": 105,
        "semantic_role": "tree_row",
        "source_geometry": (
            (50.00000, 7.00000),
            (50.00030, 7.00000),
        ),
    }

    result = AtlasTreeRowContextResolver.resolve(
        row_profile=tree_row,
        roads=[],
        pedestrian_paths=[
            {
                "id": 800,
                "geometry": [
                    (50.00015, 6.99998),
                    (50.00015, 7.00002),
                ],
            },
        ],
    )

    assert result["adjacent_feature_type"] is None
    assert result["adjacent_feature_id"] is None
    assert result["relationship"] is None
