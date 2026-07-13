"""
ATLAS Castle Geometry Classifier Regression Tests

Bu testler, kale OSM kayıtlarının yanlış üretim katmanına
gönderilmesini engeller.

Kilitlenen davranışlar:
1. Relation kale -> shell
2. Kapalı historic=castle way -> dolu shell değil, perimeter wall
3. Açık historic=castle way -> otomatik perimeter wall değil
4. building etiketi taşıyan way -> perimeter wall değil
5. Açıkça tanımlanmış city_wall -> independent wall
6. Relation kaynaklı wall -> relation wall
"""

from CORE.atlas_castle_geometry_classifier import (
    AtlasCastleGeometryClassifier,
)


def closed_geometry():
    return [
        (48.0000, 12.0000),
        (48.0000, 12.0010),
        (48.0010, 12.0010),
        (48.0010, 12.0000),
        (48.0000, 12.0000),
    ]


def open_geometry():
    return [
        (48.0000, 12.0000),
        (48.0000, 12.0010),
        (48.0010, 12.0010),
    ]


def nearly_closed_geometry():
    return [
        (48.1564993, 12.8288699),
        (48.1568000, 12.8295000),
        (48.1571000, 12.8287000),
        (48.1564860, 12.8289046),
    ]


def test_relation_castle_is_classified_as_shell():
    castles = [
        {
            "id": 1001,
            "geometry_type": "relation",
            "geometry": [],
            "tags": {
                "historic": "castle",
            },
        }
    ]

    result = AtlasCastleGeometryClassifier.classify(
        castles=castles,
        castle_walls=[],
        debug=False,
    )

    assert len(result["shell_castles"]) == 1
    assert result["shell_castles"][0]["id"] == 1001
    assert len(result["inferred_perimeter_walls"]) == 0


def test_closed_castle_site_way_becomes_perimeter_wall_not_shell():
    castles = [
        {
            "id": 68741063,
            "geometry_type": "way",
            "geometry": closed_geometry(),
            "tags": {
                "historic": "castle",
                "castle_type": "defensive",
                "name": "Synthetic Burghausen Case",
            },
        }
    ]

    result = AtlasCastleGeometryClassifier.classify(
        castles=castles,
        castle_walls=[],
        debug=False,
    )

    assert len(result["shell_castles"]) == 0
    assert len(result["inferred_perimeter_walls"]) == 1
    assert len(result["independent_castle_walls"]) == 1

    inferred_wall = result["inferred_perimeter_walls"][0]

    assert inferred_wall["source_castle_id"] == 68741063
    assert inferred_wall["inferred"] is True
    assert inferred_wall["wall_type"] == "inferred_castle_perimeter"


def test_open_castle_site_way_is_not_inferred_as_wall():
    castles = [
        {
            "id": 2001,
            "geometry_type": "way",
            "geometry": open_geometry(),
            "tags": {
                "historic": "castle",
            },
        }
    ]

    result = AtlasCastleGeometryClassifier.classify(
        castles=castles,
        castle_walls=[],
        debug=False,
    )

    assert len(result["shell_castles"]) == 0
    assert len(result["inferred_perimeter_walls"]) == 0
    assert len(result["independent_castle_walls"]) == 0
    assert len(result["unknown_castles"]) == 1


def test_castle_building_way_is_not_inferred_as_wall():
    castles = [
        {
            "id": 3001,
            "geometry_type": "way",
            "geometry": closed_geometry(),
            "tags": {
                "historic": "castle",
                "building": "castle",
            },
        }
    ]

    result = AtlasCastleGeometryClassifier.classify(
        castles=castles,
        castle_walls=[],
        debug=False,
    )

    assert len(result["shell_castles"]) == 0
    assert len(result["inferred_perimeter_walls"]) == 0
    assert len(result["independent_castle_walls"]) == 0
    assert len(result["unknown_castles"]) == 1


def test_explicit_city_wall_remains_independent_wall():
    castle_walls = [
        {
            "id": 4001,
            "geometry_type": "way",
            "geometry": open_geometry(),
            "tags": {
                "barrier": "city_wall",
            },
        }
    ]

    result = AtlasCastleGeometryClassifier.classify(
        castles=[],
        castle_walls=castle_walls,
        debug=False,
    )

    assert len(result["independent_castle_walls"]) == 1
    assert result["independent_castle_walls"][0]["id"] == 4001
    assert len(result["relation_castle_walls"]) == 0
    assert len(result["inferred_perimeter_walls"]) == 0


def test_relation_wall_is_not_duplicated_as_independent_wall():
    castle_walls = [
        {
            "id": 5001,
            "source_relation_id": 1001,
            "geometry_type": "way",
            "geometry": open_geometry(),
            "tags": {
                "barrier": "city_wall",
            },
        }
    ]

    result = AtlasCastleGeometryClassifier.classify(
        castles=[],
        castle_walls=castle_walls,
        debug=False,
    )

    assert len(result["independent_castle_walls"]) == 0
    assert len(result["relation_castle_walls"]) == 1
    assert result["relation_castle_walls"][0]["id"] == 5001


def test_nearly_closed_castle_site_way_is_inferred_as_wall():
    castles = [
        {
            "id": 68741063,
            "geometry_type": "way",
            "geometry": nearly_closed_geometry(),
            "tags": {
                "historic": "castle",
                "castle_type": "defensive",
            },
        }
    ]

    closure_gap_m = AtlasCastleGeometryClassifier._distance_meters(
        castles[0]["geometry"][0],
        castles[0]["geometry"][-1],
    )

    assert closure_gap_m > 0.0
    assert closure_gap_m <= 5.0

    result = AtlasCastleGeometryClassifier.classify(
        castles=castles,
        castle_walls=[],
        debug=False,
    )

    assert len(result["shell_castles"]) == 0
    assert len(result["inferred_perimeter_walls"]) == 1
    assert len(result["independent_castle_walls"]) == 1


if __name__ == "__main__":
    tests = [
        test_relation_castle_is_classified_as_shell,
        test_closed_castle_site_way_becomes_perimeter_wall_not_shell,
        test_open_castle_site_way_is_not_inferred_as_wall,
        test_castle_building_way_is_not_inferred_as_wall,
        test_explicit_city_wall_remains_independent_wall,
        test_relation_wall_is_not_duplicated_as_independent_wall,
        test_nearly_closed_castle_site_way_is_inferred_as_wall,
    ]

    for test in tests:
        test()
        print(f"PASS: {test.__name__}")

    print("")
    print(f"ALL TESTS PASSED: {len(tests)}")


def test_castle_way_matching_explicit_city_wall_is_not_unknown():
    castle = {
        "id": 93612350,
        "geometry_type": "way",
        "geometry": closed_geometry(),
        "tags": {
            "historic": "castle",
            "barrier": "city_wall",
            "castle_type": "defensive",
        },
    }

    castle_wall = {
        "id": 93612350,
        "geometry_type": "way",
        "geometry": closed_geometry(),
        "wall_type": "city_wall",
        "tags": {
            "historic": "castle",
            "barrier": "city_wall",
            "castle_type": "defensive",
        },
    }

    result = AtlasCastleGeometryClassifier.classify(
        castles=[castle],
        castle_walls=[castle_wall],
        debug=False,
    )

    assert len(
        result["independent_castle_walls"]
    ) == 1

    assert (
        result["independent_castle_walls"][0]["id"]
        == 93612350
    )

    assert result["unknown_castles"] == []
