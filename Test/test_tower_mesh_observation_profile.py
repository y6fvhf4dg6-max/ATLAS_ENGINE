from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_tower_builder import AtlasTowerGeometry


def _observation_geometry():
    return AtlasTowerGeometry(
        footprint=(
            (0.0, 0.0),
            (2.0, 0.0),
            (2.0, 2.0),
            (0.0, 2.0),
        ),
        height_m=100.0,
        profile="observation",
    )


def test_observation_profile_creates_multi_ring_mesh():
    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    # Generic extrusion = 4 wall quads.
    # Observation profile must create multiple stacked rings.
    assert len(mesh["walls"]) > 4

    # Observation profile should also generate
    # substantially more triangles than a simple extrusion.
    assert len(mesh["triangles"]) > 40


def test_observation_profile_uses_prismatic_body_ring():
    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    body_ring = mesh["rings"][1]

    xs = tuple(point[0] for point in body_ring)
    ys = tuple(point[1] for point in body_ring)

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)

    # Every point of a square/prismatic perimeter lies on
    # at least one bounding-box edge. Circular rings do not.
    tolerance = 1e-9

    assert all(
        abs(x - min_x) <= tolerance
        or abs(x - max_x) <= tolerance
        or abs(y - min_y) <= tolerance
        or abs(y - max_y) <= tolerance
        for x, y, _z in body_ring
    )


def test_observation_profile_has_no_duplicate_ring_vertices():
    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    for ring in mesh["rings"]:
        assert len(set(ring)) == len(ring)


def _triangle_area(triangle):
    import math

    a, b, c = triangle

    ab = (
        b[0] - a[0],
        b[1] - a[1],
        b[2] - a[2],
    )
    ac = (
        c[0] - a[0],
        c[1] - a[1],
        c[2] - a[2],
    )

    cross = (
        ab[1] * ac[2] - ab[2] * ac[1],
        ab[2] * ac[0] - ab[0] * ac[2],
        ab[0] * ac[1] - ab[1] * ac[0],
    )

    return 0.5 * math.sqrt(
        sum(value * value for value in cross)
    )


def test_observation_profile_has_no_degenerate_triangles():
    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    assert all(
        _triangle_area(triangle) > 1e-12
        for triangle in mesh["triangles"]
    )


def test_observation_body_and_platform_rings_share_angular_indexing():
    import math

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    body_ring = mesh["rings"][1]
    first_platform_ring = mesh["rings"][2]

    center_x = sum(point[0] for point in body_ring) / len(body_ring)
    center_y = sum(point[1] for point in body_ring) / len(body_ring)

    for body_point, platform_point in zip(
        body_ring,
        first_platform_ring,
    ):
        body_angle = math.atan2(
            body_point[1] - center_y,
            body_point[0] - center_x,
        )
        platform_angle = math.atan2(
            platform_point[1] - center_y,
            platform_point[0] - center_x,
        )

        angle_delta = math.atan2(
            math.sin(body_angle - platform_angle),
            math.cos(body_angle - platform_angle),
        )

        assert abs(angle_delta) < 1e-9


def test_observation_profile_uses_layered_atakule_like_proportions():
    import math

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    rings = mesh["rings"]

    assert len(rings) == 12

    center_x = 1.0
    center_y = 1.0

    radii = tuple(
        sum(
            math.hypot(
                x - center_x,
                y - center_y,
            )
            for x, y, _z in ring
        )
        / len(ring)
        for ring in rings
    )

    z_levels = tuple(
        sum(point[2] for point in ring) / len(ring)
        for ring in rings
    )

    import pytest

    assert z_levels == pytest.approx(
        (
            0.0,
            58.0,
            62.0,
            66.0,
            70.0,
            73.0,
            77.0,
            80.0,
            88.0,
            92.0,
            97.0,
            100.0,
        )
    )

    # Alt seyir katı yatay ve sabit genişlikte olmalı.
    assert radii[3] == radii[4]

    # Ara balkon da dikey cephe oluşturmalı.
    assert radii[5] == radii[6]

    # Ana platform geniş fakat yassı olmalı.
    assert radii[7] == radii[8]
    assert radii[7] > radii[5]

    # Kubbe ana platformdan kademeli biçimde daralmalı.
    assert radii[9] < radii[8]
    assert radii[10] < radii[9]
    assert radii[11] < radii[10]


def test_observation_profile_keeps_body_narrower_than_main_platform():
    import math

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    rings = mesh["rings"]
    center_x = 1.0
    center_y = 1.0

    def mean_radius(ring):
        return sum(
            math.hypot(
                x - center_x,
                y - center_y,
            )
            for x, y, _z in ring
        ) / len(ring)

    body_radius = mean_radius(rings[1])
    main_platform_radius = mean_radius(rings[7])

    assert body_radius / main_platform_radius < 0.45


def test_observation_profile_narrows_near_circular_tower_body():
    import math

    footprint = tuple(
        (
            math.cos(2.0 * math.pi * index / 16),
            math.sin(2.0 * math.pi * index / 16),
        )
        for index in range(16)
    )

    geometry = AtlasTowerGeometry(
        footprint=footprint,
        height_m=100.0,
        profile="observation",
    )

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        geometry
    )

    rings = mesh["rings"]

    def mean_radius(ring):
        return sum(
            math.hypot(x, y)
            for x, y, _z in ring
        ) / len(ring)

    body_radius = mean_radius(rings[1])
    main_platform_radius = mean_radius(rings[7])

    assert body_radius / main_platform_radius < 0.45


def test_observation_dome_is_flattened_and_ends_in_narrow_cap():
    import math

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        _observation_geometry()
    )

    rings = mesh["rings"]
    center_x = 1.0
    center_y = 1.0

    def mean_radius(ring):
        return sum(
            math.hypot(
                x - center_x,
                y - center_y,
            )
            for x, y, _z in ring
        ) / len(ring)

    def mean_z(ring):
        return sum(
            point[2]
            for point in ring
        ) / len(ring)

    main_platform_radius = mean_radius(rings[8])
    top_radius = mean_radius(rings[-1])

    dome_height = (
        mean_z(rings[-1])
        - mean_z(rings[8])
    )

    assert dome_height <= 12.0
    assert top_radius / main_platform_radius < 0.30
