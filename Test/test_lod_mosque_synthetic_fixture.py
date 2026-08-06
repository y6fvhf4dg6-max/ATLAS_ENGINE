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


def _synthetic_mosque():
    return AtlasLandmark(
        id=2701,
        source="synthetic",
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=(
            (0.0, 0.0),
            (18.0, 0.0),
            (18.0, 28.0),
            (0.0, 28.0),
        ),
        tags={
            "building": "mosque",
            "religion": "muslim",
            "height": "24",
            "atlas:worship_grammar": (
                "single_dome_single_minaret"
            ),
        },
    )


def _build():
    return AtlasLandmarkMeshBuilder.build(
        _synthetic_mosque(),
        include_semantic_architecture=True,
    )


def _filter(mesh, level):
    return AtlasLoDMeshFilter.filter(
        mesh=mesh,
        semantic_model=mesh[
            "semantic_architecture"
        ],
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
            "prayer_hall_meshes",
            "dome_drum_meshes",
            "dome_meshes",
            "minaret_meshes",
            "minaret_balcony_meshes",
            "minaret_cap_meshes",
        )
    )


def test_synthetic_mosque_exposes_semantic_mesh_contract():
    mesh = _build()

    assert mesh["type"] == "mosque_landmark"
    assert mesh["landmark_id"] == 2701
    assert mesh["triangles"]

    semantic_model = mesh[
        "semantic_architecture"
    ]

    assert isinstance(
        semantic_model,
        AtlasSemanticArchitectureModel,
    )
    assert semantic_model.landmark_family == "mosque"
    assert semantic_model.grammar_name == (
        "single_dome_single_minaret"
    )

    assert semantic_model.components_for_role(
        "prayer_hall"
    )
    assert semantic_model.components_for_role(
        "dome_drum"
    )
    assert semantic_model.components_for_role(
        "main_dome"
    )
    assert semantic_model.components_for_role(
        "minaret_body"
    )
    assert semantic_model.components_for_role(
        "minaret_balcony"
    )
    assert semantic_model.components_for_role(
        "minaret_cap"
    )


def test_synthetic_mosque_lod_1_keeps_primary_mass_only():
    mesh = _filter(
        _build(),
        LOD_1,
    )

    assert mesh["prayer_hall_meshes"]

    assert mesh["dome_drum_meshes"] == []
    assert mesh["dome_meshes"] == []
    assert mesh["minaret_meshes"] == []
    assert mesh["minaret_balcony_meshes"] == []
    assert mesh["minaret_cap_meshes"] == []

    assert mesh["triangles"]
    assert len(mesh["triangles"]) == (
        _mapped_triangle_count(mesh)
    )


def test_synthetic_mosque_lod_2_restores_major_components():
    mesh = _filter(
        _build(),
        LOD_2,
    )

    assert mesh["prayer_hall_meshes"]
    assert mesh["dome_drum_meshes"]
    assert mesh["dome_meshes"]
    assert mesh["minaret_meshes"]
    assert mesh["minaret_balcony_meshes"]
    assert mesh["minaret_cap_meshes"]

    assert len(mesh["triangles"]) == (
        _mapped_triangle_count(mesh)
    )


def test_synthetic_mosque_lod_3_matches_lod_2_without_facade_groups():
    source = _build()

    lod_2 = _filter(
        source,
        LOD_2,
    )
    lod_3 = _filter(
        source,
        LOD_3,
    )

    assert lod_3["triangles"] == (
        lod_2["triangles"]
    )
    assert (
        lod_3["lod_visible_mesh_groups"]
        == lod_2["lod_visible_mesh_groups"]
    )


def test_synthetic_mosque_triangle_count_increases_from_lod_1_to_2():
    source = _build()

    lod_1 = _filter(
        source,
        LOD_1,
    )
    lod_2 = _filter(
        source,
        LOD_2,
    )

    assert len(
        lod_1["triangles"]
    ) < len(
        lod_2["triangles"]
    )


def test_synthetic_mosque_filter_is_opt_in_and_non_mutating():
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
