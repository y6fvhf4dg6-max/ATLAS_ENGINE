"""
ATLAS Castle Roof Dispatch Regression Tests

Genel kuralları sabitler:

1. Uzun-dar veya açıkça gabled olarak işaretlenen savunma kuleleri,
   tek merkezli piramit/spire çatısı almamalıdır.

2. Bu kuleler kontrollü biçimde tower_gable çatısına
   yönlendirilmelidir.

3. Çatı yönlendirmesi sonrasında mesh açık kenar veya
   non-manifold kenar üretmemelidir.

4. Düzensiz kule footprint'lerinde minimum döndürülmüş
   dikdörtgen dinamik olarak küçültülmelidir.
"""

import warnings

from shapely.geometry import Polygon

from CORE.atlas_castle_roof_builder import (
    AtlasCastleRoofBuilder,
)
from CORE.atlas_castle_gable_roof_builder import (
    AtlasCastleGableRoofBuilder,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def build_elongated_tower_mesh():
    bottom = [
        (0.0, 0.0, 0.0),
        (4.0, 0.0, 0.0),
        (4.0, 1.5, 0.0),
        (0.0, 1.5, 0.0),
    ]

    top = [
        (0.0, 0.0, 2.0),
        (4.0, 0.0, 2.0),
        (4.0, 1.5, 2.0),
        (0.0, 1.5, 2.0),
    ]

    bottom_triangles = [
        (
            bottom[0],
            bottom[2],
            bottom[1],
        ),
        (
            bottom[0],
            bottom[3],
            bottom[2],
        ),
    ]

    top_triangles = [
        (
            top[0],
            top[1],
            top[2],
        ),
        (
            top[0],
            top[2],
            top[3],
        ),
    ]

    walls = []
    wall_triangles = []

    for index in range(len(bottom)):
        next_index = (index + 1) % len(bottom)

        b1 = bottom[index]
        b2 = bottom[next_index]
        t1 = top[index]
        t2 = top[next_index]

        walls.append(
            (
                b1,
                b2,
                t2,
                t1,
            )
        )

        wall_triangles.extend(
            [
                (
                    b1,
                    b2,
                    t2,
                ),
                (
                    b1,
                    t2,
                    t1,
                ),
            ]
        )

    return {
        "bottom": bottom,
        "top": top,
        "walls": walls,
        "triangles": [
            *bottom_triangles,
            *top_triangles,
            *wall_triangles,
        ],
        "bottom_z": 0.0,
        "top_z": 2.0,
        "castle_roof_profile": "gabled",
    }


def test_elongated_tower_routes_to_gable_and_remains_valid():
    mesh = build_elongated_tower_mesh()

    before_report = AtlasMeshValidator.report(mesh)

    assert before_report["structure_valid"] is True

    assert before_report["open_edge_count"] == 0

    assert before_report["non_manifold_edge_count"] == 0

    assert before_report["valid"] is True

    result = AtlasCastleRoofBuilder.apply(
        mesh=mesh,
        castle_profile=("defensive_tower"),
    )

    assert result.get("castle_roof_applied") is not True

    assert result.get("castle_roof_skipped_for_gable") is True

    result = AtlasCastleGableRoofBuilder.apply(
        mesh=result,
        castle_profile=("defensive_tower"),
    )

    assert result.get("castle_gable_roof_applied") is True

    assert result.get("roof_geometry") == "tower_gable"

    assert result.get("roof_height_mm") is not None

    after_report = AtlasMeshValidator.report(result)

    assert after_report["structure_valid"] is True

    assert after_report["open_edge_count"] == 0

    assert after_report["non_manifold_edge_count"] == 0

    assert after_report["valid"] is True


def test_irregular_tower_gable_rectangle_is_dynamically_reduced():
    ring = [
        (0.0, 0.0, 2.0),
        (4.0, 0.0, 2.0),
        (4.0, 1.0, 2.0),
        (2.5, 1.0, 2.0),
        (2.5, 1.5, 2.0),
        (0.0, 1.5, 2.0),
    ]

    polygon = Polygon(
        [
            (
                point[0],
                point[1],
            )
            for point in ring
        ]
    )

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=(
                "divide by zero encountered "
                "in oriented_envelope"
            ),
            category=RuntimeWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message=(
                "invalid value encountered "
                "in oriented_envelope"
            ),
            category=RuntimeWarning,
        )

        raw_rectangle = (
            polygon.minimum_rotated_rectangle
        )

    reduced_rectangle = AtlasCastleGableRoofBuilder._minimum_rotated_rectangle(
        ring=ring,
        castle_profile=("defensive_tower"),
    )

    assert reduced_rectangle is not None

    assert len(reduced_rectangle) == 4

    reduced_polygon = Polygon(reduced_rectangle)

    assert reduced_polygon.area < raw_rectangle.area

    assert reduced_polygon.area >= polygon.area * 0.70


if __name__ == "__main__":
    test_elongated_tower_routes_to_gable_and_remains_valid()

    test_irregular_tower_gable_rectangle_is_dynamically_reduced()

    print("PASS: " "test_castle_roof_dispatch_regression")
