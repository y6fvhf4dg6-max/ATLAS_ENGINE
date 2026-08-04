from __future__ import annotations

import pytest

from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_mosque_landmark_builder import (
    AtlasMosqueLandmarkBuilder,
)
from CORE.atlas_mosque_landmark_profile import (
    AtlasMosqueLandmarkProfile,
)
from CORE.atlas_mosque_semantic_architecture_adapter import (
    AtlasMosqueSemanticArchitectureAdapter,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _geometry():
    landmark = AtlasLandmark(
        id=1201,
        landmark_type=AtlasLandmarkType.MOSQUE,
        geometry=(
            (0.0, 0.0),
            (24.0, 0.0),
            (24.0, 36.0),
            (0.0, 36.0),
        ),
        tags={
            "building": "mosque",
            "religion": "muslim",
        },
        source="OSM",
    )

    return AtlasMosqueLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasMosqueLandmarkProfile(),
    )


def test_adapter_builds_common_semantic_architecture_model():
    model = AtlasMosqueSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == "mosque"
    assert model.grammar_name == (
        "single_dome_single_minaret"
    )

    assert tuple(
        component.role
        for component in model.components
    ) == (
        "prayer_hall",
        "dome_drum",
        "main_dome",
        "minaret_body",
        "minaret_balcony",
        "minaret_cap",
    )


def test_adapter_maps_mosque_geometry_kinds():
    model = AtlasMosqueSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    assert tuple(
        component.geometry_kind
        for component in model.components
    ) == (
        "polygon_extrusion",
        "drum_volume",
        "dome_surface",
        "minaret_shaft",
        "balcony_ring",
        "minaret_cap",
    )


def test_adapter_preserves_component_hierarchy():
    model = AtlasMosqueSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    assert tuple(
        component.parent_role
        for component in model.components
    ) == (
        None,
        "prayer_hall",
        "dome_drum",
        "prayer_hall",
        "minaret_body",
        "minaret_body",
    )


def test_adapter_preserves_component_indexes():
    model = AtlasMosqueSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    assert tuple(
        component.instance_index
        for component in model.components
    ) == (
        0,
        0,
        0,
        0,
        0,
        0,
    )


def test_adapter_carries_real_footprint_flag():
    model = AtlasMosqueSemanticArchitectureAdapter.adapt(
        _geometry()
    )

    assert model.flags == (
        "uses_real_footprint",
    )


def test_adapter_rejects_non_mosque_geometry():
    with pytest.raises(
        TypeError,
        match="AtlasMosqueLandmarkGeometry",
    ):
        AtlasMosqueSemanticArchitectureAdapter.adapt(
            object()
        )
