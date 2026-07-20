import pytest

from CORE.atlas_frontal_face_reference_profile import (
    AtlasFrontalFaceReferenceProfile,
)
from CORE.atlas_frontal_face_reference_profile_catalog import (
    AtlasFrontalFaceReferenceProfileCatalog,
)


def test_catalog_exposes_synthetic_neutral_profile():
    profile = AtlasFrontalFaceReferenceProfileCatalog.SYNTHETIC_NEUTRAL

    assert isinstance(
        profile,
        AtlasFrontalFaceReferenceProfile,
    )
    assert profile.name == "synthetic-neutral"


def test_synthetic_neutral_profile_preserves_expected_ratios():
    profile = AtlasFrontalFaceReferenceProfileCatalog.SYNTHETIC_NEUTRAL

    assert profile.face_width_ratio == pytest.approx(
        0.7500,
    )
    assert profile.eye_spacing_ratio == pytest.approx(
        0.3250,
    )
    assert profile.nose_width_ratio == pytest.approx(
        0.1250,
    )
    assert profile.nose_length_ratio == pytest.approx(
        0.1875,
    )
    assert profile.mouth_width_ratio == pytest.approx(
        0.2250,
    )
    assert profile.jaw_width_ratio == pytest.approx(
        0.5500,
    )
    assert profile.forehead_height_ratio == pytest.approx(
        0.3750,
    )


def test_catalog_names_are_deterministic():
    assert AtlasFrontalFaceReferenceProfileCatalog.names() == ("synthetic-neutral",)


def test_catalog_get_returns_named_profile():
    profile = AtlasFrontalFaceReferenceProfileCatalog.get(
        "synthetic-neutral",
    )

    assert profile is AtlasFrontalFaceReferenceProfileCatalog.SYNTHETIC_NEUTRAL


def test_catalog_get_strips_name():
    profile = AtlasFrontalFaceReferenceProfileCatalog.get(
        "  synthetic-neutral  ",
    )

    assert profile is AtlasFrontalFaceReferenceProfileCatalog.SYNTHETIC_NEUTRAL


def test_catalog_get_rejects_unknown_name():
    with pytest.raises(
        KeyError,
        match="unknown frontal face reference profile",
    ):
        AtlasFrontalFaceReferenceProfileCatalog.get(
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
        AtlasFrontalFaceReferenceProfileCatalog.get(
            invalid_name,
        )


def test_catalog_get_rejects_non_string_name():
    with pytest.raises(
        TypeError,
        match="name must be a string",
    ):
        AtlasFrontalFaceReferenceProfileCatalog.get(
            123,
        )


def test_catalog_instances_are_not_rebuilt():
    first = AtlasFrontalFaceReferenceProfileCatalog.get(
        "synthetic-neutral",
    )
    second = AtlasFrontalFaceReferenceProfileCatalog.get(
        "synthetic-neutral",
    )

    assert first is second
