from math import cos
from math import pi
from math import sin

from CORE.atlas_polygon_triangulator import (
    AtlasPolygonTriangulator,
)


def build_semidisk(
    center=(0.0, 0.0),
    radius=10.0,
    segments=24,
):
    center_x, center_y = center

    points = []

    for index in range(segments + 1):
        angle = pi * index / segments

        points.append(
            (
                center_x + cos(angle) * radius,
                center_y + sin(angle) * radius,
            )
        )

    return points


def polygon_area(points):
    area = 0.0

    for index in range(len(points)):
        x1, y1 = points[index]
        x2, y2 = points[
            (index + 1) % len(points)
        ]

        area += x1 * y2 - x2 * y1

    return abs(area) * 0.5


def triangle_area(triangle):
    point_a, point_b, point_c = triangle

    return abs(
        (
            point_a[0]
            * (
                point_b[1]
                - point_c[1]
            )
            + point_b[0]
            * (
                point_c[1]
                - point_a[1]
            )
            + point_c[0]
            * (
                point_a[1]
                - point_b[1]
            )
        )
        * 0.5
    )


def test_semidisk_triangulates():
    points = build_semidisk()

    triangles = (
        AtlasPolygonTriangulator.triangulate(
            points
        )
    )

    assert triangles
    assert len(triangles) == len(points) - 2


def test_semidisk_triangle_area_matches_polygon():
    points = build_semidisk()

    triangles = (
        AtlasPolygonTriangulator.triangulate(
            points
        )
    )

    expected_area = polygon_area(points)

    triangulated_area = sum(
        triangle_area(triangle)
        for triangle in triangles
    )

    assert abs(
        expected_area - triangulated_area
    ) < 1e-6


def test_semidisk_area_approximates_half_circle():
    radius = 10.0
    points = build_semidisk(
        radius=radius,
        segments=48,
    )

    actual_area = polygon_area(points)
    expected_area = 0.5 * pi * radius * radius

    relative_error = abs(
        actual_area - expected_area
    ) / expected_area

    assert relative_error < 0.01
