from CORE.atlas_green_area_tree_sampler import (
    AtlasGreenAreaTreeSampler,
)


FOREST_PARK = {
    "id": 101,
    "geometry": [
        (50.0000, 8.0000),
        (50.0000, 8.0010),
        (50.0010, 8.0010),
        (50.0010, 8.0000),
    ],
    "park_type": "landuse:forest",
    "tags": {
        "landuse": "forest",
    },
}


def test_sampler_returns_deterministic_tree_records_inside_forest():
    first = AtlasGreenAreaTreeSampler.sample(
        parks=[FOREST_PARK],
        existing_trees=[],
        max_trees=20,
    )

    second = AtlasGreenAreaTreeSampler.sample(
        parks=[FOREST_PARK],
        existing_trees=[],
        max_trees=20,
    )

    assert first
    assert first == second
    assert len(first) <= 20

    for tree in first:
        assert 50.0000 < tree["lat"] < 50.0010
        assert 8.0000 < tree["lon"] < 8.0010
        assert tree["tree_type"] == "tree"
        assert tree["tags"]["source"] == "osm_green_area_fill"
        assert tree["tags"]["park_id"] == 101
        assert tree["tags"]["park_type"] == "landuse:forest"


def test_sampler_accepts_only_supported_green_area_types():
    parks = [
        {
            **FOREST_PARK,
            "id": 201,
            "park_type": "landuse:forest",
        },
        {
            **FOREST_PARK,
            "id": 202,
            "park_type": "natural:wood",
        },
        {
            **FOREST_PARK,
            "id": 203,
            "park_type": "natural:scrub",
        },
        {
            **FOREST_PARK,
            "id": 204,
            "park_type": "leisure:park",
        },
        {
            **FOREST_PARK,
            "id": 205,
            "park_type": "leisure:garden",
        },
    ]

    result = AtlasGreenAreaTreeSampler.sample(
        parks=parks,
        existing_trees=[],
        max_trees=100,
    )

    sampled_park_types = {
        tree["tags"]["park_type"]
        for tree in result
    }

    assert sampled_park_types == {
        "landuse:forest",
        "natural:wood",
        "natural:scrub",
        "leisure:park",
        "leisure:garden",
    }


def test_sampler_rejects_open_grass_and_recreation_areas():
    excluded_types = [
        "landuse:grass",
        "landuse:meadow",
        "landuse:recreation_ground",
        "leisure:playground",
        "leisure:recreation_ground",
        "natural:grassland",
    ]

    parks = [
        {
            **FOREST_PARK,
            "id": 300 + index,
            "park_type": park_type,
        }
        for index, park_type in enumerate(excluded_types)
    ]

    result = AtlasGreenAreaTreeSampler.sample(
        parks=parks,
        existing_trees=[],
        max_trees=100,
    )

    assert result == []


def test_sampler_respects_global_tree_limit():
    result = AtlasGreenAreaTreeSampler.sample(
        parks=[
            {
                **FOREST_PARK,
                "id": 401,
            },
            {
                **FOREST_PARK,
                "id": 402,
            },
        ],
        existing_trees=[],
        max_trees=7,
    )

    assert len(result) == 7


def test_sampler_returns_empty_for_zero_limit():
    result = AtlasGreenAreaTreeSampler.sample(
        parks=[FOREST_PARK],
        existing_trees=[],
        max_trees=0,
    )

    assert result == []


def test_sampler_avoids_existing_tree_position():
    existing_tree = {
        "id": "existing_1",
        "lat": 50.0005,
        "lon": 8.0005,
        "tree_type": "tree",
    }

    result = AtlasGreenAreaTreeSampler.sample(
        parks=[FOREST_PARK],
        existing_trees=[existing_tree],
        max_trees=20,
    )

    assert result

    for tree in result:
        assert (
            tree["lat"],
            tree["lon"],
        ) != (
            existing_tree["lat"],
            existing_tree["lon"],
        )


def test_sampler_limits_candidates_to_bbox():
    park = {
        "id": 501,
        "geometry": [
            (49.9990, 7.9990),
            (49.9990, 8.0020),
            (50.0020, 8.0020),
            (50.0020, 7.9990),
        ],
        "park_type": "landuse:forest",
        "tags": {
            "landuse": "forest",
        },
    }

    result = AtlasGreenAreaTreeSampler.sample(
        parks=[park],
        existing_trees=[],
        max_trees=30,
        bbox=(
            50.0000,
            8.0000,
            50.0010,
            8.0010,
        ),
    )

    assert result

    for tree in result:
        assert 50.0000 <= tree["lat"] <= 50.0010
        assert 8.0000 <= tree["lon"] <= 8.0010
