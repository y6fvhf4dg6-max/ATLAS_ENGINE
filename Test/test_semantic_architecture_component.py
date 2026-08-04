import pytest
from dataclasses import FrozenInstanceError

from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)


def test_semantic_architecture_component_is_immutable():
    component = AtlasSemanticArchitectureComponent(
        landmark_family="church",
        role="tower",
        geometry_kind="polygon_extrusion",
    )

    with pytest.raises(FrozenInstanceError):
        component.role = "roof"


def test_semantic_architecture_component_normalizes_identity_fields():
    component = AtlasSemanticArchitectureComponent(
        landmark_family=" Church ",
        role=" Crossing Tower ",
        geometry_kind=" Polygon Extrusion ",
        parent_role=" Nave ",
        instance_index=2,
        flags=(
            " Load Bearing ",
            "PRINTABLE",
        ),
    )

    assert component.landmark_family == "church"
    assert component.role == "crossing_tower"
    assert component.geometry_kind == "polygon_extrusion"
    assert component.parent_role == "nave"
    assert component.instance_index == 2
    assert component.flags == (
        "load_bearing",
        "printable",
    )


def test_semantic_architecture_component_allows_root_component():
    component = AtlasSemanticArchitectureComponent(
        landmark_family="bridge",
        role="deck",
        geometry_kind="footprint_extrusion",
    )

    assert component.parent_role is None
    assert component.instance_index == 0
    assert component.flags == ()


@pytest.mark.parametrize(
    ("field_name", "kwargs"),
    (
        (
            "landmark_family",
            {
                "landmark_family": " ",
                "role": "body",
                "geometry_kind": "footprint_extrusion",
            },
        ),
        (
            "role",
            {
                "landmark_family": "church",
                "role": "",
                "geometry_kind": "footprint_extrusion",
            },
        ),
        (
            "geometry_kind",
            {
                "landmark_family": "church",
                "role": "body",
                "geometry_kind": " ",
            },
        ),
    ),
)
def test_semantic_architecture_component_rejects_blank_identity_fields(
    field_name,
    kwargs,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        AtlasSemanticArchitectureComponent(
            **kwargs,
        )


@pytest.mark.parametrize(
    "instance_index",
    (
        True,
        -1,
        1.5,
        "1",
    ),
)
def test_semantic_architecture_component_rejects_invalid_instance_index(
    instance_index,
):
    with pytest.raises(
        ValueError,
        match="instance_index",
    ):
        AtlasSemanticArchitectureComponent(
            landmark_family="mosque",
            role="minaret",
            geometry_kind="radial_extrusion",
            instance_index=instance_index,
        )
