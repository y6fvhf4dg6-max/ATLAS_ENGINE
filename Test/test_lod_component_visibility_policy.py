from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_lod_component_visibility_policy import (
    AtlasLoDComponentVisibilityDecision,
    AtlasLoDComponentVisibilityPolicy,
)
from CORE.atlas_lod_level_catalog import (
    LOD_0,
    LOD_1,
    LOD_2,
    LOD_3,
    LOD_4,
)
from CORE.atlas_semantic_architecture_component import (
    AtlasSemanticArchitectureComponent,
)
from CORE.atlas_semantic_architecture_model import (
    AtlasSemanticArchitectureModel,
)


def _component(
    role,
    *,
    family="church",
    parent_role=None,
    instance_index=0,
):
    return AtlasSemanticArchitectureComponent(
        landmark_family=family,
        role=role,
        geometry_kind="polygon_extrusion",
        parent_role=parent_role,
        instance_index=instance_index,
    )


@pytest.mark.parametrize(
    (
        "role",
        "feature",
    ),
    (
        (
            "footprint",
            "footprint",
        ),
        (
            "foundation",
            "base_mass",
        ),
        (
            "base_mass",
            "base_mass",
        ),
        (
            "body",
            "main_body",
        ),
        (
            "nave",
            "main_body",
        ),
        (
            "transept",
            "main_body",
        ),
        (
            "prayer_hall",
            "main_body",
        ),
        (
            "roof_section",
            "primary_roof",
        ),
        (
            "tower",
            "tower",
        ),
        (
            "crossing_tower",
            "tower",
        ),
        (
            "minaret_body",
            "tower",
        ),
        (
            "minaret_cap",
            "tower",
        ),
        (
            "main_dome",
            "dome",
        ),
        (
            "dome_drum",
            "dome",
        ),
        (
            "apse",
            "apse",
        ),
        (
            "facade_opening",
            "facade_opening",
        ),
        (
            "window_bay_system",
            "facade_opening",
        ),
        (
            "facade_structural_detail",
            "structural_detail",
        ),
        (
            "buttress_system",
            "structural_detail",
        ),
        (
            "ornament",
            "ornament",
        ),
        (
            "architectural_relief",
            "architectural_relief",
        ),
        (
            "unclassified_component",
            "major_component",
        ),
    ),
)
def test_policy_maps_semantic_roles_to_lod_features(
    role,
    feature,
):
    assert (
        AtlasLoDComponentVisibilityPolicy
        .required_feature(
            _component(role)
        )
        == feature
    )


@pytest.mark.parametrize(
    (
        "level",
        "role",
        "visible",
    ),
    (
        (
            LOD_0,
            "footprint",
            True,
        ),
        (
            LOD_0,
            "body",
            False,
        ),
        (
            LOD_1,
            "body",
            True,
        ),
        (
            LOD_1,
            "roof_section",
            True,
        ),
        (
            LOD_1,
            "tower",
            False,
        ),
        (
            LOD_2,
            "tower",
            True,
        ),
        (
            LOD_2,
            "main_dome",
            True,
        ),
        (
            LOD_2,
            "apse",
            True,
        ),
        (
            LOD_2,
            "facade_opening",
            False,
        ),
        (
            LOD_3,
            "facade_opening",
            True,
        ),
        (
            LOD_3,
            "buttress_system",
            True,
        ),
        (
            LOD_3,
            "ornament",
            False,
        ),
        (
            LOD_4,
            "ornament",
            True,
        ),
        (
            LOD_4,
            "architectural_relief",
            True,
        ),
    ),
)
def test_policy_resolves_component_visibility(
    level,
    role,
    visible,
):
    decision = (
        AtlasLoDComponentVisibilityPolicy.resolve(
            component=_component(role),
            level=level,
        )
    )

    assert isinstance(
        decision,
        AtlasLoDComponentVisibilityDecision,
    )
    assert decision.visible is visible
    assert decision.level is level
    assert decision.component.role == role


def test_visibility_decision_is_immutable():
    decision = (
        AtlasLoDComponentVisibilityPolicy.resolve(
            component=_component("tower"),
            level=LOD_2,
        )
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        decision.visible = False


def test_policy_filters_model_components_in_source_order():
    model = AtlasSemanticArchitectureModel(
        landmark_family="church",
        grammar_name="single_west_tower",
        components=(
            _component("body"),
            _component(
                "roof_section",
                parent_role="body",
            ),
            _component(
                "tower",
                parent_role="body",
            ),
            _component(
                "facade_opening",
                parent_role="body",
            ),
            _component(
                "ornament",
                parent_role="body",
            ),
        ),
    )

    visible = (
        AtlasLoDComponentVisibilityPolicy
        .visible_components(
            model=model,
            level=LOD_2,
        )
    )

    assert tuple(
        component.role
        for component in visible
    ) == (
        "body",
        "roof_section",
        "tower",
    )


def test_policy_keeps_repeated_visible_roles():
    model = AtlasSemanticArchitectureModel(
        landmark_family="mosque",
        grammar_name="multi_dome_multi_minaret",
        components=(
            _component(
                "prayer_hall",
                family="mosque",
            ),
            _component(
                "minaret_body",
                family="mosque",
                parent_role="prayer_hall",
                instance_index=0,
            ),
            _component(
                "minaret_body",
                family="mosque",
                parent_role="prayer_hall",
                instance_index=1,
            ),
        ),
    )

    visible = (
        AtlasLoDComponentVisibilityPolicy
        .visible_components(
            model=model,
            level=LOD_2,
        )
    )

    assert tuple(
        component.instance_index
        for component in visible
        if component.role == "minaret_body"
    ) == (
        0,
        1,
    )


@pytest.mark.parametrize(
    (
        "method",
        "kwargs",
        "message",
    ),
    (
        (
            "required_feature",
            {
                "component": object(),
            },
            "component",
        ),
        (
            "resolve",
            {
                "component": object(),
                "level": LOD_2,
            },
            "component",
        ),
        (
            "resolve",
            {
                "component": _component("body"),
                "level": object(),
            },
            "level",
        ),
        (
            "visible_components",
            {
                "model": object(),
                "level": LOD_2,
            },
            "model",
        ),
    ),
)
def test_policy_rejects_invalid_contracts(
    method,
    kwargs,
    message,
):
    callable_ = getattr(
        AtlasLoDComponentVisibilityPolicy,
        method,
    )

    with pytest.raises(
        TypeError,
        match=message,
    ):
        callable_(
            **kwargs
        )
