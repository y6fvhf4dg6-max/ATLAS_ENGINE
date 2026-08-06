from copy import deepcopy

import pytest

from CORE.atlas_lod_level_catalog import (
    LOD_1,
    LOD_2,
    LOD_3,
)
from CORE.atlas_lod_mesh_filter import (
    AtlasLoDMeshFilter,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _triangle(offset):
    return (
        (float(offset), 0.0, 0.0),
        (float(offset) + 1.0, 0.0, 0.0),
        (float(offset), 1.0, 0.0),
    )


def _mesh(mesh_type, offset):
    return {
        "type": mesh_type,
        "triangles": [
            _triangle(offset),
        ],
    }


def _church_model():
    return AtlasSemanticArchitectureModel(
        landmark_family="church",
        grammar_name="single_west_tower",
        components=(
            AtlasSemanticArchitectureComponent(
                landmark_family="church",
                role="nave",
                geometry_kind="polygon_extrusion",
            ),
            AtlasSemanticArchitectureComponent(
                landmark_family="church",
                role="roof_section",
                geometry_kind="roof_volume",
                parent_role="nave",
            ),
            AtlasSemanticArchitectureComponent(
                landmark_family="church",
                role="tower",
                geometry_kind="tower_volume",
                parent_role="nave",
            ),
            AtlasSemanticArchitectureComponent(
                landmark_family="church",
                role="apse",
                geometry_kind="radial_extrusion",
                parent_role="nave",
            ),
            AtlasSemanticArchitectureComponent(
                landmark_family="church",
                role="window_bay_system",
                geometry_kind="surface_detail_system",
                parent_role="nave",
            ),
            AtlasSemanticArchitectureComponent(
                landmark_family="church",
                role="buttress_system",
                geometry_kind="linear_detail_system",
                parent_role="nave",
            ),
        ),
    )


def _church_mesh():
    groups = {
        "outer_aisle_meshes": [
            _mesh("outer_aisle", 0),
        ],
        "main_nave_body_meshes": [
            _mesh("main_nave", 10),
        ],
        "transept_meshes": [],
        "apse_meshes": [
            _mesh("apse", 20),
        ],
        "tower_meshes": [
            _mesh("tower", 30),
        ],
        "tower_window_meshes": [
            _mesh("tower_window", 40),
        ],
        "roof_meshes": [
            _mesh("roof", 50),
        ],
        "facade_meshes": [
            _mesh("facade", 60),
        ],
    }

    triangles = [
        triangle
        for meshes in groups.values()
        for mesh in meshes
        for triangle in mesh["triangles"]
    ]

    return {
        "type": "church_landmark",
        "landmark_id": 1901,
        **groups,
        "triangles": triangles,
        "semantic_architecture": _church_model(),
    }


def test_lod_1_keeps_primary_body_and_roof_groups():
    result = AtlasLoDMeshFilter.filter(
        mesh=_church_mesh(),
        semantic_model=_church_model(),
        level=LOD_1,
    )

    assert result["outer_aisle_meshes"]
    assert result["main_nave_body_meshes"]
    assert result["roof_meshes"]

    assert result["apse_meshes"] == []
    assert result["tower_meshes"] == []
    assert result["tower_window_meshes"] == []
    assert result["facade_meshes"] == []


def test_lod_2_keeps_major_components_but_removes_facade_detail():
    result = AtlasLoDMeshFilter.filter(
        mesh=_church_mesh(),
        semantic_model=_church_model(),
        level=LOD_2,
    )

    assert result["outer_aisle_meshes"]
    assert result["main_nave_body_meshes"]
    assert result["roof_meshes"]
    assert result["apse_meshes"]
    assert result["tower_meshes"]

    assert result["tower_window_meshes"] == []
    assert result["facade_meshes"] == []


def test_lod_3_keeps_structural_and_opening_groups():
    result = AtlasLoDMeshFilter.filter(
        mesh=_church_mesh(),
        semantic_model=_church_model(),
        level=LOD_3,
    )

    assert result["tower_window_meshes"]
    assert result["facade_meshes"]


def test_filter_rebuilds_top_level_triangles_from_visible_groups():
    result = AtlasLoDMeshFilter.filter(
        mesh=_church_mesh(),
        semantic_model=_church_model(),
        level=LOD_1,
    )

    expected = [
        triangle
        for key in (
            "outer_aisle_meshes",
            "main_nave_body_meshes",
            "roof_meshes",
        )
        for mesh in result[key]
        for triangle in mesh["triangles"]
    ]

    assert result["triangles"] == expected


def test_filter_preserves_non_group_metadata():
    result = AtlasLoDMeshFilter.filter(
        mesh=_church_mesh(),
        semantic_model=_church_model(),
        level=LOD_1,
    )

    assert result["type"] == "church_landmark"
    assert result["landmark_id"] == 1901
    assert result["semantic_architecture"] is not None


def test_filter_does_not_mutate_source_mesh():
    source = _church_mesh()
    snapshot = deepcopy(source)

    AtlasLoDMeshFilter.filter(
        mesh=source,
        semantic_model=_church_model(),
        level=LOD_1,
    )

    assert source == snapshot


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("mesh", None),
        ("mesh", []),
        ("semantic_model", object()),
        ("level", object()),
    ),
)
def test_filter_rejects_invalid_contract(
    field,
    value,
):
    arguments = {
        "mesh": _church_mesh(),
        "semantic_model": _church_model(),
        "level": LOD_2,
    }
    arguments[field] = value

    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field,
    ):
        AtlasLoDMeshFilter.filter(
            **arguments
        )
