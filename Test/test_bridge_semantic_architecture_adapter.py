from __future__ import annotations

import pytest

from CORE.atlas_bridge_builder import (
    AtlasBridgeBuilder,
)
from CORE.atlas_bridge_semantic_architecture_adapter import (
    AtlasBridgeSemanticArchitectureAdapter,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _geometry(
    *,
    landmark_id=1401,
    tags=None,
):
    landmark = AtlasLandmark(
        id=landmark_id,
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, 0.0),
            (30.0, 0.0),
        ),
        tags=tags or {
            "bridge": "yes",
        },
        source="OSM",
    )

    return AtlasBridgeBuilder.build(
        landmark
    )


def test_adapter_builds_flat_deck_semantic_model():
    model = AtlasBridgeSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == "bridge"
    assert model.grammar_name == "flat_deck"

    assert tuple(
        component.role
        for component in model.components
    ) == (
        "deck",
    )


def test_adapter_maps_deck_geometry():
    model = AtlasBridgeSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    deck = model.components_for_role("deck")[0]

    assert deck.geometry_kind == "deck_volume"
    assert deck.parent_role is None
    assert deck.instance_index == 0


def test_adapter_creates_indexed_pier_components():
    model = AtlasBridgeSemanticArchitectureAdapter.adapt(
        _geometry(
            tags={
                "bridge": "yes",
                "bridge:pier_count": "3",
            },
        )
    )

    piers = model.components_for_role("pier")

    assert tuple(
        component.instance_index
        for component in piers
    ) == (
        0,
        1,
        2,
    )
    assert all(
        component.geometry_kind == "support_prism"
        for component in piers
    )
    assert all(
        component.parent_role == "deck"
        for component in piers
    )


def test_adapter_carries_bridge_profile_flags():
    geometry = _geometry()

    geometry.metadata[
        "bridge_approach_profile"
    ] = True
    geometry.metadata[
        "bridge_segmented_deck"
    ] = True

    model = AtlasBridgeSemanticArchitectureAdapter.adapt(
        geometry
    )

    assert model.flags == (
        "approach_profile",
        "segmented_deck",
    )


def test_adapter_resolves_full_span_convex_grammar():
    model = AtlasBridgeSemanticArchitectureAdapter.adapt(
        _geometry(
            landmark_id=280961352,
            tags={
                "man_made": "bridge",
                "name": "Galata Köprüsü",
                "wikidata": "Q81523",
            },
        )
    )

    assert model.grammar_name == (
        "full_span_convex"
    )
    assert model.flags == (
        "full_span_convex",
    )


def test_adapter_rejects_non_bridge_geometry():
    with pytest.raises(
        TypeError,
        match="AtlasBridgeGeometry",
    ):
        AtlasBridgeSemanticArchitectureAdapter.adapt(
            object()
        )
