import pytest

from CORE.atlas_lod_component_mesh_group_mapper import (
    AtlasLoDComponentMeshGroupMapper,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)


def _component(
    role,
    *,
    family="church",
):
    return AtlasSemanticArchitectureComponent(
        landmark_family=family,
        role=role,
        geometry_kind="polygon_extrusion",
    )


@pytest.mark.parametrize(
    (
        "role",
        "expected_group_keys",
    ),
    (
        (
            "nave",
            (
                "outer_aisle_meshes",
                "main_nave_body_meshes",
            ),
        ),
        (
            "transept",
            (
                "transept_meshes",
            ),
        ),
        (
            "apse",
            (
                "apse_meshes",
            ),
        ),
        (
            "tower",
            (
                "tower_meshes",
            ),
        ),
        (
            "buttress_system",
            (
                "facade_meshes",
            ),
        ),
        (
            "window_bay_system",
            (
                "facade_meshes",
                "tower_window_meshes",
            ),
        ),
        (
            "roof_section",
            (
                "roof_meshes",
            ),
        ),
    ),
)
def test_maps_church_semantic_roles_to_mesh_groups(
    role,
    expected_group_keys,
):
    assert (
        AtlasLoDComponentMeshGroupMapper
        .mesh_group_keys(
            _component(role)
        )
        == expected_group_keys
    )


@pytest.mark.parametrize(
    (
        "role",
        "expected_group_keys",
    ),
    (
        (
            "prayer_hall",
            (
                "prayer_hall_meshes",
            ),
        ),
        (
            "dome_drum",
            (
                "dome_drum_meshes",
            ),
        ),
        (
            "main_dome",
            (
                "dome_meshes",
            ),
        ),
        (
            "minaret_body",
            (
                "minaret_meshes",
            ),
        ),
        (
            "minaret_balcony",
            (
                "minaret_balcony_meshes",
            ),
        ),
        (
            "minaret_cap",
            (
                "minaret_cap_meshes",
            ),
        ),
    ),
)
def test_maps_mosque_semantic_roles_to_mesh_groups(
    role,
    expected_group_keys,
):
    assert (
        AtlasLoDComponentMeshGroupMapper
        .mesh_group_keys(
            _component(
                role,
                family="mosque",
            )
        )
        == expected_group_keys
    )


def test_mapping_is_family_specific():
    assert (
        AtlasLoDComponentMeshGroupMapper
        .mesh_group_keys(
            _component(
                "tower",
                family="church",
            )
        )
        == (
            "tower_meshes",
        )
    )

    assert (
        AtlasLoDComponentMeshGroupMapper
        .mesh_group_keys(
            _component(
                "tower",
                family="mosque",
            )
        )
        == ()
    )


def test_unknown_role_has_no_mesh_group_mapping():
    assert (
        AtlasLoDComponentMeshGroupMapper
        .mesh_group_keys(
            _component(
                "unknown_component",
            )
        )
        == ()
    )


@pytest.mark.parametrize(
    "component",
    (
        None,
        object(),
        {},
    ),
)
def test_mapper_rejects_invalid_component(
    component,
):
    with pytest.raises(
        TypeError,
        match="component",
    ):
        (
            AtlasLoDComponentMeshGroupMapper
            .mesh_group_keys(
                component
            )
        )


def test_mapper_exposes_supported_families():
    assert (
        AtlasLoDComponentMeshGroupMapper
        .supported_families()
        == (
            "church",
            "mosque",
        )
    )
