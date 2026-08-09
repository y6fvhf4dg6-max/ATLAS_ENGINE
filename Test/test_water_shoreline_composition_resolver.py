import pytest

from CORE.atlas_water_shoreline_composition_resolver import (
    AtlasWaterShorelineCompositionResolver,
)


@pytest.mark.parametrize(
    "tags,geometry_role,expected",
    [
        (
            {"waterway": "river"},
            None,
            "river",
        ),
        (
            {"waterway": "canal"},
            None,
            "canal",
        ),
        (
            {"natural": "water", "water": "lake"},
            None,
            "lake",
        ),
        (
            {"natural": "coastline"},
            "coastline",
            "coastline",
        ),
        (
            {"man_made": "embankment"},
            None,
            "embankment",
        ),
        (
            {"man_made": "quay"},
            None,
            "quay",
        ),
        (
            {"man_made": "pier"},
            None,
            "waterfront_pier",
        ),
        (
            {"leisure": "marina"},
            None,
            "marina",
        ),
    ],
)
def test_resolves_required_water_and_shoreline_semantics(
    tags,
    geometry_role,
    expected,
):
    assert (
        AtlasWaterShorelineCompositionResolver
        .resolve_semantic_class(
            tags=tags,
            geometry_role=geometry_role,
        )
        == expected
    )


def test_water_surface_profile_is_first_class_scene_layer():
    profile = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={
                "natural": "water",
                "water": "lake",
            }
        )
    )

    assert profile is not None
    assert profile.semantic_class == "lake"
    assert profile.composition_role == "water_surface"
    assert profile.first_class_scene_layer is True
    assert profile.lod_eligible is True
    assert profile.preserves_source_geometry is True


def test_shoreline_structure_profile_is_not_water_surface():
    profile = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={"man_made": "quay"}
        )
    )

    assert profile is not None
    assert profile.semantic_class == "quay"
    assert profile.composition_role == "shoreline_structure"
    assert profile.first_class_scene_layer is True
    assert profile.lod_eligible is True
    assert profile.preserves_source_geometry is True


def test_unknown_semantics_are_not_invented():
    assert (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={"amenity": "bench"}
        )
        is None
    )


def test_resolve_source_record_preserves_geometry_and_interaction_flags():
    source = {
        "id": 42,
        "geometry": (
            (50.0, 8.0),
            (50.0, 8.1),
            (50.1, 8.1),
        ),
        "tags": {
            "waterway": "river",
        },
    }

    record = (
        AtlasWaterShorelineCompositionResolver
        .resolve_source_record(
            source,
            bridge_interaction=True,
            road_interaction=True,
            rail_interaction=False,
        )
    )

    assert record is not None
    assert record["source_id"] == 42
    assert record["semantic_class"] == "river"
    assert record["composition_role"] == "water_surface"
    assert record["geometry"] == source["geometry"]
    assert record["preserves_source_geometry"] is True
    assert record["bridge_interaction"] is True
    assert record["road_interaction"] is True
    assert record["rail_interaction"] is False


def test_shoreline_structure_record_declares_shoreline_readability():
    source = {
        "id": 77,
        "geometry": (
            (50.0, 8.0),
            (50.1, 8.0),
        ),
        "tags": {
            "man_made": "quay",
        },
    }

    record = (
        AtlasWaterShorelineCompositionResolver
        .resolve_source_record(source)
    )

    assert record is not None
    assert record["semantic_class"] == "quay"
    assert record["composition_role"] == "shoreline_structure"
    assert record["supports_shoreline_readability"] is True
    assert record["supports_water_surface_continuity"] is False


def test_water_surface_record_declares_continuity_role():
    source = {
        "id": 88,
        "geometry": (
            (50.0, 8.0),
            (50.0, 8.1),
            (50.1, 8.1),
        ),
        "tags": {
            "natural": "water",
            "water": "lake",
        },
    }

    record = (
        AtlasWaterShorelineCompositionResolver
        .resolve_source_record(source)
    )

    assert record is not None
    assert record["supports_water_surface_continuity"] is True
    assert record["supports_shoreline_readability"] is True


def test_resolve_source_record_rejects_non_mapping_source():
    with pytest.raises(TypeError):
        (
            AtlasWaterShorelineCompositionResolver
            .resolve_source_record(
                ["not", "a", "mapping"]
            )
        )


def test_resolve_scene_records_combines_water_coastline_and_waterfront_sources():
    waters = [
        {
            "id": 1,
            "geometry": (
                (50.0, 8.0),
                (50.0, 8.1),
                (50.1, 8.1),
            ),
            "tags": {
                "waterway": "river",
            },
        },
        {
            "id": 2,
            "geometry": (
                (50.2, 8.0),
                (50.2, 8.1),
                (50.3, 8.1),
            ),
            "tags": {
                "natural": "water",
                "water": "lake",
            },
        },
    ]

    coastlines = [
        {
            "id": 3,
            "geometry": (
                (50.4, 8.0),
                (50.4, 8.1),
            ),
            "tags": {
                "natural": "coastline",
            },
        },
    ]

    waterfront_structures = [
        {
            "id": 4,
            "geometry": (
                (50.5, 8.0),
                (50.5, 8.1),
            ),
            "tags": {
                "man_made": "quay",
            },
            "waterfront_type": "quay",
        },
    ]

    records = (
        AtlasWaterShorelineCompositionResolver
        .resolve_scene_records(
            waters=waters,
            coastlines=coastlines,
            waterfront_structures=waterfront_structures,
        )
    )

    assert [
        record["semantic_class"]
        for record in records
    ] == [
        "river",
        "lake",
        "coastline",
        "quay",
    ]

    assert [
        record["source_id"]
        for record in records
    ] == [
        1,
        2,
        3,
        4,
    ]


def test_resolve_scene_records_preserves_source_geometry():
    source_geometry = (
        (50.0, 8.0),
        (50.0, 8.1),
        (50.1, 8.1),
    )

    records = (
        AtlasWaterShorelineCompositionResolver
        .resolve_scene_records(
            waters=[
                {
                    "id": 10,
                    "geometry": source_geometry,
                    "tags": {
                        "waterway": "canal",
                    },
                }
            ],
            coastlines=(),
            waterfront_structures=(),
        )
    )

    assert len(records) == 1
    assert records[0]["geometry"] == source_geometry
    assert records[0]["preserves_source_geometry"] is True


def test_resolve_scene_records_skips_unknown_records_without_invention():
    records = (
        AtlasWaterShorelineCompositionResolver
        .resolve_scene_records(
            waters=[
                {
                    "id": 20,
                    "geometry": (),
                    "tags": {
                        "amenity": "bench",
                    },
                }
            ],
            coastlines=(),
            waterfront_structures=(),
        )
    )

    assert records == ()


def test_resolves_bridge_road_and_rail_interactions_from_source_geometry():
    source = {
        "id": 100,
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.1000),
            (50.0000, 8.2000),
        ),
        "tags": {
            "waterway": "river",
        },
    }

    bridge = {
        "id": 200,
        "geometry": (
            (49.9500, 8.1000),
            (50.0500, 8.1000),
        ),
        "tags": {
            "bridge": "yes",
        },
    }

    road = {
        "id": 300,
        "geometry": (
            (49.9500, 8.1500),
            (50.0500, 8.1500),
        ),
        "tags": {
            "highway": "primary",
        },
    }

    railway = {
        "id": 400,
        "geometry": (
            (49.9500, 8.0500),
            (50.0500, 8.0500),
        ),
        "tags": {
            "railway": "rail",
        },
    }

    flags = (
        AtlasWaterShorelineCompositionResolver
        .resolve_interaction_flags(
            source=source,
            bridges=(bridge,),
            roads=(road,),
            railways=(railway,),
        )
    )

    assert flags == {
        "bridge_interaction": True,
        "road_interaction": True,
        "rail_interaction": True,
    }


def test_interaction_resolver_does_not_mark_unrelated_scene_geometry():
    source = {
        "id": 101,
        "geometry": (
            (50.0000, 8.0000),
            (50.0000, 8.1000),
            (50.0000, 8.2000),
        ),
        "tags": {
            "waterway": "canal",
        },
    }

    distant_road = {
        "id": 301,
        "geometry": (
            (51.0000, 9.0000),
            (51.1000, 9.1000),
        ),
        "tags": {
            "highway": "secondary",
        },
    }

    flags = (
        AtlasWaterShorelineCompositionResolver
        .resolve_interaction_flags(
            source=source,
            bridges=(),
            roads=(distant_road,),
            railways=(),
        )
    )

    assert flags == {
        "bridge_interaction": False,
        "road_interaction": False,
        "rail_interaction": False,
    }


def test_interaction_resolver_preserves_source_geometry():
    geometry = (
        (50.0000, 8.0000),
        (50.0000, 8.1000),
        (50.0000, 8.2000),
    )

    source = {
        "id": 102,
        "geometry": geometry,
        "tags": {
            "waterway": "river",
        },
    }

    (
        AtlasWaterShorelineCompositionResolver
        .resolve_interaction_flags(
            source=source,
            bridges=(),
            roads=(),
            railways=(),
        )
    )

    assert source["geometry"] == geometry


def test_scene_records_automatically_include_geometry_interaction_context():
    waters = [
        {
            "id": 1,
            "geometry": (
                (50.0000, 8.0000),
                (50.0000, 8.1000),
                (50.0000, 8.2000),
            ),
            "tags": {
                "waterway": "river",
            },
        },
    ]

    bridges = [
        {
            "id": 2,
            "geometry": (
                (49.9500, 8.1000),
                (50.0500, 8.1000),
            ),
            "tags": {
                "bridge": "yes",
            },
        },
    ]

    roads = [
        {
            "id": 3,
            "geometry": (
                (49.9500, 8.1500),
                (50.0500, 8.1500),
            ),
            "tags": {
                "highway": "primary",
            },
        },
    ]

    railways = [
        {
            "id": 4,
            "geometry": (
                (49.9500, 8.0500),
                (50.0500, 8.0500),
            ),
            "tags": {
                "railway": "rail",
            },
        },
    ]

    records = (
        AtlasWaterShorelineCompositionResolver
        .resolve_scene_records(
            waters=waters,
            coastlines=(),
            waterfront_structures=(),
            bridges=bridges,
            roads=roads,
            railways=railways,
        )
    )

    assert len(records) == 1

    record = records[0]

    assert record["bridge_interaction"] is True
    assert record["road_interaction"] is True
    assert record["rail_interaction"] is True


def test_scene_records_default_to_no_interaction_without_scene_context():
    records = (
        AtlasWaterShorelineCompositionResolver
        .resolve_scene_records(
            waters=[
                {
                    "id": 5,
                    "geometry": (
                        (50.0, 8.0),
                        (50.0, 8.1),
                        (50.1, 8.1),
                    ),
                    "tags": {
                        "natural": "water",
                        "water": "lake",
                    },
                },
            ],
            coastlines=(),
            waterfront_structures=(),
        )
    )

    assert len(records) == 1
    assert records[0]["bridge_interaction"] is False
    assert records[0]["road_interaction"] is False
    assert records[0]["rail_interaction"] is False


def test_water_surface_profile_declares_product_composition_policy():
    profile = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={
                "waterway": "river",
            }
        )
    )

    assert profile.physical_separation_role == "raised_water_solid"
    assert profile.product_scale_simplification == "source_preserving"
    assert profile.shoreline_treatment == "readable_boundary"
    assert profile.lod_eligible is True


def test_quay_profile_declares_shoreline_structure_policy():
    profile = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={
                "man_made": "quay",
            }
        )
    )

    assert profile.physical_separation_role == "shoreline_structure"
    assert profile.product_scale_simplification == "source_preserving"
    assert profile.shoreline_treatment == "structural_edge"
    assert profile.lod_eligible is True


def test_waterfront_pier_and_marina_remain_distinct_structure_semantics():
    pier = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={
                "man_made": "pier",
            }
        )
    )

    marina = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={
                "leisure": "marina",
            }
        )
    )

    assert pier.semantic_class == "waterfront_pier"
    assert marina.semantic_class == "marina"

    assert pier.shoreline_treatment == "structural_edge"
    assert marina.shoreline_treatment == "structural_edge"

    assert pier.product_scale_simplification == "source_preserving"
    assert marina.product_scale_simplification == "source_preserving"


def test_source_record_exposes_product_composition_policy():
    record = (
        AtlasWaterShorelineCompositionResolver
        .resolve_source_record(
            {
                "id": 900,
                "geometry": (
                    (50.0, 8.0),
                    (50.0, 8.1),
                    (50.1, 8.1),
                ),
                "tags": {
                    "natural": "water",
                    "water": "lake",
                },
            }
        )
    )

    assert record["physical_separation_role"] == "raised_water_solid"
    assert record["product_scale_simplification"] == "source_preserving"
    assert record["shoreline_treatment"] == "readable_boundary"


def test_resolves_island_as_required_waterfront_morphology_semantic():
    profile = (
        AtlasWaterShorelineCompositionResolver
        .resolve_profile(
            tags={
                "place": "island",
            }
        )
    )

    assert profile is not None
    assert profile.semantic_class == "island"
    assert profile.composition_role == "land_within_water"
    assert profile.first_class_scene_layer is True
    assert profile.lod_eligible is True
    assert profile.preserves_source_geometry is True


def test_scene_records_include_embankment_context():
    embankment = {
        "id": 700,
        "geometry": (
            (50.0, 8.0),
            (50.0, 8.1),
        ),
        "tags": {
            "man_made": "embankment",
        },
        "semantic_class": "embankment",
    }

    records = (
        AtlasWaterShorelineCompositionResolver
        .resolve_scene_records(
            waters=(),
            coastlines=(),
            waterfront_structures=(),
            embankments=(embankment,),
        )
    )

    assert len(records) == 1
    assert records[0]["semantic_class"] == "embankment"
    assert records[0]["composition_role"] == "shoreline_structure"
