import pytest
from dataclasses import FrozenInstanceError

from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _component(
    role,
    *,
    parent_role=None,
    instance_index=0,
):
    return AtlasSemanticArchitectureComponent(
        landmark_family="church",
        role=role,
        geometry_kind="polygon_extrusion",
        parent_role=parent_role,
        instance_index=instance_index,
    )


def test_semantic_architecture_model_is_immutable():
    model = AtlasSemanticArchitectureModel(
        landmark_family="church",
        grammar_name="single_west_tower",
        components=(
            _component("body"),
        ),
    )

    with pytest.raises(FrozenInstanceError):
        model.grammar_name = "changed"


def test_semantic_architecture_model_normalizes_identity_fields():
    model = AtlasSemanticArchitectureModel(
        landmark_family=" Church ",
        grammar_name=" Single West Tower ",
        components=(
            _component("body"),
            _component(
                "tower",
                parent_role="body",
            ),
        ),
        flags=(
            " Printable ",
            "CATALOG_RESOLVED",
        ),
    )

    assert model.landmark_family == "church"
    assert model.grammar_name == "single_west_tower"
    assert model.flags == (
        "printable",
        "catalog_resolved",
    )
    assert tuple(
        component.role
        for component in model.components
    ) == (
        "body",
        "tower",
    )


def test_semantic_architecture_model_requires_components():
    with pytest.raises(
        ValueError,
        match="components",
    ):
        AtlasSemanticArchitectureModel(
            landmark_family="bridge",
            grammar_name="galata",
            components=(),
        )


def test_semantic_architecture_model_rejects_foreign_component_family():
    with pytest.raises(
        ValueError,
        match="landmark_family",
    ):
        AtlasSemanticArchitectureModel(
            landmark_family="church",
            grammar_name="auto",
            components=(
                AtlasSemanticArchitectureComponent(
                    landmark_family="mosque",
                    role="dome",
                    geometry_kind="radial_surface",
                ),
            ),
        )


def test_semantic_architecture_model_rejects_duplicate_component_identity():
    with pytest.raises(
        ValueError,
        match="duplicate",
    ):
        AtlasSemanticArchitectureModel(
            landmark_family="church",
            grammar_name="auto",
            components=(
                _component("tower"),
                _component("tower"),
            ),
        )


def test_semantic_architecture_model_allows_repeated_roles_with_unique_indexes():
    model = AtlasSemanticArchitectureModel(
        landmark_family="church",
        grammar_name="twin_west_towers",
        components=(
            _component(
                "tower",
                instance_index=0,
            ),
            _component(
                "tower",
                instance_index=1,
            ),
        ),
    )

    assert len(model.components) == 2


def test_semantic_architecture_model_resolves_components_by_role():
    model = AtlasSemanticArchitectureModel(
        landmark_family="church",
        grammar_name="twin_west_towers",
        components=(
            _component("body"),
            _component(
                "tower",
                parent_role="body",
                instance_index=0,
            ),
            _component(
                "tower",
                parent_role="body",
                instance_index=1,
            ),
        ),
    )

    towers = model.components_for_role(" Tower ")

    assert tuple(
        component.instance_index
        for component in towers
    ) == (
        0,
        1,
    )

def test_semantic_architecture_model_normalizes_profile_name():
    model = AtlasSemanticArchitectureModel(
        landmark_family="church",
        grammar_name="single_west_tower",
        profile_name=" Romanesque Basilica ",
        components=(
            _component("body"),
        ),
    )

    assert model.profile_name == "romanesque_basilica"

