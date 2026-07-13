"""
ATLAS Building Vertical Parts Regression Tests

OSM min_height ve building:min_level değerlerinin bina veri
modeline doğru aktarılmasını doğrular.
"""

from CORE.atlas_building import AtlasBuilding


GEOMETRY = [
    (39.0000, 32.0000),
    (39.0000, 32.0010),
    (39.0010, 32.0010),
    (39.0010, 32.0000),
]


def make_building(tags):
    return AtlasBuilding(
        building_id=1,
        source="TEST",
        geometry=GEOMETRY,
        tags=tags,
    )


def test_building_parses_min_height():
    building = make_building(
        {
            "building": "yes",
            "height": "25",
            "min_height": "22",
        }
    )

    assert building.height == 25.0
    assert building.min_height == 22.0


def test_building_parses_min_height_with_unit():
    building = make_building(
        {
            "building": "yes",
            "min_height": "22 m",
        }
    )

    assert building.min_height == 22.0


def test_building_parses_min_level():
    building = make_building(
        {
            "building": "yes",
            "building:levels": "7",
            "building:min_level": "6",
        }
    )

    assert building.levels == 7
    assert building.min_level == 6


def test_invalid_vertical_part_values_become_none():
    building = make_building(
        {
            "building": "yes",
            "min_height": "unknown",
            "building:min_level": "unknown",
        }
    )

    assert building.min_height is None
    assert building.min_level is None


def test_summary_contains_vertical_part_fields():
    building = make_building(
        {
            "building": "yes",
            "height": "25",
            "min_height": "22",
            "building:levels": "7",
            "building:min_level": "6",
        }
    )

    summary = building.summary()

    assert summary["min_height"] == 22.0
    assert summary["min_level"] == 6
