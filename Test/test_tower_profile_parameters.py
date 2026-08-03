import pytest

from CORE.atlas_tower_builder import AtlasTowerBuilder


def test_tower_builder_parses_height_with_metre_unit():
    class Landmark:
        tags = {
            "height": "62.59 m",
            "building:levels": "9",
            "wikidata": "Q91274",
            "name": "Galata Kulesi",
            "man_made": "tower",
            "historic": "tower",
            "tower:type": (
                "observation;"
                "museum_and_observation"
            ),
            "roof:height": "10.94",
            "roof:shape": "pyramidal",
        }
        geometry = (
            (0.0, 0.0),
            (7.0, 0.0),
            (7.0, 7.0),
            (0.0, 7.0),
        )

    geometry = AtlasTowerBuilder.build(
        Landmark()
    )

    assert geometry.height_m == pytest.approx(
        62.59,
        abs=1e-9,
    )
    assert geometry.roof_height_m == pytest.approx(
        10.94,
        abs=1e-9,
    )
    assert geometry.profile == "galata"
