import dataclasses

import pytest

from CORE.atlas_vegetation_composition_resolver import (
    AtlasVegetationCompositionProfile,
)


@pytest.mark.parametrize(
    ("semantic_role", "representation_mode"),
    (
        ("isolated_tree", "individual"),
        ("tree_row", "ordered_row"),
        ("tree_cluster", "controlled_cluster"),
        ("forest_canopy", "continuous_canopy"),
    ),
)
def test_profile_supports_required_vegetation_roles(
    semantic_role,
    representation_mode,
):
    profile = AtlasVegetationCompositionProfile(
        semantic_role=semantic_role,
        representation_mode=representation_mode,
    )

    assert profile.semantic_role == semantic_role
    assert profile.representation_mode == representation_mode


def test_profile_is_immutable():
    profile = AtlasVegetationCompositionProfile(
        semantic_role="isolated_tree",
        representation_mode="individual",
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        profile.semantic_role = "tree_cluster"


@pytest.mark.parametrize(
    ("semantic_role", "representation_mode"),
    (
        ("unknown", "individual"),
        ("isolated_tree", "ordered_row"),
        ("tree_row", "individual"),
        ("tree_cluster", "continuous_canopy"),
        ("forest_canopy", "controlled_cluster"),
    ),
)
def test_profile_rejects_invalid_role_mode_combinations(
    semantic_role,
    representation_mode,
):
    with pytest.raises(ValueError):
        AtlasVegetationCompositionProfile(
            semantic_role=semantic_role,
            representation_mode=representation_mode,
        )



from CORE.atlas_vegetation_composition_resolver import (
    AtlasVegetationCompositionResolver,
)


@pytest.mark.parametrize(
    ("source", "expected_role"),
    (
        ({"tree_type": "tree"}, "isolated_tree"),
        ({"tree_type": "tree_row"}, "tree_row"),
        ({"vegetation_role": "tree_cluster"}, "tree_cluster"),
        ({"surface_type": "forest"}, "forest_canopy"),
    ),
)
def test_resolver_maps_explicit_source_context_to_semantic_role(
    source,
    expected_role,
):
    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)
        == expected_role
    )


def test_resolver_returns_none_for_unsupported_source():
    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(
            {"surface_type": "grass"}
        )
        is None
    )


@pytest.mark.parametrize(
    ("source", "expected_role", "expected_mode"),
    (
        ({"tree_type": "tree"}, "isolated_tree", "individual"),
        ({"tree_type": "tree_row"}, "tree_row", "ordered_row"),
        ({"vegetation_role": "tree_cluster"}, "tree_cluster", "controlled_cluster"),
        ({"surface_type": "forest"}, "forest_canopy", "continuous_canopy"),
    ),
)
def test_resolve_profile_returns_role_and_representation(
    source,
    expected_role,
    expected_mode,
):
    profile = AtlasVegetationCompositionResolver.resolve_profile(source)

    assert profile.semantic_role == expected_role
    assert profile.representation_mode == expected_mode


def test_resolve_profile_returns_none_for_unsupported_source():
    assert (
        AtlasVegetationCompositionResolver.resolve_profile(
            {"surface_type": "grass"}
        )
        is None
    )


@pytest.mark.parametrize("source", (None, [], "tree", 42))
def test_resolver_rejects_non_mapping_source(source):
    with pytest.raises(TypeError, match="source must be a mapping"):
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)


def test_worldcover_tree_sample_resolves_as_forest_canopy():
    source = {
        "id": "worldcover_0",
        "tree_type": "tree",
        "tags": {
            "source": "worldcover",
            "class_id": 10,
            "resolution_m": 10,
        },
    }

    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)
        == "forest_canopy"
    )


def test_osm_tree_remains_isolated_tree():
    source = {
        "id": 123,
        "tree_type": "tree",
        "tags": {
            "source": "osm",
            "natural": "tree",
        },
    }

    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)
        == "isolated_tree"
    )


def test_resolve_collection_groups_sources_by_semantic_role():
    sources = (
        {
            "id": 10,
            "tree_type": "tree",
            "tags": {"source": "osm"},
        },
        {
            "id": "worldcover_0",
            "tree_type": "tree",
            "tags": {"source": "worldcover"},
        },
        {
            "id": "cluster_a",
            "vegetation_role": "tree_cluster",
        },
        {
            "id": "row_a",
            "tree_type": "tree_row",
        },
    )

    result = AtlasVegetationCompositionResolver.resolve_collection(sources)

    assert tuple(result) == (
        "isolated_tree",
        "tree_row",
        "tree_cluster",
        "forest_canopy",
    )
    assert tuple(item["id"] for item in result["isolated_tree"]) == (10,)
    assert tuple(item["id"] for item in result["tree_row"]) == ("row_a",)
    assert tuple(item["id"] for item in result["tree_cluster"]) == ("cluster_a",)
    assert tuple(item["id"] for item in result["forest_canopy"]) == (
        "worldcover_0",
    )


def test_resolve_collection_ignores_unsupported_sources():
    result = AtlasVegetationCompositionResolver.resolve_collection(
        (
            {"surface_type": "grass"},
            {"tree_type": "tree", "id": 20},
        )
    )

    assert tuple(item["id"] for item in result["isolated_tree"]) == (20,)
    assert result["tree_row"] == ()
    assert result["tree_cluster"] == ()
    assert result["forest_canopy"] == ()


def test_resolve_collection_order_is_deterministic():
    sources = (
        {"id": 20, "tree_type": "tree"},
        {"id": 10, "tree_type": "tree"},
        {"id": "b", "vegetation_role": "tree_cluster"},
        {"id": "a", "vegetation_role": "tree_cluster"},
    )

    first = AtlasVegetationCompositionResolver.resolve_collection(sources)
    second = AtlasVegetationCompositionResolver.resolve_collection(
        tuple(reversed(sources))
    )

    assert tuple(item["id"] for item in first["isolated_tree"]) == (10, 20)
    assert tuple(item["id"] for item in second["isolated_tree"]) == (10, 20)
    assert tuple(item["id"] for item in first["tree_cluster"]) == ("a", "b")
    assert tuple(item["id"] for item in second["tree_cluster"]) == ("a", "b")


def test_resolve_collection_does_not_mutate_sources():
    source = {
        "id": 10,
        "tree_type": "tree",
        "tags": {"source": "osm"},
    }
    before = {
        "id": 10,
        "tree_type": "tree",
        "tags": {"source": "osm"},
    }

    AtlasVegetationCompositionResolver.resolve_collection((source,))

    assert source == before


def test_resolve_forest_canopy_group_creates_single_composition_record():
    sources = (
        {
            "id": "worldcover_2",
            "lat": 50.0,
            "lon": 7.0,
            "tree_type": "tree",
            "tags": {"source": "worldcover"},
        },
        {
            "id": "worldcover_1",
            "lat": 50.1,
            "lon": 7.1,
            "tree_type": "tree",
            "tags": {"source": "worldcover"},
        },
    )

    result = AtlasVegetationCompositionResolver.resolve_forest_canopy_group(
        sources
    )

    assert result["semantic_role"] == "forest_canopy"
    assert result["representation_mode"] == "continuous_canopy"
    assert tuple(item["id"] for item in result["members"]) == (
        "worldcover_1",
        "worldcover_2",
    )


def test_resolve_forest_canopy_group_rejects_non_forest_members():
    with pytest.raises(
        ValueError,
        match="forest_canopy group requires forest_canopy members",
    ):
        AtlasVegetationCompositionResolver.resolve_forest_canopy_group(
            (
                {"id": 1, "tree_type": "tree"},
            )
        )


def test_resolve_forest_canopy_group_rejects_empty_group():
    with pytest.raises(
        ValueError,
        match="forest_canopy group must not be empty",
    ):
        AtlasVegetationCompositionResolver.resolve_forest_canopy_group(())


def test_resolve_tree_cluster_group_creates_single_composition_record():
    sources = (
        {
            "id": "cluster_b",
            "vegetation_role": "tree_cluster",
        },
        {
            "id": "cluster_a",
            "vegetation_role": "tree_cluster",
        },
    )

    result = AtlasVegetationCompositionResolver.resolve_tree_cluster_group(
        sources
    )

    assert result["semantic_role"] == "tree_cluster"
    assert result["representation_mode"] == "controlled_cluster"
    assert tuple(item["id"] for item in result["members"]) == (
        "cluster_a",
        "cluster_b",
    )


def test_resolve_tree_cluster_group_rejects_empty_group():
    with pytest.raises(
        ValueError,
        match="tree_cluster group must not be empty",
    ):
        AtlasVegetationCompositionResolver.resolve_tree_cluster_group(())


def test_resolve_tree_cluster_group_rejects_non_cluster_members():
    with pytest.raises(
        ValueError,
        match="tree_cluster group requires tree_cluster members",
    ):
        AtlasVegetationCompositionResolver.resolve_tree_cluster_group(
            (
                {"id": 1, "tree_type": "tree"},
            )
        )


def test_compose_collection_builds_semantic_outputs():
    sources = (
        {"id": 2, "tree_type": "tree"},
        {"id": 1, "tree_type": "tree"},
        {"id": "row_a", "tree_type": "tree_row"},
        {"id": "cluster_b", "vegetation_role": "tree_cluster"},
        {"id": "cluster_a", "vegetation_role": "tree_cluster"},
        {
            "id": "worldcover_2",
            "tree_type": "tree",
            "tags": {"source": "worldcover"},
        },
        {
            "id": "worldcover_1",
            "tree_type": "tree",
            "tags": {"source": "worldcover"},
        },
    )

    result = AtlasVegetationCompositionResolver.compose_collection(sources)

    assert tuple(item["id"] for item in result["isolated_trees"]) == (1, 2)
    assert tuple(item["id"] for item in result["tree_rows"]) == ("row_a",)

    assert len(result["tree_clusters"]) == 1
    assert result["tree_clusters"][0]["semantic_role"] == "tree_cluster"
    assert tuple(
        item["id"] for item in result["tree_clusters"][0]["members"]
    ) == ("cluster_a", "cluster_b")

    assert len(result["forest_canopies"]) == 1
    assert result["forest_canopies"][0]["semantic_role"] == "forest_canopy"
    assert tuple(
        item["id"] for item in result["forest_canopies"][0]["members"]
    ) == ("worldcover_1", "worldcover_2")


def test_compose_collection_ignores_unsupported_sources():
    result = AtlasVegetationCompositionResolver.compose_collection(
        (
            {"surface_type": "grass"},
            {"id": 1, "tree_type": "tree"},
        )
    )

    assert tuple(item["id"] for item in result["isolated_trees"]) == (1,)
    assert result["tree_rows"] == ()
    assert result["tree_clusters"] == ()
    assert result["forest_canopies"] == ()


def test_green_area_fill_tree_resolves_as_tree_cluster():
    source = {
        "id": "osm_green_area_fill_100_0",
        "tree_type": "tree",
        "tags": {
            "source": "osm_green_area_fill",
            "park_id": 100,
            "park_type": "leisure:park",
        },
    }

    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)
        == "tree_cluster"
    )


def test_real_osm_tree_still_resolves_as_isolated_tree():
    source = {
        "id": 1000,
        "tree_type": "tree",
        "tags": {
            "source": "osm",
            "natural": "tree",
        },
    }

    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)
        == "isolated_tree"
    )


def test_compose_collection_groups_green_area_fill_by_park_id():
    sources = (
        {
            "id": "fill_200_1",
            "tree_type": "tree",
            "tags": {
                "source": "osm_green_area_fill",
                "park_id": 200,
            },
        },
        {
            "id": "fill_100_2",
            "tree_type": "tree",
            "tags": {
                "source": "osm_green_area_fill",
                "park_id": 100,
            },
        },
        {
            "id": "fill_100_1",
            "tree_type": "tree",
            "tags": {
                "source": "osm_green_area_fill",
                "park_id": 100,
            },
        },
    )

    result = AtlasVegetationCompositionResolver.compose_collection(sources)

    assert len(result["tree_clusters"]) == 2

    assert tuple(
        item["id"]
        for item in result["tree_clusters"][0]["members"]
    ) == (
        "fill_100_1",
        "fill_100_2",
    )

    assert tuple(
        item["id"]
        for item in result["tree_clusters"][1]["members"]
    ) == (
        "fill_200_1",
    )


def test_compose_collection_splits_disconnected_worldcover_canopies():
    sources = (
        {
            "id": "wc_a1",
            "lat": 50.00000,
            "lon": 7.00000,
            "tree_type": "tree",
            "tags": {
                "source": "worldcover",
                "resolution_m": 10,
            },
        },
        {
            "id": "wc_a2",
            "lat": 50.00008,
            "lon": 7.00000,
            "tree_type": "tree",
            "tags": {
                "source": "worldcover",
                "resolution_m": 10,
            },
        },
        {
            "id": "wc_b1",
            "lat": 50.01000,
            "lon": 7.01000,
            "tree_type": "tree",
            "tags": {
                "source": "worldcover",
                "resolution_m": 10,
            },
        },
    )

    result = AtlasVegetationCompositionResolver.compose_collection(sources)

    assert len(result["forest_canopies"]) == 2

    member_groups = tuple(
        tuple(item["id"] for item in canopy["members"])
        for canopy in result["forest_canopies"]
    )

    assert member_groups == (
        ("wc_a1", "wc_a2"),
        ("wc_b1",),
    )


def test_raw_worldcover_forest_record_resolves_as_forest_canopy():
    source = {
        "lat": 50.0,
        "lon": 7.0,
        "class_id": 10,
        "source": "worldcover",
        "resolution_m": 10,
    }

    assert (
        AtlasVegetationCompositionResolver.resolve_semantic_role(source)
        == "forest_canopy"
    )


def test_raw_worldcover_resolution_controls_canopy_connectivity():
    sources = (
        {
            "id": "wc_30m_a",
            "lat": 50.00000,
            "lon": 7.00000,
            "class_id": 10,
            "source": "worldcover",
            "resolution_m": 30,
        },
        {
            "id": "wc_30m_b",
            "lat": 50.00020,
            "lon": 7.00000,
            "class_id": 10,
            "source": "worldcover",
            "resolution_m": 30,
        },
    )

    result = AtlasVegetationCompositionResolver.compose_collection(sources)

    assert len(result["forest_canopies"]) == 1
    assert tuple(
        item["id"] for item in result["forest_canopies"][0]["members"]
    ) == (
        "wc_30m_a",
        "wc_30m_b",
    )


def test_compose_nature_data_avoids_worldcover_double_representation():
    nature_data = {
        "trees": [
            {
                "id": 100,
                "tree_type": "tree",
                "tags": {"source": "osm"},
            },
            {
                "id": "worldcover_0",
                "lat": 50.0,
                "lon": 7.0,
                "tree_type": "tree",
                "tags": {
                    "source": "worldcover",
                    "class_id": 10,
                    "resolution_m": 10,
                },
            },
        ],
        "tree_rows": [
            {
                "id": "row_1",
                "tree_type": "tree_row",
            },
        ],
        "forests": [
            {
                "id": "forest_cell_1",
                "lat": 50.0,
                "lon": 7.0,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ],
    }

    result = AtlasVegetationCompositionResolver.compose_nature_data(
        nature_data
    )

    assert tuple(
        item["id"] for item in result["isolated_trees"]
    ) == (100,)

    assert tuple(
        item["id"] for item in result["tree_rows"]
    ) == ("row_1",)

    assert len(result["forest_canopies"]) == 1
    assert tuple(
        item["id"]
        for item in result["forest_canopies"][0]["members"]
    ) == ("forest_cell_1",)


def test_resolve_forest_canopy_surfaces_reuses_worldcover_dissolve():
    canopy = {
        "semantic_role": "forest_canopy",
        "representation_mode": "continuous_canopy",
        "members": (
            {
                "id": "wc_1",
                "lat": 50.00000,
                "lon": 7.00000,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
            {
                "id": "wc_2",
                "lat": 50.00008,
                "lon": 7.00000,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ),
    }

    surfaces = (
        AtlasVegetationCompositionResolver
        .resolve_forest_canopy_surfaces(canopy)
    )

    assert len(surfaces) == 1
    assert surfaces[0]["surface_type"] == "forest"
    assert surfaces[0]["source"] == "worldcover"
    assert surfaces[0]["park_type"] == "worldcover:forest"
    assert surfaces[0]["cell_count"] == 2
    assert len(surfaces[0]["geometry"]) >= 3


def test_compose_nature_data_exposes_forest_canopy_surfaces():
    nature_data = {
        "trees": [],
        "tree_rows": [],
        "forests": [
            {
                "id": "wc_1",
                "lat": 50.00000,
                "lon": 7.00000,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
            {
                "id": "wc_2",
                "lat": 50.00008,
                "lon": 7.00000,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ],
    }

    result = AtlasVegetationCompositionResolver.compose_nature_data(
        nature_data
    )

    assert len(result["forest_canopies"]) == 1
    assert len(result["forest_canopy_surfaces"]) == 1
    assert result["forest_canopy_surfaces"][0]["surface_type"] == "forest"
    assert result["forest_canopy_surfaces"][0]["cell_count"] == 2


from CORE.atlas_terrain_following_landcover_builder import (
    AtlasTerrainFollowingLandcoverBuilder,
)


def test_forest_canopy_surfaces_are_landcover_builder_compatible():
    nature_data = {
        "trees": [],
        "tree_rows": [],
        "forests": [
            {
                "id": "wc_1",
                "lat": 50.00000,
                "lon": 7.00000,
                "class_id": 10,
                "source": "worldcover",
                "resolution_m": 10,
            },
        ],
    }

    result = AtlasVegetationCompositionResolver.compose_nature_data(
        nature_data
    )

    terrain_mesh = {
        "top_points": (
            ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0)),
            ((0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        )
    }

    meshes = AtlasTerrainFollowingLandcoverBuilder.build(
        surfaces=result["forest_canopy_surfaces"],
        terrain_mesh=terrain_mesh,
        height_mm=0.2,
    )

    assert isinstance(meshes, list)


from CORE.atlas_park_foundation_builder import (
    AtlasParkFoundationBuilder,
)


class _IdentityCoordinateEngine:
    @staticmethod
    def geometry_to_stl_mm(geometry):
        return geometry


def test_forest_canopy_surface_can_use_closed_foundation_geometry():
    surface = {
        "id": "forest_surface_1",
        "surface_type": "forest",
        "park_type": "worldcover:forest",
        "geometry": [
            (1.0, 1.0),
            (4.0, 1.0),
            (4.0, 4.0),
            (1.0, 4.0),
        ],
    }

    terrain_mesh = {
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
        "top_points": (
            ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0)),
            ((0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        ),
    }

    mesh = AtlasParkFoundationBuilder._build_park_mesh(
        park=surface,
        coordinate_engine=_IdentityCoordinateEngine(),
        terrain_mesh=terrain_mesh,
    )

    assert mesh is not None
    assert mesh["bottom"]
    assert mesh["top"]
    assert mesh["walls"]
    assert mesh["triangles"]


from CORE.atlas_forest_canopy_foundation_builder import (
    AtlasForestCanopyFoundationBuilder,
)


def test_forest_canopy_builder_preserves_canopy_semantics():
    surface = {
        "id": "forest_surface_1",
        "surface_type": "forest",
        "source": "worldcover",
        "cell_count": 4,
        "geometry": [
            (1.0, 1.0),
            (4.0, 1.0),
            (4.0, 4.0),
            (1.0, 4.0),
        ],
    }

    terrain_mesh = {
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
        "top_points": (
            ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0)),
            ((0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        ),
    }

    meshes = AtlasForestCanopyFoundationBuilder.build(
        surfaces=(surface,),
        coordinate_engine=_IdentityCoordinateEngine(),
        terrain_mesh=terrain_mesh,
        debug=False,
    )

    assert len(meshes) == 1

    mesh = meshes[0]

    assert mesh["type"] == "forest_canopy_foundation"
    assert mesh["semantic_role"] == "forest_canopy"
    assert mesh["surface_id"] == "forest_surface_1"
    assert mesh["source"] == "worldcover"
    assert mesh["cell_count"] == 4
    assert mesh["bottom"]
    assert mesh["top"]
    assert mesh["walls"]
    assert mesh["triangles"]


from CORE.atlas_mesh_validator import AtlasMeshValidator


def test_forest_canopy_foundation_is_closed_and_manifold():
    surface = {
        "id": "forest_surface_topology",
        "surface_type": "forest",
        "source": "worldcover",
        "cell_count": 4,
        "geometry": [
            (1.0, 1.0),
            (4.0, 1.0),
            (4.0, 4.0),
            (1.0, 4.0),
        ],
    }

    terrain_mesh = {
        "metadata": {
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
        "top_points": (
            ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0)),
            ((0.0, 10.0, 0.0), (10.0, 10.0, 0.0)),
        ),
    }

    meshes = AtlasForestCanopyFoundationBuilder.build(
        surfaces=(surface,),
        coordinate_engine=_IdentityCoordinateEngine(),
        terrain_mesh=terrain_mesh,
        debug=False,
    )

    assert len(meshes) == 1

    report = AtlasMeshValidator._topology_report(
        meshes[0]
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
