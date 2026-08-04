import pytest

from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType
from CORE.atlas_worship_grammar_resolver import (
    AtlasWorshipGrammarResolver,
)


def _landmark(
    *,
    landmark_type,
    tags=None,
):
    return AtlasLandmark(
        id=1001,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 30.0),
            (0.0, 30.0),
        ),
        tags=tags or {},
        source="OSM",
    )


def test_unknown_mosque_uses_safe_footprint_fallback():
    grammar = AtlasWorshipGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.MOSQUE,
            tags={
                "building": "mosque",
                "religion": "muslim",
            },
        )
    )

    assert grammar == "footprint_fallback"


def test_unknown_synagogue_uses_safe_footprint_fallback():
    grammar = AtlasWorshipGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.SYNAGOGUE,
            tags={
                "building": "synagogue",
                "religion": "jewish",
            },
        )
    )

    assert grammar == "footprint_fallback"


def test_explicit_mosque_grammar_tag_is_normalized():
    grammar = AtlasWorshipGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.MOSQUE,
            tags={
                "building": "mosque",
                "religion": "muslim",
                "atlas:worship_grammar": (
                    " SINGLE_DOME_SINGLE_MINARET "
                ),
            },
        )
    )

    assert grammar == "single_dome_single_minaret"


def test_explicit_synagogue_grammar_tag_is_normalized():
    grammar = AtlasWorshipGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.SYNAGOGUE,
            tags={
                "building": "synagogue",
                "religion": "jewish",
                "atlas:worship_grammar": (
                    " TWIN_TOWER_FACADE "
                ),
            },
        )
    )

    assert grammar == "twin_tower_facade"


def test_rejects_grammar_incompatible_with_landmark_type():
    with pytest.raises(
        ValueError,
        match="not valid for mosque",
    ):
        AtlasWorshipGrammarResolver.resolve(
            _landmark(
                landmark_type=AtlasLandmarkType.MOSQUE,
                tags={
                    "building": "mosque",
                    "atlas:worship_grammar": (
                        "basilica_hall"
                    ),
                },
            )
        )


def test_rejects_non_worship_landmark():
    with pytest.raises(
        ValueError,
        match="mosque or synagogue",
    ):
        AtlasWorshipGrammarResolver.resolve(
            _landmark(
                landmark_type=AtlasLandmarkType.TOWER,
            )
        )
