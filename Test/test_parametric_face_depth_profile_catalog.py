import pytest

from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)
from CORE.atlas_parametric_face_depth_profile_catalog import (
    AtlasParametricFaceDepthProfileCatalog,
)


def test_catalog_exposes_neutral_anatomical_profile():
    profile = (
        AtlasParametricFaceDepthProfileCatalog
        .NEUTRAL_ANATOMICAL
    )

    assert isinstance(
        profile,
        AtlasParametricFaceDepthProfile,
    )
    assert profile.name == "neutral-anatomical"


def test_neutral_anatomical_profile_preserves_expected_depths():
    profile = (
        AtlasParametricFaceDepthProfileCatalog
        .NEUTRAL_ANATOMICAL
    )

    assert profile.brow_projection == pytest.approx(
        0.026,
    )
    assert profile.eye_socket_depth == pytest.approx(
        0.035,
    )
    assert profile.cheek_projection == pytest.approx(
        0.060,
    )
    assert profile.nose_bridge_projection == pytest.approx(
        0.110,
    )
    assert profile.nose_tip_projection == pytest.approx(
        0.160,
    )
    assert profile.nose_wing_projection == pytest.approx(
        0.045,
    )
    assert profile.upper_lip_projection == pytest.approx(
        0.035,
    )
    assert profile.lower_lip_projection == pytest.approx(
        0.045,
    )
    assert profile.philtrum_depth == pytest.approx(
        0.018,
    )
    assert profile.labiomental_fold_depth == pytest.approx(
        0.022,
    )
    assert profile.chin_projection == pytest.approx(
        0.070,
    )


def test_catalog_names_are_deterministic():
    assert (
        AtlasParametricFaceDepthProfileCatalog.names()
        == (
            "neutral-anatomical",
        )
    )


def test_catalog_get_returns_named_profile():
    profile = AtlasParametricFaceDepthProfileCatalog.get(
        "neutral-anatomical",
    )

    assert (
        profile
        is AtlasParametricFaceDepthProfileCatalog
        .NEUTRAL_ANATOMICAL
    )


def test_catalog_get_strips_name():
    profile = AtlasParametricFaceDepthProfileCatalog.get(
        "  neutral-anatomical  ",
    )

    assert (
        profile
        is AtlasParametricFaceDepthProfileCatalog
        .NEUTRAL_ANATOMICAL
    )


def test_catalog_get_rejects_unknown_name():
    with pytest.raises(
        KeyError,
        match=(
            "unknown parametric face depth profile"
        ),
    ):
        AtlasParametricFaceDepthProfileCatalog.get(
            "unknown",
        )


@pytest.mark.parametrize(
    "invalid_name",
    [
        "",
        "   ",
    ],
)
def test_catalog_get_rejects_blank_name(
    invalid_name,
):
    with pytest.raises(
        ValueError,
        match="name must not be blank",
    ):
        AtlasParametricFaceDepthProfileCatalog.get(
            invalid_name,
        )


def test_catalog_get_rejects_non_string_name():
    with pytest.raises(
        TypeError,
        match="name must be a string",
    ):
        AtlasParametricFaceDepthProfileCatalog.get(
            123,
        )


def test_catalog_instances_are_not_rebuilt():
    first = AtlasParametricFaceDepthProfileCatalog.get(
        "neutral-anatomical",
    )
    second = AtlasParametricFaceDepthProfileCatalog.get(
        "neutral-anatomical",
    )

    assert first is second
