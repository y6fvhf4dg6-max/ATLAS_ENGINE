from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)


def test_default_church_profile_defines_v01_components():
    profile = AtlasChurchLandmarkProfile()

    assert profile.has_nave is True
    assert profile.has_transept is True
    assert profile.has_apse is True
    assert profile.tower_count == 1
    assert profile.has_spires is True
    assert profile.has_buttresses is True
    assert profile.has_window_bays is True
    assert profile.roof_sections == (
        "nave",
        "transept",
        "apse",
        "tower",
    )


def test_cathedral_profile_supports_twin_towers():
    profile = AtlasChurchLandmarkProfile(
        landmark_class="cathedral",
        tower_count=2,
    )

    assert profile.landmark_class == "cathedral"
    assert profile.tower_count == 2


def test_profile_carries_physical_output_context():
    profile = AtlasChurchLandmarkProfile(
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.2,
    )

    assert profile.scale_ratio == pytest.approx(5500.0)
    assert profile.nozzle_diameter_mm == pytest.approx(0.2)


@pytest.mark.parametrize(
    "landmark_class",
    [
        "",
        "mosque",
        "generic",
    ],
)
def test_rejects_invalid_landmark_class(landmark_class):
    with pytest.raises(ValueError):
        AtlasChurchLandmarkProfile(
            landmark_class=landmark_class,
        )


@pytest.mark.parametrize(
    "tower_count",
    [
        -1,
        3,
        1.5,
    ],
)
def test_rejects_invalid_tower_count(tower_count):
    with pytest.raises(ValueError):
        AtlasChurchLandmarkProfile(
            tower_count=tower_count,
        )


@pytest.mark.parametrize(
    ("scale_ratio", "nozzle_diameter_mm"),
    [
        (0.0, 0.4),
        (-5500.0, 0.4),
        (5500.0, 0.0),
        (5500.0, -0.4),
    ],
)
def test_rejects_non_positive_physical_context(
    scale_ratio,
    nozzle_diameter_mm,
):
    with pytest.raises(ValueError):
        AtlasChurchLandmarkProfile(
            scale_ratio=scale_ratio,
            nozzle_diameter_mm=nozzle_diameter_mm,
        )


def test_profile_is_immutable():
    profile = AtlasChurchLandmarkProfile()

    with pytest.raises(FrozenInstanceError):
        profile.tower_count = 2

def test_church_profile_defines_semantic_profile_name():
    profile = AtlasChurchLandmarkProfile(
        profile_name=" Romanesque Basilica ",
    )

    assert profile.profile_name == "romanesque_basilica"


def test_default_church_profile_uses_generic_semantic_profile():
    profile = AtlasChurchLandmarkProfile()

    assert profile.profile_name == "generic_church"

