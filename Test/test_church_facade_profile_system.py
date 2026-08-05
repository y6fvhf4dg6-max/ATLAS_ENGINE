from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_church_facade_profile_system import (
    AtlasChurchFacadeProfile,
    AtlasChurchFacadeProfileSystem,
)


def test_regular_facade_profile_defines_balanced_bay_rhythm():
    profile = AtlasChurchFacadeProfileSystem.resolve(
        "regular"
    )

    assert isinstance(
        profile,
        AtlasChurchFacadeProfile,
    )
    assert profile.facade_rhythm == "regular"
    assert profile.bay_spacing_ratio == pytest.approx(0.18)
    assert profile.opening_width_ratio == pytest.approx(0.28)
    assert profile.opening_height_ratio == pytest.approx(0.34)
    assert profile.arch_shape == "simple_arch"
    assert profile.recess_depth_ratio == pytest.approx(0.04)


def test_heavy_round_arch_profile_strengthens_romanesque_facade_mass():
    profile = AtlasChurchFacadeProfileSystem.resolve(
        "heavy_round_arch"
    )

    assert profile.facade_rhythm == "heavy_round_arch"
    assert profile.bay_spacing_ratio == pytest.approx(0.22)
    assert profile.opening_width_ratio == pytest.approx(0.24)
    assert profile.opening_height_ratio == pytest.approx(0.30)
    assert profile.arch_shape == "round_arch"
    assert profile.recess_depth_ratio == pytest.approx(0.06)


def test_facade_profile_resolution_normalizes_identifier():
    profile = AtlasChurchFacadeProfileSystem.resolve(
        " Heavy Round Arch "
    )

    assert profile.facade_rhythm == "heavy_round_arch"


def test_facade_profile_is_immutable():
    profile = AtlasChurchFacadeProfileSystem.resolve(
        "regular"
    )

    with pytest.raises(FrozenInstanceError):
        profile.opening_width_ratio = 0.10


def test_unknown_facade_rhythm_is_rejected():
    with pytest.raises(
        ValueError,
        match="unsupported church facade_rhythm",
    ):
        AtlasChurchFacadeProfileSystem.resolve(
            "glass_curtain"
        )

def test_regular_profile_defines_front_and_rear_compositions():
    profile = AtlasChurchFacadeProfileSystem.resolve(
        "regular"
    )

    assert (
        profile.front_composition
        == "single_arch_portal"
    )
    assert (
        profile.rear_composition
        == "single_arch_opening"
    )


def test_heavy_round_arch_profile_adds_oculus_composition():
    profile = AtlasChurchFacadeProfileSystem.resolve(
        "heavy_round_arch"
    )

    assert (
        profile.front_composition
        == "portal_with_oculus"
    )
    assert (
        profile.rear_composition
        == "round_arch_opening"
    )


def test_facade_composition_identifiers_are_normalized():
    profile = AtlasChurchFacadeProfile(
        facade_rhythm=" Custom Rhythm ",
        bay_spacing_ratio=0.20,
        opening_width_ratio=0.30,
        opening_height_ratio=0.40,
        arch_shape=" Round Arch ",
        recess_depth_ratio=0.05,
        front_composition=" Portal With Oculus ",
        rear_composition=" Round Arch Opening ",
    )

    assert (
        profile.front_composition
        == "portal_with_oculus"
    )
    assert (
        profile.rear_composition
        == "round_arch_opening"
    )

