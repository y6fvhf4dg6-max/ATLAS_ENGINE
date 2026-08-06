from copy import deepcopy

from CORE.atlas_landmark_mesh_builder import (
    AtlasLandmarkMeshBuilder,
)
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
from Test.test_bonn_church_landmark_real_fixture import (
    _build_real_church_meshes,
)


def _build_real_bonner_muenster():
    meshes = _build_real_church_meshes()
    landmark, production_mesh = meshes[
        "Bonner Münster"
    ]

    semantic_mesh = (
        AtlasLandmarkMeshBuilder.build(
            landmark,
            terrain_mesh=None,
            include_semantic_architecture=True,
        )
    )

    return (
        landmark,
        production_mesh,
        semantic_mesh,
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


def _mapped_triangle_count(mesh):
    return sum(
        len(component_mesh["triangles"])
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
        for component_mesh in mesh[key]
    )


def test_real_bonner_muenster_exposes_semantic_architecture():
    landmark, _, mesh = (
        _build_real_bonner_muenster()
    )

    assert landmark.tags["wikidata"] == "Q686664"
    assert mesh["type"] == "church_landmark"

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
    assert len(
        semantic_model.components_for_role(
            "tower"
        )
    ) == 4


def test_real_bonner_muenster_lod_1_keeps_primary_form():
    _, _, mesh = (
        _build_real_bonner_muenster()
    )

    filtered = _filter(
        mesh,
        LOD_1,
    )

    assert filtered["outer_aisle_meshes"]
    assert filtered["main_nave_body_meshes"]
    assert filtered["roof_meshes"]

    assert filtered["tower_meshes"] == []
    assert filtered["tower_window_meshes"] == []
    assert filtered["facade_meshes"] == []

    assert len(filtered["triangles"]) == (
        _mapped_triangle_count(filtered)
    )


def test_real_bonner_muenster_lod_2_restores_catalog_towers():
    _, _, mesh = (
        _build_real_bonner_muenster()
    )

    filtered = _filter(
        mesh,
        LOD_2,
    )

    assert tuple(
        tower["tower_type"]
        for tower in filtered["tower_meshes"]
    ) == (
        "crossing_tower",
        "outer_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )

    assert filtered["tower_window_meshes"] == []
    assert filtered["facade_meshes"] == []

    assert len(filtered["triangles"]) == (
        _mapped_triangle_count(filtered)
    )


def test_real_bonner_muenster_lod_3_restores_facade_detail():
    _, _, mesh = (
        _build_real_bonner_muenster()
    )

    filtered = _filter(
        mesh,
        LOD_3,
    )

    assert filtered["tower_meshes"]
    assert filtered["tower_window_meshes"]
    assert filtered["facade_meshes"]

    assert len(filtered["triangles"]) == (
        _mapped_triangle_count(filtered)
    )


def test_real_bonner_muenster_detail_increases_with_lod():
    _, _, source = (
        _build_real_bonner_muenster()
    )

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


def test_real_bonner_muenster_lod_is_opt_in_and_non_mutating():
    _, production_mesh, source = (
        _build_real_bonner_muenster()
    )
    snapshot = deepcopy(source)

    filtered = _filter(
        source,
        LOD_1,
    )

    assert source == snapshot
    assert "lod_level" not in source
    assert "semantic_architecture" not in (
        production_mesh
    )
    assert filtered["lod_level"] is LOD_1
    assert len(filtered["triangles"]) < len(
        source["triangles"]
    )
