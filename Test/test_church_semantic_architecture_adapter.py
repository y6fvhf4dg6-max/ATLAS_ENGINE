from __future__ import annotations

import pytest

from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_church_semantic_architecture_adapter import (
    AtlasChurchSemanticArchitectureAdapter,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _landmark(
    *,
    landmark_type=AtlasLandmarkType.CHURCH,
):
    return AtlasLandmark(
        id=701,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags={},
        source="OSM",
    )


def _build_geometry(
    *,
    landmark_type=AtlasLandmarkType.CHURCH,
    profile=None,
):
    if profile is None:
        profile = AtlasChurchLandmarkProfile()

    return AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=landmark_type,
        ),
        profile=profile,
    )


def test_adapter_builds_common_semantic_architecture_model():
    model = AtlasChurchSemanticArchitectureAdapter.adapt(
        _build_geometry()
    )

    assert isinstance(
        model,
        AtlasSemanticArchitectureModel,
    )
    assert model.landmark_family == "church"
    assert model.grammar_name == "auto"

    assert tuple(
        component.role
        for component in model.components
    ) == (
        "nave",
        "transept",
        "apse",
        "tower",
        "buttress_system",
        "window_bay_system",
        "roof_section",
        "roof_section",
        "roof_section",
        "roof_section",
    )


def test_adapter_maps_church_geometry_kinds_and_parent_roles():
    model = AtlasChurchSemanticArchitectureAdapter.adapt(
        _build_geometry()
    )

    nave = model.components_for_role("nave")[0]
    tower = model.components_for_role("tower")[0]
    roof_sections = model.components_for_role(
        "roof_section"
    )

    assert nave.geometry_kind == "polygon_extrusion"

    assert tower.geometry_kind == "tower_volume"
    assert tower.parent_role == "nave"

    assert tuple(
        component.parent_role
        for component in roof_sections
    ) == (
        "nave",
        "transept",
        "apse",
        "tower",
    )
    assert tuple(
        component.instance_index
        for component in roof_sections
    ) == (
        0,
        1,
        2,
        3,
    )


def test_adapter_preserves_resolved_tower_types_as_flags():
    geometry = _build_geometry(
        landmark_type=AtlasLandmarkType.CATHEDRAL,
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="bonn_muenster_catalog",
            tower_count=2,
        ),
    )

    model = AtlasChurchSemanticArchitectureAdapter.adapt(
        geometry
    )

    assert model.grammar_name == "bonn_muenster_catalog"

    assert tuple(
        component.flags
        for component in model.components_for_role(
            "tower"
        )
    ) == (
        ("section_crossing_tower",),
        ("section_outer_polygon_tower",),
        ("section_west_tower_left",),
        ("section_west_tower_right",),
    )


def test_adapter_preserves_physical_detail_actions_as_flags():
    model = AtlasChurchSemanticArchitectureAdapter.adapt(
        _build_geometry()
    )

    buttresses = model.components_for_role(
        "buttress_system"
    )[0]
    windows = model.components_for_role(
        "window_bay_system"
    )[0]

    assert len(buttresses.flags) == 1
    assert buttresses.flags[0] in {
        "physical_preserve",
        "physical_enlarge",
        "physical_omit",
    }

    assert len(windows.flags) == 1
    assert windows.flags[0] in {
        "physical_preserve",
        "physical_enlarge",
        "physical_omit",
    }


def test_adapter_rejects_non_church_geometry():
    with pytest.raises(
        TypeError,
        match="AtlasChurchLandmarkGeometry",
    ):
        AtlasChurchSemanticArchitectureAdapter.adapt(
            object()
        )
