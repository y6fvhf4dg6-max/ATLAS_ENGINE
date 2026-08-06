from copy import deepcopy

from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import (
    AtlasLandmarkMeshBuilder,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_lod_level_catalog import (
    LOD_1,
    LOD_2,
    LOD_3,
)
from CORE.atlas_lod_mesh_filter import (
    AtlasLoDMeshFilter,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _synthetic_church():
    return AtlasLandmark(
        id=2601,
        source="synthetic",
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (24.0, 0.0),
            (24.0, 42.0),
            (0.0, 42.0),
        ),
        tags={
            "building": "church",
            "height": "26",
            "atlas:church_grammar": (
                "single_west_tower"
            ),
        },
    )


def _build():
    return AtlasLandmarkMeshBuilder.build(
        _synthetic_church(),
        include_semantic_architecture=True,
    )


def _filter(mesh, level):
    semantic_model = mesh[
        "semantic_architecture"
    ]

    return AtlasLoDMeshFilter.filter(
        mesh=mesh,
        semantic_model=semantic_model,
        level=level,
    )


def _group_triangle_count(mesh, key):
    return sum(
        len(component_mesh["triangles"])
        for component_mesh in mesh[key]
    )


def _mapped_triangle_count(mesh):
    return sum(
        _group_triangle_count(
            mesh,
            key,
        )
        for key in (
            "outer_aisle_meshes",
            "main_nave_body_meshes",
            "transept_meshes",
            "apse_meshes",
            "tower_meshes",
            "tower_window_meshes",
            "roof_meshes",
            "facade_meshes",
        )
    )


def test_synthetic_church_build_exposes_semantic_mesh_contract():
    mesh = _build()

    assert mesh["type"] == "church_landmark"
    assert mesh["landmark_id"] == 2601
    assert mesh["triangles"]

    semantic_model = mesh[
        "semantic_architecture"
    ]

    assert isinstance(
        semantic_model,
        AtlasSemanticArchitectureModel,
    )
    assert semantic_model.landmark_family == "church"

    assert semantic_model.components_for_role(
        "nave"
    )
    assert semantic_model.components_for_role(
        "roof_section"
    )
    assert semantic_model.components_for_role(
        "tower"
    )
    assert semantic_model.components_for_role(
        "apse"
    )


def test_synthetic_church_lod_1_keeps_primary_form_only():
    mesh = _filter(
        _build(),
        LOD_1,
    )

    assert mesh["outer_aisle_meshes"]
    assert mesh["main_nave_body_meshes"]
    assert mesh["roof_meshes"]

    assert mesh["apse_meshes"] == []
    assert mesh["tower_meshes"] == []
    assert mesh["tower_window_meshes"] == []
    assert mesh["facade_meshes"] == []

    assert mesh["triangles"]
    assert len(mesh["triangles"]) == (
        _mapped_triangle_count(mesh)
    )


def test_synthetic_church_lod_2_restores_major_components():
    mesh = _filter(
        _build(),
        LOD_2,
    )

    assert mesh["outer_aisle_meshes"]
    assert mesh["main_nave_body_meshes"]
    assert mesh["roof_meshes"]
    assert mesh["apse_meshes"]
    assert mesh["tower_meshes"]

    assert mesh["tower_window_meshes"] == []
    assert mesh["facade_meshes"] == []

    assert len(mesh["triangles"]) == (
        _mapped_triangle_count(mesh)
    )


def test_synthetic_church_lod_3_restores_facade_detail():
    mesh = _filter(
        _build(),
        LOD_3,
    )

    assert mesh["tower_window_meshes"]
    assert mesh["facade_meshes"]

    assert len(mesh["triangles"]) == (
        _mapped_triangle_count(mesh)
    )


def test_synthetic_church_triangle_count_increases_with_lod():
    source = _build()

    lod_1 = _filter(
        source,
        LOD_1,
    )
    lod_2 = _filter(
        source,
        LOD_2,
    )
    lod_3 = _filter(
        source,
        LOD_3,
    )

    assert (
        len(lod_1["triangles"])
        < len(lod_2["triangles"])
        < len(lod_3["triangles"])
    )


def test_synthetic_church_filter_is_opt_in_and_non_mutating():
    source = _build()
    snapshot = deepcopy(source)

    filtered = _filter(
        source,
        LOD_1,
    )

    assert source == snapshot
    assert len(filtered["triangles"]) < len(
        source["triangles"]
    )
    assert "lod_level" not in source
    assert filtered["lod_level"] is LOD_1
