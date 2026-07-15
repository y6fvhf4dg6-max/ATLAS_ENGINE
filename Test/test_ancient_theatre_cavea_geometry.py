from math import cos
from math import pi
from math import sin

from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


ARC_SEGMENTS = 32


def _build_semiring(
    inner_radius,
    outer_radius,
):
    outer_arc = []

    for index in range(
        ARC_SEGMENTS + 1
    ):
        angle = (
            pi
            - pi
            * index
            / ARC_SEGMENTS
        )

        outer_arc.append(
            (
                cos(angle) * outer_radius,
                sin(angle) * outer_radius,
            )
        )

    inner_arc = []

    for index in range(
        ARC_SEGMENTS,
        -1,
        -1,
    ):
        angle = (
            pi
            - pi
            * index
            / ARC_SEGMENTS
        )

        inner_arc.append(
            (
                cos(angle) * inner_radius,
                sin(angle) * inner_radius,
            )
        )

    return outer_arc + inner_arc


def test_cavea_semiring_is_created():
    points = _build_semiring(
        inner_radius=16.824,
        outer_radius=47.108,
    )

    assert len(points) == 66
    assert len(set(points)) == 66


def test_cavea_semiring_triangulates():
    points = _build_semiring(
        inner_radius=16.824,
        outer_radius=47.108,
    )

    triangles = (
        AtlasPolygonTriangulator.triangulate(
            points
        )
    )

    assert triangles
    assert len(triangles) > 32


def test_cavea_semiring_preserves_inner_opening():
    points = _build_semiring(
        inner_radius=16.824,
        outer_radius=47.108,
    )

    radii = [
        (
            point[0] ** 2
            + point[1] ** 2
        ) ** 0.5
        for point in points
    ]

    assert min(radii) > 16.823
    assert max(radii) < 47.109
