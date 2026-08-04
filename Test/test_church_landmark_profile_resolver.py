from CORE.atlas_church_landmark_profile_resolver import (
    AtlasChurchLandmarkProfileResolver,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def _landmark(
    *,
    landmark_id,
    landmark_type=AtlasLandmarkType.CATHEDRAL,
    name=None,
    wikidata=None,
):
    tags = {
        "building": (
            "cathedral"
            if landmark_type is AtlasLandmarkType.CATHEDRAL
            else "church"
        ),
    }

    if name is not None:
        tags["name"] = name

    if wikidata is not None:
        tags["wikidata"] = wikidata

    return AtlasLandmark(
        id=landmark_id,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
        ),
        tags=tags,
        source="OSM",
    )


def test_bonner_muenster_profile_disables_synthetic_front_apse():
    profile = AtlasChurchLandmarkProfileResolver.resolve(
        _landmark(
            landmark_id=112526702,
            name="Bonner Münster",
            wikidata="Q686664",
        ),
        scale_ratio=5500.0,
    )

    assert profile.landmark_class == "cathedral"
    assert profile.has_apse is False


def test_generic_cathedral_preserves_default_apse():
    profile = AtlasChurchLandmarkProfileResolver.resolve(
        _landmark(
            landmark_id=999001,
            name="Generic Cathedral",
        ),
        scale_ratio=5500.0,
    )

    assert profile.landmark_class == "cathedral"
    assert profile.has_apse is True


def test_generic_church_resolves_church_profile():
    profile = AtlasChurchLandmarkProfileResolver.resolve(
        _landmark(
            landmark_id=999002,
            landmark_type=AtlasLandmarkType.CHURCH,
            name="Generic Church",
        ),
        scale_ratio=3000.0,
    )

    assert profile.landmark_class == "church"
    assert profile.scale_ratio == 3000.0


def test_profile_resolver_carries_bonner_muenster_catalog_grammar():
    profile = AtlasChurchLandmarkProfileResolver.resolve(
        _landmark(
            landmark_id=112526702,
            name="Bonner Münster",
            wikidata="Q686664",
        ),
        scale_ratio=5500.0,
    )

    assert profile.grammar_name == "bonn_muenster_catalog"


def test_profile_resolver_uses_safe_default_grammar_for_unknown_church():
    profile = AtlasChurchLandmarkProfileResolver.resolve(
        _landmark(
            landmark_id=999003,
            landmark_type=AtlasLandmarkType.CHURCH,
            name="Unknown Church",
        ),
        scale_ratio=5500.0,
    )

    assert profile.grammar_name == "single_west_tower"


def test_bonner_muenster_geometry_override_resolves_with_normalized_wikidata():
    profile = AtlasChurchLandmarkProfileResolver.resolve(
        _landmark(
            landmark_id=999999,
            name="Bonner Münster",
            wikidata=" q686664 ",
        ),
        scale_ratio=5500.0,
    )

    assert profile.has_apse is False
