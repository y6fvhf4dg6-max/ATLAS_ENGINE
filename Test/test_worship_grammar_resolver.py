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

def test_infers_single_minaret_mosque_grammar_from_hierarchy_parts():
    from types import SimpleNamespace

    landmark = SimpleNamespace(
        id=4100,
        landmark_type=AtlasLandmarkType.MOSQUE,
        tags={},
    )

    hierarchy_context = {
        "parents": {
            4100: {
                "parent": {"id": 4100},
                "parts": [
                    {
                        "id": 4101,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                ],
                "part_ids": [4101],
            },
        },
    }

    assert AtlasWorshipGrammarResolver.resolve(
        landmark,
        hierarchy_context=hierarchy_context,
    ) == "single_dome_single_minaret"


def test_infers_multi_minaret_mosque_grammar_from_hierarchy_parts():
    from types import SimpleNamespace

    landmark = SimpleNamespace(
        id=4200,
        landmark_type=AtlasLandmarkType.MOSQUE,
        tags={},
    )

    hierarchy_context = {
        "parents": {
            4200: {
                "parent": {"id": 4200},
                "parts": [
                    {
                        "id": 4201,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 4202,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 4211,
                        "tags": {
                            "building:part": "yes",
                            "roof:shape": "dome",
                        },
                    },
                    {
                        "id": 4212,
                        "tags": {
                            "building:part": "yes",
                            "roof:shape": "dome",
                        },
                    },
                ],
                "part_ids": [
                    4201,
                    4202,
                    4211,
                    4212,
                ],
            },
        },
    }

    assert AtlasWorshipGrammarResolver.resolve(
        landmark,
        hierarchy_context=hierarchy_context,
    ) == "multi_dome_multi_minaret"


def test_explicit_worship_grammar_overrides_hierarchy_inference():
    from types import SimpleNamespace

    landmark = SimpleNamespace(
        id=4300,
        landmark_type=AtlasLandmarkType.MOSQUE,
        tags={
            "atlas:worship_grammar": (
                "single_dome_single_minaret"
            ),
        },
    )

    hierarchy_context = {
        "parents": {
            4300: {
                "parent": {"id": 4300},
                "parts": [
                    {
                        "id": 4301,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 4302,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                ],
                "part_ids": [4301, 4302],
            },
        },
    }

    assert AtlasWorshipGrammarResolver.resolve(
        landmark,
        hierarchy_context=hierarchy_context,
    ) == "single_dome_single_minaret"

def test_multi_minarets_without_dome_evidence_use_safe_fallback():
    from types import SimpleNamespace

    landmark = SimpleNamespace(
        id=4250,
        landmark_type=AtlasLandmarkType.MOSQUE,
        tags={},
    )

    hierarchy_context = {
        "parents": {
            4250: {
                "parent": {"id": 4250},
                "parts": [
                    {
                        "id": 4251,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 4252,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                ],
                "part_ids": [
                    4251,
                    4252,
                ],
            },
        },
    }

    assert AtlasWorshipGrammarResolver.resolve(
        landmark,
        hierarchy_context=hierarchy_context,
    ) == "footprint_fallback"


def test_multi_minarets_with_only_one_dome_use_safe_fallback():
    from types import SimpleNamespace

    landmark = SimpleNamespace(
        id=4260,
        landmark_type=AtlasLandmarkType.MOSQUE,
        tags={},
    )

    hierarchy_context = {
        "parents": {
            4260: {
                "parent": {"id": 4260},
                "parts": [
                    {
                        "id": 4261,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 4262,
                        "tags": {
                            "building:part": "yes",
                            "tower:type": "minaret",
                        },
                    },
                    {
                        "id": 4263,
                        "tags": {
                            "building:part": "yes",
                            "roof:shape": "dome",
                        },
                    },
                ],
                "part_ids": [
                    4261,
                    4262,
                    4263,
                ],
            },
        },
    }

    assert AtlasWorshipGrammarResolver.resolve(
        landmark,
        hierarchy_context=hierarchy_context,
    ) == "footprint_fallback"
