from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_church_body_profile_system import (
    AtlasChurchBodyProfile,
    AtlasChurchBodyProfileSystem,
)


def test_cross_plan_preserves_existing_body_ratios():
    profile = AtlasChurchBodyProfileSystem.resolve(
        "cross_plan"
    )

    assert isinstance(
        profile,
        AtlasChurchBodyProfile,
    )
    assert profile.plan_type == "cross_plan"
    assert profile.nave_width_ratio == pytest.approx(0.52)
    assert profile.nave_depth_ratio == pytest.approx(0.78)
    assert profile.outer_aisle_height_ratio == pytest.approx(0.72)
    assert profile.transept_depth_ratio == pytest.approx(0.22)
    assert profile.transept_width_ratio == pytest.approx(0.84)
    assert profile.transept_height_ratio == pytest.approx(0.92)
    assert profile.apse_depth_ratio == pytest.approx(0.14)
    assert profile.apse_width_ratio == pytest.approx(0.78)
    assert profile.apse_height_ratio == pytest.approx(0.82)


def test_basilica_cross_plan_strengthens_longitudinal_body_hierarchy():
    profile = AtlasChurchBodyProfileSystem.resolve(
        "basilica_cross_plan"
    )

    assert profile.plan_type == "basilica_cross_plan"
    assert profile.nave_width_ratio == pytest.approx(0.46)
    assert profile.nave_depth_ratio == pytest.approx(0.82)
    assert profile.outer_aisle_height_ratio == pytest.approx(0.68)
    assert profile.transept_depth_ratio == pytest.approx(0.24)
    assert profile.transept_width_ratio == pytest.approx(0.88)
    assert profile.transept_height_ratio == pytest.approx(0.92)
    assert profile.apse_depth_ratio == pytest.approx(0.16)
    assert profile.apse_width_ratio == pytest.approx(0.74)
    assert profile.apse_height_ratio == pytest.approx(0.82)


def test_body_profile_resolution_normalizes_plan_type():
    profile = AtlasChurchBodyProfileSystem.resolve(
        " Basilica Cross Plan "
    )

    assert profile.plan_type == "basilica_cross_plan"


def test_body_profile_is_immutable():
    profile = AtlasChurchBodyProfileSystem.resolve(
        "cross_plan"
    )

    with pytest.raises(FrozenInstanceError):
        profile.nave_width_ratio = 0.10


def test_unknown_body_plan_is_rejected():
    with pytest.raises(
        ValueError,
        match="unsupported church plan_type",
    ):
        AtlasChurchBodyProfileSystem.resolve(
            "centralized_octagon"
        )
