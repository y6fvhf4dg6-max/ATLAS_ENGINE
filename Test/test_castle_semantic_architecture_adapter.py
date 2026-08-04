from __future__ import annotations

import pytest

from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)
from CORE.atlas_castle_semantic_architecture_adapter import (
    AtlasCastleSemanticArchitectureAdapter,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _closed_geometry():
    return [
        (48.0000, 12.0000),
        (48.0000, 12.0010),
        (48.0010, 12.0010),
        (48.0010, 12.0000),
        (48.0000, 12.0000),
    ]


def test_adapter_builds_shell_castle_semantic_model():
    classification = AtlasCastleGeometryClassifier.classify(
        castles=[
            {
                "id": 1701,
                "geometry_type": "relation",
                "outer_geometries": [
                    _closed_geometry(),
                ],
                "tags": {
                    "historic": "castle",
                },
            },
        ],
        castle_walls=[],
        debug=False,
    )

    model = AtlasCastleSemanticArchitectureAdapter.adapt(
        classification
    )

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == "castle"
    assert model.grammar_name == "shell_complex"

    assert tuple(
        component.role
        for component in model.components
    ) == (
        "shell",
    )


def test_adapter_maps_shell_geometry():
    classification = AtlasCastleGeometryClassifier.classify(
        castles=[
            {
                "id": 1702,
                "geometry_type": "relation",
                "outer_geometries": [
                    _closed_geometry(),
                ],
                "tags": {
                    "historic": "castle",
                },
            },
        ],
        castle_walls=[],
        debug=False,
    )

    model = AtlasCastleSemanticArchitectureAdapter.adapt(
        classification
    )

    shell = model.components_for_role("shell")[0]

    assert shell.geometry_kind == "courtyard_shell"
    assert shell.parent_role is None
    assert shell.instance_index == 0


def test_adapter_builds_perimeter_wall_model():
    classification = AtlasCastleGeometryClassifier.classify(
        castles=[
            {
                "id": 1703,
                "geometry_type": "way",
                "geometry": _closed_geometry(),
                "tags": {
                    "historic": "castle",
                },
            },
        ],
        castle_walls=[],
        debug=False,
    )

    model = AtlasCastleSemanticArchitectureAdapter.adapt(
        classification
    )

    assert model.grammar_name == (
        "perimeter_fortification"
    )

    walls = model.components_for_role(
        "perimeter_wall"
    )

    assert len(walls) == 1
    assert walls[0].geometry_kind == (
        "fortification_wall"
    )
    assert walls[0].instance_index == 0
    assert walls[0].flags == (
        "inferred",
    )


def test_adapter_preserves_relation_wall_role():
    classification = AtlasCastleGeometryClassifier.classify(
        castles=[
            {
                "id": 1704,
                "geometry_type": "relation",
                "outer_geometries": [
                    _closed_geometry(),
                ],
                "tags": {
                    "historic": "castle",
                },
            },
        ],
        castle_walls=[
            {
                "id": 2701,
                "source_relation_id": 1704,
                "geometry_type": "way",
                "geometry": _closed_geometry(),
                "tags": {
                    "barrier": "city_wall",
                },
            },
        ],
        debug=False,
    )

    model = AtlasCastleSemanticArchitectureAdapter.adapt(
        classification
    )

    relation_walls = model.components_for_role(
        "relation_wall"
    )

    assert len(relation_walls) == 1
    assert relation_walls[0].geometry_kind == (
        "fortification_wall"
    )
    assert relation_walls[0].parent_role == "shell"


def test_adapter_resolves_mixed_castle_complex_grammar():
    classification = AtlasCastleGeometryClassifier.classify(
        castles=[
            {
                "id": 1705,
                "geometry_type": "relation",
                "outer_geometries": [
                    _closed_geometry(),
                ],
                "tags": {
                    "historic": "castle",
                },
            },
        ],
        castle_walls=[
            {
                "id": 2702,
                "geometry_type": "way",
                "geometry": _closed_geometry(),
                "tags": {
                    "barrier": "city_wall",
                },
            },
        ],
        debug=False,
    )

    model = AtlasCastleSemanticArchitectureAdapter.adapt(
        classification
    )

    assert model.grammar_name == (
        "mixed_castle_complex"
    )
    assert tuple(
        component.role
        for component in model.components
    ) == (
        "shell",
        "perimeter_wall",
    )


def test_adapter_rejects_invalid_classification():
    with pytest.raises(
        TypeError,
        match="classification",
    ):
        AtlasCastleSemanticArchitectureAdapter.adapt(
            object()
        )
