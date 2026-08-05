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
    assert len(mesh["tower_meshes"]) == 1
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
            grammar_name="bonn_muenster_catalog",
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
            grammar_name="bonn_muenster_catalog",
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
            grammar_name="bonn_muenster_catalog",
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


def test_profile_can_disable_apse_without_landmark_id_special_case():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            has_apse=False,
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    assert mesh["apse_meshes"] == []
    assert all(
        roof["section_type"] != "apse"
        for roof in mesh["roof_meshes"]
    )

def test_romanesque_semantic_profile_drives_stepped_pitched_roof_character():
    generic_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="twin_west_towers",
            profile_name="generic_church",
            tower_count=2,
        ),
    )
    romanesque_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="bonn_muenster_catalog",
            profile_name="romanesque_cathedral",
            tower_count=2,
        ),
    )

    generic_mesh = AtlasChurchLandmarkMesher.build(
        generic_geometry
    )
    romanesque_mesh = AtlasChurchLandmarkMesher.build(
        romanesque_geometry
    )

    generic_sections = {
        section["section_type"]: section
        for section in generic_mesh["roof_meshes"]
    }
    romanesque_sections = {
        section["section_type"]: section
        for section in romanesque_mesh["roof_meshes"]
    }

    assert (
        romanesque_sections["outer_aisle_left"]["eave_z"]
        < generic_sections["outer_aisle_left"]["eave_z"]
    )
    assert (
        romanesque_sections["outer_aisle_left"]["ridge_z"]
        == generic_sections["outer_aisle_left"]["ridge_z"]
    )
    assert (
        romanesque_sections["main_nave"]["ridge_z"]
        > generic_sections["main_nave"]["ridge_z"]
    )

def test_basilica_cross_plan_drives_church_body_proportions():
    generic_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="twin_west_towers",
            profile_name="generic_church",
            tower_count=2,
        ),
    )
    basilica_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="bonn_muenster_catalog",
            profile_name="romanesque_cathedral",
            tower_count=2,
        ),
    )

    generic_mesh = AtlasChurchLandmarkMesher.build(
        generic_geometry
    )
    basilica_mesh = AtlasChurchLandmarkMesher.build(
        basilica_geometry
    )

    generic_body = generic_mesh[
        "architectural_body_system"
    ]
    basilica_body = basilica_mesh[
        "architectural_body_system"
    ]

    generic_main = next(
        section
        for section in generic_body["sections"]
        if section["section_type"] == "main_nave"
    )
    basilica_main = next(
        section
        for section in basilica_body["sections"]
        if section["section_type"] == "main_nave"
    )

    generic_aisle = next(
        section
        for section in generic_body["sections"]
        if section["section_type"] == "outer_aisle_left"
    )
    basilica_aisle = next(
        section
        for section in basilica_body["sections"]
        if section["section_type"] == "outer_aisle_left"
    )

    from CORE.atlas_church_footprint_resolver import (
        AtlasChurchFootprintResolver,
    )

    def mesh_spans(mesh, geometry):
        frame = AtlasChurchFootprintResolver.resolve(
            geometry.footprint
        )

        local_points = tuple(
            frame.to_local(vertex)
            for triangle in mesh["triangles"]
            for vertex in triangle
        )

        longitudinal_values = tuple(
            point[0]
            for point in local_points
        )
        lateral_values = tuple(
            point[1]
            for point in local_points
        )

        return (
            max(longitudinal_values)
            - min(longitudinal_values),
            max(lateral_values)
            - min(lateral_values),
        )

    generic_nave_depth, generic_nave_width = mesh_spans(
        generic_main["mesh"],
        generic_geometry,
    )
    basilica_nave_depth, basilica_nave_width = mesh_spans(
        basilica_main["mesh"],
        basilica_geometry,
    )

    generic_transept_depth, generic_transept_width = mesh_spans(
        generic_mesh["transept_meshes"][0],
        generic_geometry,
    )
    basilica_transept_depth, basilica_transept_width = mesh_spans(
        basilica_mesh["transept_meshes"][0],
        basilica_geometry,
    )

    assert basilica_nave_width < generic_nave_width
    assert basilica_nave_depth > generic_nave_depth
    assert basilica_aisle["top_z"] < generic_aisle["top_z"]

    assert basilica_transept_width > generic_transept_width
    assert basilica_transept_depth > generic_transept_depth

def test_semantic_facade_rhythm_drives_church_facade_geometry():
    generic_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="church",
            grammar_name="single_west_tower",
            profile_name="generic_church",
        ),
    )
    romanesque_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="church",
            grammar_name="single_west_tower",
            profile_name="romanesque_cathedral",
        ),
    )

    generic_mesh = AtlasChurchLandmarkMesher.build(
        generic_geometry
    )
    romanesque_mesh = AtlasChurchLandmarkMesher.build(
        romanesque_geometry
    )

    generic_facade = generic_mesh[
        "architectural_facade_system"
    ]
    romanesque_facade = romanesque_mesh[
        "architectural_facade_system"
    ]

    assert generic_facade["facade_rhythm"] == "regular"
    assert (
        romanesque_facade["facade_rhythm"]
        == "heavy_round_arch"
    )
    assert (
        generic_facade["panel_count"]
        > romanesque_facade["panel_count"]
    )
    assert (
        romanesque_facade["arch_shape"]
        == "round_arch"
    )
    assert len(
        romanesque_mesh["facade_meshes"]
    ) == romanesque_facade["panel_count"]

    facade_roles = {
        mesh["architectural_role"]
        for mesh in romanesque_mesh["facade_meshes"]
    }

    assert facade_roles == {
        "church_main_nave_facade_bay",
        "church_front_facade_opening",
        "church_front_facade_oculus",
        "church_rear_facade_opening",
    }

    assert {
        mesh["facade_side"]
        for mesh in romanesque_mesh["facade_meshes"]
    } == {
        "left",
        "right",
        "front",
        "rear",
    }

def test_window_bay_physical_decision_controls_landmark_facade_output():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="church",
            grammar_name="single_west_tower",
            profile_name="generic_church",
            scale_ratio=50000.0,
            nozzle_diameter_mm=0.4,
        ),
    )

    window_component = next(
        component
        for component in geometry.components
        if component.component_type
        == "window_bay_system"
    )

    assert window_component.physical_action == "omit"
    assert window_component.resolved_size_mm == 0.0

    result = AtlasChurchLandmarkMesher.build(
        geometry
    )

    facade = result[
        "architectural_facade_system"
    ]

    assert facade["window_action"] == "omit"
    assert facade["window_resolved_size_mm"] == 0.0
    assert facade["panel_count"] == 0
    assert result["facade_meshes"] == []

def test_semantic_profile_routes_front_and_rear_facade_compositions():
    generic_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="church",
            grammar_name="single_west_tower",
            profile_name="generic_church",
        ),
    )
    romanesque_geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="church",
            grammar_name="single_west_tower",
            profile_name="romanesque_cathedral",
        ),
    )

    generic = AtlasChurchLandmarkMesher.build(
        generic_geometry
    )["architectural_facade_system"]
    romanesque = AtlasChurchLandmarkMesher.build(
        romanesque_geometry
    )["architectural_facade_system"]

    assert (
        generic["front_composition"]
        == "single_arch_portal"
    )
    assert (
        generic["rear_composition"]
        == "single_arch_opening"
    )
    assert (
        romanesque["front_composition"]
        == "portal_with_oculus"
    )
    assert (
        romanesque["rear_composition"]
        == "round_arch_opening"
    )

    romanesque_front = next(
        facade
        for facade in romanesque["end_facades"]
        if facade["facade_side"] == "front"
    )

    assert (
        romanesque_front["facade_composition"]
        == "portal_with_oculus"
    )



def test_outer_aisle_body_is_split_into_real_footprint_regions():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    aisle_meshes = mesh[
        "outer_aisle_meshes"
    ]

    assert len(aisle_meshes) >= 2
    assert {
        aisle["section_type"]
        for aisle in aisle_meshes
    } == {
        "outer_aisle_left",
        "outer_aisle_right",
    }
    assert any(
        aisle["section_type"]
        == "outer_aisle_left"
        for aisle in aisle_meshes
    )
    assert any(
        aisle["section_type"]
        == "outer_aisle_right"
        for aisle in aisle_meshes
    )
    assert all(
        aisle["uses_real_footprint"] is True
        for aisle in aisle_meshes
    )


def test_outer_aisle_regions_leave_main_nave_corridor_uncovered():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    frame = mesh["footprint_frame"]
    aisle_meshes = mesh[
        "outer_aisle_meshes"
    ]

    local_lateral_values = {
        "outer_aisle_left": [],
        "outer_aisle_right": [],
    }

    for aisle in aisle_meshes:
        local_lateral_values[
            aisle["section_type"]
        ].extend(
            frame.to_local(point)[1]
            for point in aisle["footprint"]
        )

    left_values = local_lateral_values[
        "outer_aisle_left"
    ]
    right_values = local_lateral_values[
        "outer_aisle_right"
    ]

    left_min = min(left_values)
    left_max = max(left_values)
    right_min = min(right_values)
    right_max = max(right_values)

    assert left_max < 0.0
    assert right_min > 0.0
    assert left_min < left_max
    assert right_min < right_max


def test_outer_aisle_clipping_preserves_expected_rectangular_area():
    from shapely.geometry import Polygon

    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    aisle_area = sum(
        Polygon(
            aisle["footprint"]
        ).area
        for aisle in mesh[
            "outer_aisle_meshes"
        ]
    )

    footprint_area = Polygon(
        geometry.footprint
    ).area

    expected_main_nave_area = (
        mesh["architectural_facade_system"][
            "main_nave_width"
        ]
        * mesh["footprint_frame"].longitudinal_span
    )

    assert aisle_area == pytest.approx(
        footprint_area
        - expected_main_nave_area,
        abs=1e-8,
    )


def test_concave_outer_aisle_regions_stay_inside_real_footprint():
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    landmark = AtlasLandmark(
        id=607,
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

    source_polygon = Polygon(
        geometry.footprint
    )
    aisle_union = unary_union(
        [
            Polygon(aisle["footprint"])
            for aisle in mesh[
                "outer_aisle_meshes"
            ]
        ]
    )

    assert aisle_union.difference(
        source_polygon
    ).area == pytest.approx(
        0.0,
        abs=1e-8,
    )
    assert aisle_union.area > 0.0


def test_outer_aisle_components_preserve_side_identity():
    landmark = AtlasLandmark(
        id=608,
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

    aisle_meshes = mesh[
        "outer_aisle_meshes"
    ]

    assert all(
        aisle["section_type"] in {
            "outer_aisle_left",
            "outer_aisle_right",
        }
        for aisle in aisle_meshes
    )

    component_indices = {}

    for aisle in aisle_meshes:
        component_indices.setdefault(
            aisle["section_type"],
            [],
        ).append(
            aisle["component_index"]
        )

    assert all(
        sorted(indices)
        == list(range(len(indices)))
        for indices in component_indices.values()
    )

def test_landmark_routes_side_facades_above_outer_aisles():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            profile_name="romanesque_cathedral",
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    body_sections = {
        section["section_type"]: section
        for section in mesh[
            "architectural_body_system"
        ]["sections"]
    }

    outer_aisle_top_z = max(
        body_sections["outer_aisle_left"]["top_z"],
        body_sections["outer_aisle_right"]["top_z"],
    )

    facade = mesh[
        "architectural_facade_system"
    ]

    side_panels = [
        panel
        for side_facade in facade["side_facades"]
        for panel in side_facade["component_meshes"]
    ]

    assert facade["side_wall_min_z"] == (
        outer_aisle_top_z
    )
    assert facade["side_surface_target"] == (
        "visible_clerestory_band"
    )

    assert side_panels

    assert all(
        panel["surface_target"]
        == "visible_clerestory_band"
        for panel in side_panels
    )

    assert min(
        vertex[2]
        for panel in side_panels
        for vertex in (
            *panel["back"],
            *panel["front"],
        )
    ) >= outer_aisle_top_z

def test_landmark_integrates_single_west_tower_window_stage():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            grammar_name="single_west_tower",
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    tower_system = mesh[
        "architectural_tower_system"
    ]

    assert len(
        mesh["tower_window_meshes"]
    ) == 4

    assert (
        tower_system["window_meshes"]
        == mesh["tower_window_meshes"]
    )

    tower = tower_system["towers"][0]

    assert (
        tower["tower_type"]
        == "west_tower_center"
    )
    assert (
        tower["window_stage"]["type"]
        == "bell_stage"
    )
    assert (
        tower["window_stage"]["window_count"]
        == 4
    )
    assert len(tower["window_meshes"]) == 4


def test_bonn_tower_windows_are_included_in_final_landmark_triangles():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="bonn_muenster_catalog",
            profile_name="romanesque_cathedral",
            tower_count=2,
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    tower_system = mesh[
        "architectural_tower_system"
    ]
    window_meshes = mesh[
        "tower_window_meshes"
    ]

    assert len(window_meshes) == 24

    assert {
        tower["tower_type"]:
        tower["window_stage"]["window_count"]
        for tower in tower_system["towers"]
    } == {
        "crossing_tower": 8,
        "outer_polygon_tower": 8,
        "west_tower_left": 4,
        "west_tower_right": 4,
    }

    final_triangles = set(
        mesh["triangles"]
    )

    assert all(
        triangle in final_triangles
        for window in window_meshes
        for triangle in window["triangles"]
    )

def test_single_west_tower_routes_front_details_to_tower_face():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(),
        profile=AtlasChurchLandmarkProfile(
            grammar_name="single_west_tower",
            profile_name="romanesque_cathedral",
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    facade = mesh[
        "architectural_facade_system"
    ]
    tower = next(
        tower
        for tower in mesh["tower_meshes"]
        if tower["tower_type"]
        == "west_tower_center"
    )

    front = next(
        item
        for item in facade["end_facades"]
        if item["facade_side"] == "front"
    )
    oculus = facade["oculus_meshes"][0]

    assert facade["front_surface_target"] == (
        "west_tower_center_front"
    )
    assert front["surface_target"] == (
        "west_tower_center_front"
    )
    assert oculus["surface_target"] == (
        "west_tower_center_front"
    )

    frame = mesh["footprint_frame"]

    tower_front_longitudinal = (
        tower["center_longitudinal"]
        - tower["longitudinal_span"] / 2.0
    )
    nave_front_longitudinal = (
        -facade["main_nave_depth"] / 2.0
    )

    portal = front["component_meshes"][0]

    portal_longitudinal = sum(
        frame.to_local(
            (point[0], point[1])
        )[0]
        for point in portal["back"]
    ) / len(portal["back"])

    oculus_longitudinal = frame.to_local(
        (
            oculus["center"][0],
            oculus["center"][1],
        )
    )[0]

    assert abs(
        portal_longitudinal
        - tower_front_longitudinal
    ) < abs(
        portal_longitudinal
        - nave_front_longitudinal
    )

    assert abs(
        oculus_longitudinal
        - tower_front_longitudinal
    ) < abs(
        oculus_longitudinal
        - nave_front_longitudinal
    )


def test_twin_west_towers_keep_central_front_composition_on_nave():
    geometry = AtlasChurchLandmarkBuilder.build(
        landmark=_landmark(
            landmark_type=AtlasLandmarkType.CATHEDRAL,
        ),
        profile=AtlasChurchLandmarkProfile(
            landmark_class="cathedral",
            grammar_name="twin_west_towers",
            profile_name="romanesque_cathedral",
            tower_count=2,
        ),
    )

    mesh = AtlasChurchLandmarkMesher.build(
        geometry
    )

    facade = mesh[
        "architectural_facade_system"
    ]

    front = next(
        item
        for item in facade["end_facades"]
        if item["facade_side"] == "front"
    )

    assert facade["front_surface_target"] == (
        "main_nave_front"
    )
    assert front["surface_target"] == (
        "main_nave_front"
    )

    assert all(
        panel["surface_target"]
        == "main_nave_front"
        for panel in front["component_meshes"]
    )

    assert all(
        oculus["surface_target"]
        == "main_nave_front"
        for oculus in facade["oculus_meshes"]
    )

