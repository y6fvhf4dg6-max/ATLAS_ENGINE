from CORE.atlas_church_grammar_resolver import (
    AtlasChurchGrammarResolver,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def _landmark(
    *,
    landmark_type,
    wikidata=None,
    architecture=None,
):
    tags = {
        "building": (
            "cathedral"
            if landmark_type is AtlasLandmarkType.CATHEDRAL
            else "church"
        ),
    }

    if wikidata is not None:
        tags["wikidata"] = wikidata

    if architecture is not None:
        tags["building:architecture"] = architecture

    return AtlasLandmark(
        id=1001,
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


def test_bonner_muenster_uses_catalog_grammar():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
            wikidata="Q686664",
            architecture="romanesque",
        )
    )

    assert grammar == "bonn_muenster_catalog"


def test_kreuzkirche_uses_single_west_tower_grammar():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CHURCH,
            wikidata="Q1788329",
        )
    )

    assert grammar == "single_west_tower"


def test_unknown_church_uses_safe_single_west_tower_grammar():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CHURCH,
        )
    )

    assert grammar == "single_west_tower"


def test_unknown_cathedral_uses_twin_west_tower_grammar():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        )
    )

    assert grammar == "twin_west_towers"


def test_catalog_wikidata_matching_is_normalized():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
            wikidata=" q686664 ",
        )
    )

    assert grammar == "bonn_muenster_catalog"


def _hierarchy_context(
    *,
    parent_id=1001,
    tower_count,
):
    parts = [
        {
            "id": 2000 + index,
            "tags": {
                "building:part": "yes",
                "tower:type": "bell_tower",
            },
        }
        for index in range(tower_count)
    ]

    return {
        "parents": {
            parent_id: {
                "parts": parts,
                "part_ids": [
                    part["id"]
                    for part in parts
                ],
            },
        },
    }


def test_hierarchy_single_bell_tower_selects_single_west_tower():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        hierarchy_context=_hierarchy_context(
            tower_count=1,
        ),
    )

    assert grammar == "single_west_tower"


def test_hierarchy_twin_bell_towers_selects_twin_west_towers():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CHURCH,
        ),
        hierarchy_context=_hierarchy_context(
            tower_count=2,
        ),
    )

    assert grammar == "twin_west_towers"


def test_hierarchy_three_bell_towers_preserves_safe_family_default():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CHURCH,
        ),
        hierarchy_context=_hierarchy_context(
            tower_count=3,
        ),
    )

    assert grammar == "single_west_tower"


def test_catalog_grammar_precedes_hierarchy_tower_evidence():
    grammar = AtlasChurchGrammarResolver.resolve(
        _landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
            wikidata="Q686664",
        ),
        hierarchy_context=_hierarchy_context(
            tower_count=1,
        ),
    )

    assert grammar == "bonn_muenster_catalog"
