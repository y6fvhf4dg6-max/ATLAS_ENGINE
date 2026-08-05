from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_landmark_validation_engine import (
    AtlasLandmarkValidationEngine,
    AtlasLandmarkValidationResult,
)


def _source(
    *,
    source_id=100,
    geometry=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0)),
    **tags,
):
    return {
        "id": source_id,
        "geometry": geometry,
        "tags": tags,
    }


def test_catalog_identity_overrides_conflicting_osm_family():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            source_id=322722702,
            name="Cenabi Ahmet Paşa Cami",
            wikidata="Q96278624",
            building="church",
            amenity="place_of_worship",
            religion="muslim",
        )
    )

    assert isinstance(
        result,
        AtlasLandmarkValidationResult,
    )
    assert result.family == "mosque"
    assert result.confidence == "high"
    assert result.action == "special"
    assert result.catalog_key == (
        "cenabi-ahmet-pasha-mosque"
    )
    assert result.grammar_name == (
        "single_dome_single_minaret"
    )
    assert result.has_conflict is True
    assert "building_religion_conflict" in (
        result.conflicts
    )


def test_consistent_explicit_mosque_is_accepted_with_fallback():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            building="mosque",
            amenity="place_of_worship",
            religion="muslim",
        )
    )

    assert result.family == "mosque"
    assert result.confidence == "high"
    assert result.action == "fallback"
    assert result.catalog_key is None
    assert result.grammar_name is None
    assert result.conflicts == ()


def test_generic_worship_building_is_inferred_with_medium_confidence():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            building="yes",
            amenity="place_of_worship",
            religion="jewish",
        )
    )

    assert result.family == "synagogue"
    assert result.confidence == "medium"
    assert result.action == "fallback"
    assert "religion_inference" in result.evidence


def test_conflicting_uncataloged_worship_requires_review():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            building="church",
            amenity="place_of_worship",
            religion="muslim",
        )
    )

    assert result.family == "unknown"
    assert result.confidence == "low"
    assert result.action == "review"
    assert result.has_conflict is True
    assert "building_religion_conflict" in (
        result.conflicts
    )


def test_unknown_non_landmark_is_rejected():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            building="house",
        )
    )

    assert result.family == "unknown"
    assert result.confidence == "low"
    assert result.action == "reject"
    assert result.conflicts == ()


def test_missing_geometry_for_recognized_family_requires_review():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            geometry=(),
            building="cathedral",
            amenity="place_of_worship",
            religion="christian",
        )
    )

    assert result.family == "cathedral"
    assert result.confidence == "low"
    assert result.action == "review"
    assert "missing_footprint" in result.conflicts


def test_validation_result_is_immutable():
    result = AtlasLandmarkValidationEngine.validate(
        _source(
            building="mosque",
            amenity="place_of_worship",
            religion="muslim",
        )
    )

    with pytest.raises(FrozenInstanceError):
        result.family = "church"
