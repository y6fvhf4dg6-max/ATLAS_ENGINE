from collections import Counter

import pytest

from CORE.atlas_church_landmark_builder import (
    AtlasChurchLandmarkBuilder,
)
from CORE.atlas_church_landmark_mesher import (
    AtlasChurchLandmarkMesher,
)
from CORE.atlas_church_landmark_profile import (
    AtlasChurchLandmarkProfile,
)
from CORE.atlas_landmark import AtlasLandmark
from CORE.atlas_landmark_type import AtlasLandmarkType


def _landmark(
    *,
    landmark_type=AtlasLandmarkType.CHURCH,
):
    return AtlasLandmark(
        id=601,
        landmark_type=landmark_type,
        geometry=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 40.0),
            (0.0, 40.0),
        ),
        tags={},
        source="OSM",
    )


def _topology(triangles):
    counts = Counter()

    def key(point):
        return tuple(round(float(value), 8) for value in point)

    for first, second, third in triangles:
        for a, b in (
            (first, second),
            (second, third),
            (third, first),
        ):
            counts[tuple(sorted((key(a), key(b))))] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in counts.values()
        ),
    }


def test_mesher_builds_closed_church_mesh():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert mesh["type"] == "church_landmark"
    assert mesh["landmark_id"] == 601
    assert mesh["landmark_class"] == "church"
    assert len(mesh["triangles"]) > 0

    topology = _topology(
        mesh["triangles"]
    )

    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0


def test_cathedral_mesh_contains_twin_tower_components():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            tower_count=2,
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert mesh["landmark_class"] == "cathedral"
    assert len(mesh["tower_meshes"]) == 2
    assert len(mesh["spire_meshes"]) == 2


def test_mesher_preserves_component_batches():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert len(mesh["nave_meshes"]) == 1
    assert len(mesh["transept_meshes"]) == 1
    assert len(mesh["apse_meshes"]) == 1
    assert len(mesh["tower_meshes"]) == 1
    assert len(mesh["spire_meshes"]) == 1
    assert len(mesh["roof_meshes"]) == 4


def test_mesher_rejects_wrong_geometry_type():
    try:
        AtlasChurchLandmarkMesher.build(
            object()
        )
    except TypeError as exc:
        assert "AtlasChurchLandmarkGeometry" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid geometry type to be rejected"
        )


def test_mesher_follows_rotated_church_footprint_axis():
    import math

    angle = math.radians(32.0)
    center_x = 15.0
    center_y = -8.0
    half_lateral = 10.0
    half_longitudinal = 25.0

    def world(longitudinal, lateral):
        axis_x = -math.sin(angle)
        axis_y = math.cos(angle)
        normal_x = -axis_y
        normal_y = axis_x

        return (
            center_x
            + longitudinal * axis_x
            + lateral * normal_x,
            center_y
            + longitudinal * axis_y
            + lateral * normal_y,
        )

    footprint = (
        world(-half_longitudinal, -half_lateral),
        world(-half_longitudinal, half_lateral),
        world(half_longitudinal, half_lateral),
        world(half_longitudinal, -half_lateral),
    )

    landmark = AtlasLandmark(
        id=603,
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=footprint,
        tags={},
        source="OSM",
    )

    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    nave_points = tuple(
        point
        for triangle in mesh["nave_meshes"][0]["triangles"]
        for point in triangle
    )

    xs = tuple(point[0] for point in nave_points)
    ys = tuple(point[1] for point in nave_points)

    world_x_span = max(xs) - min(xs)
    world_y_span = max(ys) - min(ys)

    assert world_y_span > world_x_span


def test_mesher_reports_resolved_footprint_frame():
    landmark = AtlasLandmark(
        id=604,
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (20.0, 10.0),
            (0.0, 50.0),
            (-20.0, 40.0),
        ),
        tags={},
        source="OSM",
    )

    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    frame = mesh["footprint_frame"]

    assert frame.longitudinal_span > frame.lateral_span
    assert abs(frame.axis_x) > 0.0
    assert abs(frame.axis_y) > 0.0


def _triangle_xy_area(triangle):
    (ax, ay, _), (bx, by, _), (cx, cy, _) = triangle

    return abs(
        (
            ax * (by - cy)
            + bx * (cy - ay)
            + cx * (ay - by)
        )
        / 2.0
    )


def test_nave_base_uses_real_irregular_footprint_area():
    landmark = AtlasLandmark(
        id=605,
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (8.0, 0.0),
            (8.0, 8.0),
            (14.0, 8.0),
            (14.0, 18.0),
            (8.0, 18.0),
            (8.0, 30.0),
            (0.0, 30.0),
            (0.0, 18.0),
            (-6.0, 18.0),
            (-6.0, 8.0),
            (0.0, 8.0),
        ),
        tags={},
        source="OSM",
    )

    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    nave = mesh["nave_meshes"][0]

    assert nave["uses_real_footprint"] is True
    assert nave["footprint"] == geometry.footprint

    base_triangles = tuple(
        triangle
        for triangle in nave["triangles"]
        if all(
            point[2] == 0.0
            for point in triangle
        )
    )

    base_area = sum(
        _triangle_xy_area(triangle)
        for triangle in base_triangles
    )

    assert base_area == pytest.approx(
        360.0,
        abs=1e-8,
    )


def test_real_footprint_nave_preserves_concave_outline_vertices():
    landmark = AtlasLandmark(
        id=606,
        landmark_type=AtlasLandmarkType.CHURCH,
        geometry=(
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (6.0, 10.0),
            (6.0, 20.0),
            (0.0, 20.0),
        ),
        tags={},
        source="OSM",
    )

    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=landmark,
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    nave = mesh["nave_meshes"][0]

    base_vertices = {
        (round(x, 8), round(y, 8))
        for triangle in nave["triangles"]
        for x, y, z in triangle
        if z == 0.0
    }

    expected_vertices = {
        (round(x, 8), round(y, 8))
        for x, y in geometry.footprint
    }

    assert expected_vertices.issubset(
        base_vertices
    )
