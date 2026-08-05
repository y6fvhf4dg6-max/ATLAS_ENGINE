from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_church_semantic_profile_system import (
    AtlasChurchSemanticProfile,
    AtlasChurchSemanticProfileSystem,
)


def test_generic_church_semantic_profile_contract():
    profile = AtlasChurchSemanticProfileSystem.resolve(
        "generic_church"
    )

    assert isinstance(
        profile,
        AtlasChurchSemanticProfile,
    )
    assert profile.name == "generic_church"
    assert profile.architectural_style == "generic"
    assert profile.plan_type == "cross_plan"
    assert profile.tower_scheme == "grammar_driven"
    assert profile.roof_character == "pitched"
    assert profile.facade_rhythm == "regular"


def test_romanesque_cathedral_semantic_profile_contract():
    profile = AtlasChurchSemanticProfileSystem.resolve(
        "romanesque_cathedral"
    )

    assert profile.name == "romanesque_cathedral"
    assert profile.architectural_style == "romanesque"
    assert profile.plan_type == "basilica_cross_plan"
    assert profile.tower_scheme == "multi_tower"
    assert profile.roof_character == "stepped_pitched"
    assert profile.facade_rhythm == "heavy_round_arch"


def test_semantic_profile_resolution_normalizes_name():
    profile = AtlasChurchSemanticProfileSystem.resolve(
        " Romanesque Cathedral "
    )

    assert profile.name == "romanesque_cathedral"


def test_semantic_profile_is_immutable():
    profile = AtlasChurchSemanticProfileSystem.resolve(
        "generic_church"
    )

    with pytest.raises(FrozenInstanceError):
        profile.plan_type = "changed"


def test_unknown_semantic_profile_is_rejected():
    with pytest.raises(
        ValueError,
        match="unsupported church semantic profile",
    ):
        AtlasChurchSemanticProfileSystem.resolve(
            "unknown_style"
        )
