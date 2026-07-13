"""
ATLAS Geometry Simplifier Regression Tests

Gerçek kollinear noktaların kaldırılmasını, fakat bina footprint
köşelerinin ve girintilerinin korunmasını doğrular.
"""

from CORE.atlas_geometry_simplifier import AtlasGeometrySimplifier


def test_consecutive_duplicate_points_are_removed():
    points = [
        (0.0, 0.0),
        (0.0, 0.0),
        (0.0, 2.0),
        (2.0, 2.0),
        (2.0, 0.0),
    ]

    result = AtlasGeometrySimplifier.remove_duplicate_points(points)

    assert result == [
        (0.0, 0.0),
        (0.0, 2.0),
        (2.0, 2.0),
        (2.0, 0.0),
    ]


def test_closing_duplicate_point_is_removed():
    points = [
        (0.0, 0.0),
        (0.0, 2.0),
        (2.0, 2.0),
        (2.0, 0.0),
        (0.0, 0.0),
    ]

    result = AtlasGeometrySimplifier.remove_duplicate_points(points)

    assert len(result) == 4
    assert result[0] != result[-1]


def test_true_collinear_middle_point_is_removed():
    points = [
        (0.0, 0.0),
        (0.0, 1.0),
        (0.0, 2.0),
        (2.0, 2.0),
        (2.0, 0.0),
    ]

    result = AtlasGeometrySimplifier.remove_collinear_points(
        points,
        tolerance=0.0,
    )

    assert (0.0, 1.0) not in result
    assert len(result) == 4


def test_l_shaped_footprint_keeps_all_real_corners():
    points = [
        (0.0, 0.0),
        (0.0, 3.0),
        (1.0, 3.0),
        (1.0, 1.0),
        (3.0, 1.0),
        (3.0, 0.0),
    ]

    result = AtlasGeometrySimplifier.simplify(points)

    assert result == points
    assert len(result) == 6


def test_small_but_real_notch_is_preserved():
    points = [
        (39.0000000, 32.0000000),
        (39.0000000, 32.0003000),
        (39.0000100, 32.0003000),
        (39.0000100, 32.0001800),
        (39.0000200, 32.0001800),
        (39.0000200, 32.0000000),
    ]

    result = AtlasGeometrySimplifier.simplify(points)

    assert len(result) == 6
    assert result == points


def test_anitkabir_complex_footprint_is_not_over_simplified():
    points = [
        (39.9253661, 32.8367842),
        (39.9256283, 32.8372264),
        (39.9255856, 32.8372687),
        (39.9255512, 32.8373028),
        (39.9255479, 32.8373063),
        (39.9255445, 32.8373098),
        (39.9255410, 32.8373135),
        (39.9255372, 32.8373175),
        (39.9255337, 32.8373212),
        (39.9255301, 32.8373250),
        (39.9255265, 32.8373287),
        (39.9255228, 32.8373326),
        (39.9255194, 32.8373362),
        (39.9255162, 32.8373395),
        (39.9255131, 32.8373428),
        (39.9254833, 32.8373725),
        (39.9254599, 32.8373991),
        (39.9255135, 32.8374869),
        (39.9257814, 32.8372086),
        (39.9257200, 32.8371080),
        (39.9255262, 32.8367903),
        (39.9254615, 32.8366848),
        (39.9254573, 32.8366892),
    ]

    result = AtlasGeometrySimplifier.simplify(points)

    assert len(result) >= 20
    assert AtlasGeometrySimplifier.has_self_intersection(result) is False
