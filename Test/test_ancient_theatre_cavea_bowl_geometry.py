from math import cos
from math import pi
from math import sin

from CORE.atlas_ancient_theatre_cavea_profile import (
    AtlasAncientTheatreCaveaProfile,
)


ARC_SEGMENTS = 32
RADIAL_SEGMENTS = 8

INNER_RADIUS_M = 16.824
OUTER_RADIUS_M = 47.108
CAVEA_RISE_M = 12.0


def _build_bowl_grid():
    rings = []

    for radial_index in range(
        RADIAL_SEGMENTS + 1
    ):
        radial_ratio = (
            radial_index
            / RADIAL_SEGMENTS
        )

        radius = (
            INNER_RADIUS_M
            + (
                OUTER_RADIUS_M
                - INNER_RADIUS_M
            )
            * radial_ratio
        )

        height = (
            AtlasAncientTheatreCaveaProfile
            .height_at_radius(
                radius=radius,
                inner_radius=INNER_RADIUS_M,
                outer_radius=OUTER_RADIUS_M,
                rise=CAVEA_RISE_M,
            )
        )

        ring = []

        for arc_index in range(
            ARC_SEGMENTS + 1
        ):
            angle = (
                pi
                - pi
                * arc_index
                / ARC_SEGMENTS
            )

            ring.append(
                (
                    cos(angle) * radius,
                    sin(angle) * radius,
                    height,
                )
            )

        rings.append(ring)

    return rings


def _build_surface_triangles(rings):
    triangles = []

    for radial_index in range(
        RADIAL_SEGMENTS
    ):
        inner_ring = rings[radial_index]
        outer_ring = rings[
            radial_index + 1
        ]

        for arc_index in range(
            ARC_SEGMENTS
        ):
            inner_1 = inner_ring[arc_index]
            inner_2 = inner_ring[
                arc_index + 1
            ]
            outer_1 = outer_ring[arc_index]
            outer_2 = outer_ring[
                arc_index + 1
            ]

            triangles.append(
                (
                    inner_1,
                    outer_1,
                    outer_2,
                )
            )

            triangles.append(
                (
                    inner_1,
                    outer_2,
                    inner_2,
                )
            )

    return triangles


def test_cavea_bowl_grid_dimensions():
    rings = _build_bowl_grid()

    assert len(rings) == (
        RADIAL_SEGMENTS + 1
    )

    assert all(
        len(ring) == ARC_SEGMENTS + 1
        for ring in rings
    )


def test_cavea_bowl_height_rises_outward():
    rings = _build_bowl_grid()

    heights = [
        ring[0][2]
        for ring in rings
    ]

    assert heights == sorted(heights)
    assert heights[0] == 0.0
    assert heights[-1] == CAVEA_RISE_M


def test_cavea_bowl_surface_triangle_count():
    rings = _build_bowl_grid()

    triangles = _build_surface_triangles(
        rings
    )

    assert len(triangles) == (
        RADIAL_SEGMENTS
        * ARC_SEGMENTS
        * 2
    )


def test_cavea_bowl_has_vertical_cut_endpoints():
    rings = _build_bowl_grid()

    left_cut = [
        ring[0]
        for ring in rings
    ]

    right_cut = [
        ring[-1]
        for ring in rings
    ]

    assert all(
        abs(point[1]) < 1e-9
        for point in left_cut
    )

    assert all(
        abs(point[1]) < 1e-9
        for point in right_cut
    )

    assert left_cut[0][2] == 0.0
    assert left_cut[-1][2] == CAVEA_RISE_M
    assert right_cut[0][2] == 0.0
    assert right_cut[-1][2] == CAVEA_RISE_M
