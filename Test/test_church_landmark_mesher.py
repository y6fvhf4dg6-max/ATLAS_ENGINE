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
    assert len(mesh["tower_meshes"]) == 4
    assert mesh["spire_meshes"] == []


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
    assert len(mesh["tower_meshes"]) == 3
    assert mesh["spire_meshes"] == []
    assert len(mesh["roof_meshes"]) == 5


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


def test_landmark_mesher_integrates_architectural_roof_system():
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

    roof_system = mesh["architectural_roof_system"]

    assert roof_system["type"] == "church_roof_system"

    assert tuple(
        section["section_type"]
        for section in roof_system["sections"]
    ) == (
        "outer_aisle_left",
        "outer_aisle_right",
        "main_nave",
        "transept",
        "apse",
    )

    assert mesh["roof_meshes"] == roof_system["sections"]

    assert all(
        triangle in mesh["triangles"]
        for triangle in roof_system["triangles"]
    )


def test_architectural_roofs_replace_flat_box_roof_sections():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert all(
        roof["roof_shape"] in {
            "gable",
            "polygon_pyramid",
        }
        for roof in mesh["roof_meshes"]
    )

    assert not any(
        roof.get("type") == "church_roof_section"
        for roof in mesh["roof_meshes"]
    )


def test_main_and_outer_aisle_roofs_have_distinct_height_levels():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    sections = {
        roof["section_type"]: roof
        for roof in mesh["roof_meshes"]
    }

    left_aisle = sections["outer_aisle_left"]
    right_aisle = sections["outer_aisle_right"]
    main_nave = sections["main_nave"]

    assert left_aisle["ridge_z"] < main_nave["eave_z"]
    assert right_aisle["ridge_z"] < main_nave["eave_z"]
    assert main_nave["ridge_z"] > main_nave["eave_z"]


def test_church_body_has_stepped_outer_aisle_and_main_nave_levels():
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

    body_system = mesh["architectural_body_system"]

    assert body_system["type"] == "church_stepped_body"

    sections = {
        section["section_type"]: section
        for section in body_system["sections"]
    }

    left_aisle = sections["outer_aisle_left"]
    right_aisle = sections["outer_aisle_right"]
    main_nave = sections["main_nave"]

    assert left_aisle["top_z"] < main_nave["top_z"]
    assert right_aisle["top_z"] < main_nave["top_z"]

    roof_sections = {
        section["section_type"]: section
        for section in mesh["roof_meshes"]
    }

    assert (
        roof_sections["outer_aisle_left"]["eave_z"]
        >= left_aisle["top_z"]
    )
    assert (
        roof_sections["outer_aisle_right"]["eave_z"]
        >= right_aisle["top_z"]
    )
    assert (
        roof_sections["main_nave"]["eave_z"]
        >= main_nave["top_z"]
    )


def test_lower_roofs_are_not_buried_inside_full_height_footprint_body():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    roof_sections = {
        section["section_type"]: section
        for section in mesh["roof_meshes"]
    }

    assert (
        mesh["nave_meshes"][0]["max_z"]
        <= roof_sections["outer_aisle_left"]["eave_z"]
    )


def test_landmark_mesher_integrates_architectural_tower_system():
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

    tower_system = mesh["architectural_tower_system"]

    assert tower_system["type"] == "church_tower_system"

    assert tuple(
        tower["tower_type"]
        for tower in tower_system["towers"]
    ) == (
        "crossing_tower",
        "outer_polygon_tower",
        "west_tower_left",
        "west_tower_right",
    )

    assert mesh["tower_meshes"] == tower_system["towers"]


def test_crossing_and_outer_towers_use_polygon_geometry():
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

    towers = {
        tower["tower_type"]: tower
        for tower in mesh["tower_meshes"]
    }

    crossing = towers["crossing_tower"]
    front = towers["outer_polygon_tower"]

    assert crossing["body_shape"] == "polygon"
    assert len(crossing["body_top_ring"]) == 8

    assert front["body_shape"] == "polygon"
    assert len(front["body_top_ring"]) >= 6

    assert crossing["lateral_span"] > front["lateral_span"]


def test_outer_polygon_tower_uses_polygon_spire():
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

    front = next(
        tower
        for tower in mesh["tower_meshes"]
        if tower["tower_type"]
        == "outer_polygon_tower"
    )

    assert front["roof_shape"] == "polygon_spire"
    assert len(front["roof_base_ring"]) >= 6
    assert front["roof_top_z"] > front["body_top_z"]


def test_old_generic_spire_batches_are_replaced():
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

    assert mesh["spire_meshes"] == []
    assert not any(
        tower.get("type") == "church_tower"
        for tower in mesh["tower_meshes"]
    )


def test_landmark_mesher_integrates_tower_window_system():
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

    tower_system = mesh[
        "architectural_tower_system"
    ]

    assert (
        tower_system["window_system_applied"]
        is True
    )

    towers = {
        tower["tower_type"]: tower
        for tower in mesh["tower_meshes"]
    }

    assert len(
        towers["crossing_tower"][
            "window_meshes"
        ]
    ) == 8

    assert len(
        towers["outer_polygon_tower"][
            "window_meshes"
        ]
    ) == 8

    assert len(
        towers["west_tower_left"][
            "window_meshes"
        ]
    ) == 4

    assert len(
        towers["west_tower_right"][
            "window_meshes"
        ]
    ) == 4


def test_tower_window_triangles_are_in_final_church_mesh():
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

    window_triangles = mesh[
        "architectural_tower_system"
    ]["window_triangles"]

    assert window_triangles

    assert all(
        triangle in mesh["triangles"]
        for triangle in window_triangles
    )
