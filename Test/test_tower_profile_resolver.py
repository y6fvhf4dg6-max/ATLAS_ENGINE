from CORE.atlas_tower_profile_resolver import (
    AtlasTowerProfileResolver,
)


def test_observation_tower_uses_observation_profile():
    profile = AtlasTowerProfileResolver.resolve(
        {
            "tower:type": "observation",
        }
    )

    assert profile == "observation"


def test_generic_tower_uses_generic_profile():
    profile = AtlasTowerProfileResolver.resolve({})

    assert profile == "generic"


def test_clock_tower_uses_clock_profile():
    profile = AtlasTowerProfileResolver.resolve(
        {
            "amenity": "clock",
            "man_made": "tower",
            "building:part": "yes",
            "roof:shape": "pyramidal",
        }
    )

    assert profile == "clock"


def test_galata_tower_uses_galata_profile():
    profile = AtlasTowerProfileResolver.resolve(
        {
            "wikidata": "Q91274",
            "name": "Galata Kulesi",
            "historic": "tower",
            "man_made": "tower",
            "tower:type": (
                "observation;"
                "museum_and_observation"
            ),
        }
    )

    assert profile == "galata"


def test_generic_observation_tower_does_not_use_galata_profile():
    profile = AtlasTowerProfileResolver.resolve(
        {
            "historic": "tower",
            "man_made": "tower",
            "tower:type": "observation",
        }
    )

    assert profile == "observation"
