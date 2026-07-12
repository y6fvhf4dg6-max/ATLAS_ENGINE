"""
ATLAS Castle Roof Boundary Topology Regression Test

Çatı ring'indeki kollinear ara noktaların silinerek bina gövdesiyle
farklı boundary segmentasyonu oluşturmasını engeller.

Eski hatalı davranış:

    body boundary : A-B, B-C
    roof boundary : A-C

Bu durum üç açık kenarlı bir T-junction üretiyordu.
Çatı ve gövde aynı boundary noktalarını korumalıdır.

Fixture kareye yakın tutulur; böylece uzun-dar kuleler için kullanılan
gable-dispatch kuralı devreye girmez ve spire topolojisi doğrudan test edilir.
"""

from CORE.atlas_castle_roof_builder import (
    AtlasCastleRoofBuilder,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def build_collinear_boundary_tower_mesh():
    bottom = [
        (0.0, 0.0, 0.0),
        (0.5, 0.0, 0.0),  # A-C doğrusu üzerindeki ara nokta
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
    ]

    top = [
        (0.0, 0.0, 1.0),
        (0.5, 0.0, 1.0),  # Gövde ve çatı tarafından korunmalıdır
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 1.0),
        (0.0, 1.0, 1.0),
    ]

    bottom_triangles = [
        (
            bottom[0],
            bottom[1],
            bottom[4],
        ),
        (
            bottom[1],
            bottom[2],
            bottom[4],
        ),
        (
            bottom[2],
            bottom[3],
            bottom[4],
        ),
    ]

    top_triangles = [
        (
            top[0],
            top[4],
            top[1],
        ),
        (
            top[1],
            top[4],
            top[2],
        ),
        (
            top[2],
            top[4],
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
        "top_z": 1.0,
        "castle_roof_profile": "hipped",
    }


def test_castle_roof_preserves_collinear_boundary_segmentation():
    mesh = build_collinear_boundary_tower_mesh()

    before_report = AtlasMeshValidator.report(mesh)

    assert before_report["open_edge_count"] == 0

    assert before_report["non_manifold_edge_count"] == 0

    result = AtlasCastleRoofBuilder.apply(
        mesh=mesh,
        castle_profile=("defensive_tower"),
    )

    after_report = AtlasMeshValidator.report(result)

    assert result["castle_roof_applied"] is True

    assert result["roof_ring_point_count"] == 5

    assert len(result["roof_triangles"]) == 5

    assert after_report["open_edge_count"] == 0

    assert after_report["non_manifold_edge_count"] == 0

    assert after_report["valid"] is True


if __name__ == "__main__":
    test_castle_roof_preserves_collinear_boundary_segmentation()

    print("PASS: " "test_castle_roof_preserves_collinear_boundary_segmentation")
