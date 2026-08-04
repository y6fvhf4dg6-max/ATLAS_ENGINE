from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_mesh_builder import (
    AtlasLandmarkMeshBuilder,
)
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _bridge_landmark():
    return AtlasLandmark(
        id="semantic-bridge-1",
        source="test",
        landmark_type=AtlasLandmarkType.BRIDGE,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 6.0),
            (0.0, 6.0),
        ),
        tags={
            "bridge": "yes",
            "height": "8",
        },
    )


def test_mesh_builder_keeps_semantic_architecture_opt_in():
    mesh = AtlasLandmarkMeshBuilder.build(
        _bridge_landmark()
    )

    assert "semantic_architecture" not in mesh


def test_mesh_builder_can_include_bridge_semantic_architecture():
    mesh = AtlasLandmarkMeshBuilder.build(
        _bridge_landmark(),
        include_semantic_architecture=True,
    )

    semantic_model = mesh[
        "semantic_architecture"
    ]

    assert isinstance(
        semantic_model,
        AtlasSemanticArchitectureModel,
    )
    assert semantic_model.landmark_family == "bridge"
    assert semantic_model.components_for_role(
        "deck"
    )


def _church_landmark():
    return AtlasLandmark(
        id=1901,
        source="test",
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags={
            "building": "church",
            "height": "24",
        },
    )


def _premium_mosque_landmark():
    return AtlasLandmark(
        id=1902,
        source="test",
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
            "atlas:worship_grammar": (
                "single_dome_single_minaret"
            ),
        },
    )


def _fallback_mosque_landmark():
    return AtlasLandmark(
        id=1903,
        source="test",
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
        },
    )


def test_mesh_builder_can_include_church_semantic_architecture():
    mesh = AtlasLandmarkMeshBuilder.build(
        _church_landmark(),
        include_semantic_architecture=True,
    )

    semantic_model = mesh[
        "semantic_architecture"
    ]

    assert semantic_model.landmark_family == "church"
    assert semantic_model.components_for_role(
        "nave"
    )


def test_mesh_builder_can_include_premium_mosque_semantic_architecture():
    mesh = AtlasLandmarkMeshBuilder.build(
        _premium_mosque_landmark(),
        include_semantic_architecture=True,
    )

    semantic_model = mesh[
        "semantic_architecture"
    ]

    assert semantic_model.landmark_family == "mosque"
    assert semantic_model.grammar_name == (
        "single_dome_single_minaret"
    )
    assert semantic_model.components_for_role(
        "prayer_hall"
    )
    assert semantic_model.components_for_role(
        "main_dome"
    )


def test_mesh_builder_rejects_semantic_architecture_for_fallback_path():
    import pytest

    with pytest.raises(
        ValueError,
        match="semantic architecture is unavailable",
    ):
        AtlasLandmarkMeshBuilder.build(
            _fallback_mosque_landmark(),
            include_semantic_architecture=True,
        )
