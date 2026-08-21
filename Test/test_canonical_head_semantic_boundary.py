from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_semantic_boundary import (
    AtlasCanonicalHeadSemanticBoundary,
)


def _boundary():
    return AtlasCanonicalHeadSemanticBoundary.production_v1()


def test_production_boundary_defines_canonical_head_surface_ownership():
    boundary = _boundary()

    assert boundary.canonical_head_regions == (
        "face",
        "left_ear",
        "right_ear",
        "jaw",
        "chin",
        "neck",
        "left_eye_region",
        "right_eye_region",
    )


def test_hair_is_a_separate_semantic_component():
    boundary = _boundary()

    assert "hair" not in boundary.canonical_head_regions
    assert "hair" in boundary.separate_components
    assert boundary.owner_of("hair") == "separate_component"


def test_eyeballs_are_separate_from_canonical_eye_regions():
    boundary = _boundary()

    assert "left_eye_region" in boundary.canonical_head_regions
    assert "right_eye_region" in boundary.canonical_head_regions

    assert "left_eyeball" in boundary.separate_components
    assert "right_eyeball" in boundary.separate_components

    assert boundary.owner_of("left_eye_region") == "canonical_head"
    assert boundary.owner_of("left_eyeball") == "separate_component"


def test_beard_and_moustache_are_optional_detail_layers():
    boundary = _boundary()

    assert boundary.optional_detail_layers == (
        "beard",
        "moustache",
    )

    assert boundary.owner_of("beard") == "optional_detail_layer"
    assert boundary.owner_of("moustache") == "optional_detail_layer"


@pytest.mark.parametrize(
    ("semantic_name", "expected_owner"),
    (
        ("face", "canonical_head"),
        ("left_ear", "canonical_head"),
        ("right_ear", "canonical_head"),
        ("jaw", "canonical_head"),
        ("chin", "canonical_head"),
        ("neck", "canonical_head"),
        ("left_eye_region", "canonical_head"),
        ("right_eye_region", "canonical_head"),
        ("hair", "separate_component"),
        ("left_eyeball", "separate_component"),
        ("right_eyeball", "separate_component"),
        ("beard", "optional_detail_layer"),
        ("moustache", "optional_detail_layer"),
    ),
)
def test_owner_of_returns_explicit_semantic_ownership(
    semantic_name,
    expected_owner,
):
    assert _boundary().owner_of(semantic_name) == expected_owner


def test_owner_lookup_normalizes_semantic_name():
    boundary = _boundary()

    assert boundary.owner_of("  Left Eye Region  ") == "canonical_head"
    assert boundary.owner_of("LEFT EYEBALL") == "separate_component"


def test_unknown_semantic_name_is_rejected():
    with pytest.raises(
        KeyError,
        match="semantic ownership",
    ):
        _boundary().owner_of("unknown-part")


def test_boundary_is_immutable():
    boundary = _boundary()

    with pytest.raises(FrozenInstanceError):
        boundary.canonical_head_regions = ()


def test_contract_does_not_claim_geometry_provider_or_identity_confidence():
    boundary = _boundary()

    assert not hasattr(boundary, "vertices")
    assert not hasattr(boundary, "faces")
    assert not hasattr(boundary, "provider_id")
    assert not hasattr(boundary, "confidence")
    assert not hasattr(boundary, "likeness_score")
    assert not hasattr(boundary, "identity_shape")
