import pytest

from CORE.atlas_park_plaza_semantic_resolver import (
    AtlasParkPlazaSemanticResolver,
)


@pytest.mark.parametrize(
    ("tags", "expected"),
    (
        ({"leisure": "park"}, "park"),
        ({"leisure": "garden"}, "garden"),
        ({"place": "square"}, "plaza"),
        (
            {"highway": "pedestrian", "area": "yes"},
            "pedestrian_square",
        ),
    ),
)
def test_park_plaza_semantic_resolver_classifies_core_surface_types(
    tags,
    expected,
):
    assert (
        AtlasParkPlazaSemanticResolver.resolve_semantic_class(tags)
        == expected
    )


@pytest.mark.parametrize(
    ("tags", "expected"),
    (
        ({"landuse": "grass"}, "grass_area"),
        ({"landuse": "cemetery"}, "cemetery"),
        ({"leisure": "pitch"}, "sports_field"),
    ),
)
def test_park_plaza_semantic_resolver_classifies_additional_open_surfaces(
    tags,
    expected,
):
    assert (
        AtlasParkPlazaSemanticResolver.resolve_semantic_class(tags)
        == expected
    )


def test_park_plaza_semantic_resolver_accepts_geometry_derived_courtyard():
    assert (
        AtlasParkPlazaSemanticResolver.resolve_semantic_class(
            {},
            geometry_role="courtyard",
        )
        == "courtyard"
    )


def test_pedestrian_square_semantics_override_generic_plaza():
    tags = {
        "place": "square",
        "highway": "pedestrian",
        "area": "yes",
    }

    assert (
        AtlasParkPlazaSemanticResolver.resolve_semantic_class(tags)
        == "pedestrian_square"
    )


def test_park_profile_exposes_composition_capabilities():
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(
        {"leisure": "park"},
    )

    assert profile.semantic_class == "park"
    assert profile.ground_surface_role == "park_ground"
    assert profile.supports_internal_paths is True
    assert profile.supports_tree_rows is True
    assert profile.supports_vegetation_clusters is True


def test_plaza_profile_remains_distinct_from_park_composition():
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(
        {"place": "square"},
    )

    assert profile.semantic_class == "plaza"
    assert profile.ground_surface_role == "plaza_ground"
    assert profile.supports_internal_paths is False
    assert profile.supports_tree_rows is False
    assert profile.supports_vegetation_clusters is False


def test_pedestrian_square_profile_remains_distinct_from_generic_plaza():
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(
        {
            "highway": "pedestrian",
            "area": "yes",
        },
    )

    assert profile.semantic_class == "pedestrian_square"
    assert profile.ground_surface_role == "pedestrian_square_ground"
    assert profile.supports_internal_paths is False
    assert profile.supports_tree_rows is False
    assert profile.supports_vegetation_clusters is False


@pytest.mark.parametrize(
    ("tags", "semantic_class", "ground_role", "paths", "rows", "clusters"),
    (
        (
            {"leisure": "garden"},
            "garden",
            "garden_ground",
            True,
            True,
            True,
        ),
        (
            {"landuse": "grass"},
            "grass_area",
            "grass_ground",
            False,
            False,
            False,
        ),
    ),
)
def test_open_surface_profiles_keep_distinct_composition_capabilities(
    tags,
    semantic_class,
    ground_role,
    paths,
    rows,
    clusters,
):
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(tags)

    assert profile.semantic_class == semantic_class
    assert profile.ground_surface_role == ground_role
    assert profile.supports_internal_paths is paths
    assert profile.supports_tree_rows is rows
    assert profile.supports_vegetation_clusters is clusters


@pytest.mark.parametrize(
    ("tags", "semantic_class", "ground_role"),
    (
        (
            {"landuse": "cemetery"},
            "cemetery",
            "cemetery_ground",
        ),
        (
            {"leisure": "pitch"},
            "sports_field",
            "sports_field_ground",
        ),
    ),
)
def test_cemetery_and_sports_field_profiles_remain_distinct(
    tags,
    semantic_class,
    ground_role,
):
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(tags)

    assert profile.semantic_class == semantic_class
    assert profile.ground_surface_role == ground_role
    assert profile.supports_internal_paths is False
    assert profile.supports_tree_rows is False
    assert profile.supports_vegetation_clusters is False


def test_geometry_derived_courtyard_has_distinct_surface_profile():
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(
        {},
        geometry_role="courtyard",
    )

    assert profile.semantic_class == "courtyard"
    assert profile.ground_surface_role == "courtyard_ground"
    assert profile.supports_internal_paths is False
    assert profile.supports_tree_rows is False
    assert profile.supports_vegetation_clusters is False


def test_park_plaza_semantic_resolver_enriches_reader_record_without_mutation():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["source_id"] == 42
    assert result["semantic_class"] == "park"
    assert result["ground_surface_role"] == "park_ground"
    assert result["geometry"] == source["geometry"]
    assert result["source_park_type"] == "leisure:park"
    assert "semantic_class" not in source


def test_surface_record_preserves_source_internal_paths():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "internal_paths": (
            {
                "id": 100,
                "geometry": (
                    (50.01, 7.01),
                    (50.05, 7.05),
                ),
            },
        ),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["internal_paths"] == source["internal_paths"]
    assert result["supports_internal_paths"] is True


def test_surface_record_preserves_source_tree_rows():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "tree_rows": (
            {
                "id": 200,
                "geometry": (
                    (50.01, 7.02),
                    (50.08, 7.02),
                ),
            },
        ),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["tree_rows"] == source["tree_rows"]
    assert result["supports_tree_rows"] is True


def test_surface_record_preserves_source_vegetation_clusters():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "vegetation_clusters": (
            {
                "id": 300,
                "geometry": (
                    (50.02, 7.02),
                    (50.02, 7.04),
                    (50.04, 7.04),
                ),
            },
        ),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert (
        result["vegetation_clusters"]
        == source["vegetation_clusters"]
    )
    assert result["supports_vegetation_clusters"] is True


def test_surface_record_preserves_source_clearings():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "clearings": (
            {
                "id": 400,
                "geometry": (
                    (50.03, 7.03),
                    (50.03, 7.05),
                    (50.05, 7.05),
                ),
            },
        ),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["clearings"] == source["clearings"]


def test_surface_record_preserves_source_borders_and_edges():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "borders": (
            {
                "id": 500,
                "geometry": (
                    (50.0, 7.0),
                    (50.0, 7.1),
                ),
            },
        ),
        "edges": (
            {
                "id": 501,
                "geometry": (
                    (50.0, 7.1),
                    (50.1, 7.1),
                ),
            },
        ),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["borders"] == source["borders"]
    assert result["edges"] == source["edges"]


def test_park_surface_record_reports_deterministic_composition_layers():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "internal_paths": ({"id": 100},),
        "tree_rows": ({"id": 200},),
        "vegetation_clusters": ({"id": 300},),
        "clearings": ({"id": 400},),
        "borders": ({"id": 500},),
        "edges": ({"id": 501},),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["composition_layers"] == (
        "park_ground",
        "internal_paths",
        "tree_rows",
        "vegetation_clusters",
        "clearings",
        "borders",
        "edges",
    )


def test_plaza_composition_ignores_unsupported_park_layers():
    source = {
        "id": 99,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"place": "square"},
        "park_type": "place:square",
        "internal_paths": ({"id": 100},),
        "tree_rows": ({"id": 200},),
        "vegetation_clusters": ({"id": 300},),
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["composition_layers"] == (
        "plaza_ground",
    )


def test_park_profile_exposes_extended_composition_capabilities():
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(
        {"leisure": "park"},
    )

    assert profile.supports_clearings is True
    assert profile.supports_borders is True
    assert profile.supports_edges is True


def test_plaza_profile_rejects_extended_park_composition_capabilities():
    profile = AtlasParkPlazaSemanticResolver.resolve_profile(
        {"place": "square"},
    )

    assert profile.supports_clearings is False
    assert profile.supports_borders is False
    assert profile.supports_edges is False


def test_surface_record_exposes_extended_composition_capabilities():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 7.0),
            (50.0, 7.1),
            (50.1, 7.1),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
    }

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(source)

    assert result["supports_clearings"] is True
    assert result["supports_borders"] is True
    assert result["supports_edges"] is True


def test_park_surface_record_resolves_internal_pedestrian_paths():
    source = {
        "id": 42,
        "geometry": (
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
    }

    pedestrian_paths = (
        {
            "id": 100,
            "geometry": (
                (2.0, 2.0),
                (8.0, 8.0),
            ),
            "tags": {"highway": "footway"},
            "road_type": "footway",
        },
        {
            "id": 101,
            "geometry": (
                (20.0, 20.0),
                (30.0, 30.0),
            ),
            "tags": {"highway": "footway"},
            "road_type": "footway",
        },
    )

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(
        source,
        pedestrian_paths=pedestrian_paths,
    )

    assert tuple(
        path["id"]
        for path in result["internal_paths"]
    ) == (100,)


def test_park_surface_record_rejects_path_that_crosses_park_boundary():
    source = {
        "id": 42,
        "geometry": (
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
    }

    pedestrian_paths = (
        {
            "id": 100,
            "geometry": (
                (-2.0, 5.0),
                (12.0, 5.0),
            ),
            "tags": {"highway": "footway"},
            "road_type": "footway",
        },
    )

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(
        source,
        pedestrian_paths=pedestrian_paths,
    )

    assert result["internal_paths"] == ()
    assert result["composition_layers"] == (
        "park_ground",
    )


def test_park_surface_record_deduplicates_internal_paths_by_id():
    source = {
        "id": 42,
        "geometry": (
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
        "internal_paths": (
            {
                "id": 100,
                "geometry": (
                    (2.0, 2.0),
                    (8.0, 8.0),
                ),
            },
        ),
    }

    pedestrian_paths = (
        {
            "id": 100,
            "geometry": (
                (2.0, 2.0),
                (8.0, 8.0),
            ),
            "tags": {"highway": "footway"},
            "road_type": "footway",
        },
    )

    result = AtlasParkPlazaSemanticResolver.resolve_surface_record(
        source,
        pedestrian_paths=pedestrian_paths,
    )

    assert tuple(
        path["id"]
        for path in result["internal_paths"]
    ) == (100,)


def test_surface_record_rejects_non_mapping_source():
    with pytest.raises(TypeError, match="source must be a mapping"):
        AtlasParkPlazaSemanticResolver.resolve_surface_record(
            source=None,
        )


def test_surface_record_rejects_non_mapping_tags():
    source = {
        "id": 42,
        "geometry": (),
        "tags": None,
    }

    with pytest.raises(TypeError, match="tags must be a mapping"):
        AtlasParkPlazaSemanticResolver.resolve_surface_record(
            source=source,
        )


def test_semantic_class_rejects_non_mapping_tags():
    with pytest.raises(TypeError, match="tags must be a mapping"):
        AtlasParkPlazaSemanticResolver.resolve_semantic_class(
            None,
        )


def test_internal_pedestrian_path_resolution_is_deterministic():
    source = {
        "id": 42,
        "geometry": (
            (0.0, 0.0),
            (0.0, 10.0),
            (10.0, 10.0),
            (10.0, 0.0),
        ),
        "tags": {"leisure": "park"},
        "park_type": "leisure:park",
    }

    paths = (
        {
            "id": 200,
            "geometry": ((2.0, 2.0), (8.0, 2.0)),
        },
        {
            "id": 100,
            "geometry": ((2.0, 8.0), (8.0, 8.0)),
        },
    )

    first = AtlasParkPlazaSemanticResolver.resolve_surface_record(
        source,
        pedestrian_paths=paths,
    )
    second = AtlasParkPlazaSemanticResolver.resolve_surface_record(
        source,
        pedestrian_paths=tuple(reversed(paths)),
    )

    assert tuple(path["id"] for path in first["internal_paths"]) == (
        100,
        200,
    )
    assert first["internal_paths"] == second["internal_paths"]
