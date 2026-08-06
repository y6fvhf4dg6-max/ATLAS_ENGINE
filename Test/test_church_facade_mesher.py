from CORE.atlas_church_body_profile_system import (
    AtlasChurchBodyProfileSystem,
)
from CORE.atlas_church_facade_mesher import (
    AtlasChurchFacadeMesher,
)
from CORE.atlas_church_facade_profile_system import (
    AtlasChurchFacadeProfileSystem,
)
from CORE.atlas_church_footprint_resolver import (
    AtlasChurchFootprintResolver,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def _frame():
    return AtlasChurchFootprintResolver.resolve(
        (
            (0.0, 0.0),
            (30.0, 0.0),
            (30.0, 60.0),
            (0.0, 60.0),
        )
    )


def test_heavy_round_arch_builds_two_main_nave_side_facades():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["type"] == "church_facade_system"
    assert result["facade_rhythm"] == "heavy_round_arch"
    assert len(result["side_facades"]) == 2
    assert sum(
        facade["panel_count"]
        for facade in result["side_facades"]
    ) == 10
    assert len(result["end_facades"]) == 2
    assert len(result["oculus_meshes"]) == 1
    assert result["panel_count"] == 13

    assert {
        facade["facade_side"]
        for facade in result["side_facades"]
    } == {
        "left",
        "right",
    }


def test_regular_facade_uses_denser_bay_rhythm():
    regular = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )
    heavy = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert regular["panel_count"] > heavy["panel_count"]


def test_facade_panels_preserve_semantic_metadata():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    side_panels = [
        panel
        for facade in result["side_facades"]
        for panel in facade["component_meshes"]
    ]

    assert all(
        panel["architectural_role"]
        == "church_main_nave_facade_bay"
        and panel["facade_rhythm"]
        == "heavy_round_arch"
        and panel["arch_shape"]
        == "round_arch"
        for panel in side_panels
    )


def test_each_church_facade_panel_is_closed():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    for component in result["component_meshes"]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0


def test_facade_depth_respects_printable_nozzle_minimum():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["physical_depth_mm"] >= 0.4
    assert result["model_depth_m"] > 0.0

def test_basilica_body_profile_controls_facade_wall_proportions():
    cross_plan = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )
    basilica = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert (
        basilica["main_nave_width"]
        < cross_plan["main_nave_width"]
    )
    assert (
        basilica["main_nave_depth"]
        > cross_plan["main_nave_depth"]
    )

    import pytest

    assert basilica["main_nave_width"] == pytest.approx(
        30.0 * 0.46
    )
    assert basilica["main_nave_depth"] == pytest.approx(
        60.0 * 0.82
    )

def test_window_bay_omit_action_suppresses_facade_panels():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="omit",
        window_resolved_size_mm=0.0,
    )

    assert result["window_action"] == "omit"
    assert result["window_resolved_size_mm"] == 0.0
    assert result["panel_count"] == 0
    assert result["side_facades"] == []
    assert result["component_meshes"] == []
    assert result["triangles"] == []


def test_window_bay_physical_decision_is_published():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="enlarge",
        window_resolved_size_mm=0.8,
    )

    assert result["window_action"] == "enlarge"
    assert result["window_resolved_size_mm"] == 0.8
    assert result["physical_depth_mm"] == 0.4
    assert result["panel_count"] > 0

    assert all(
        panel["physical_action"] == "enlarge"
        and panel["resolved_size_mm"] == 0.8
        and panel["depth_mm"]
        == result["model_depth_m"]
        for panel in result["component_meshes"]
    )

def test_church_facade_builds_front_and_rear_compositions():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert len(result["end_facades"]) == 2
    assert {
        facade["facade_side"]
        for facade in result["end_facades"]
    } == {
        "front",
        "rear",
    }

    assert all(
        facade["panel_count"] == 1
        for facade in result["end_facades"]
    )


def test_front_and_rear_facades_preserve_semantic_roles():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    end_panels = [
        panel
        for facade in result["end_facades"]
        for panel in facade["component_meshes"]
    ]

    assert {
        panel["facade_side"]
        for panel in end_panels
    } == {
        "front",
        "rear",
    }

    assert {
        panel["architectural_role"]
        for panel in end_panels
    } == {
        "church_front_facade_opening",
        "church_rear_facade_opening",
    }


def test_window_omit_suppresses_all_four_facade_sides():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="omit",
        window_resolved_size_mm=0.0,
    )

    assert result["side_facades"] == []
    assert result["end_facades"] == []
    assert result["panel_count"] == 0

def test_facade_output_publishes_front_and_rear_compositions():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert (
        result["front_composition"]
        == "portal_with_oculus"
    )
    assert (
        result["rear_composition"]
        == "round_arch_opening"
    )


def test_end_facades_preserve_composition_identity():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    front = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "front"
    )
    rear = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "rear"
    )

    assert (
        front["facade_composition"]
        == "portal_with_oculus"
    )
    assert (
        rear["facade_composition"]
        == "round_arch_opening"
    )

    assert all(
        panel["facade_composition"]
        == front["facade_composition"]
        for panel in front["component_meshes"]
    )
    assert all(
        panel["facade_composition"]
        == rear["facade_composition"]
        for panel in rear["component_meshes"]
    )


def test_omit_output_retains_composition_contract():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="omit",
        window_resolved_size_mm=0.0,
    )

    assert (
        result["front_composition"]
        == "single_arch_portal"
    )
    assert (
        result["rear_composition"]
        == "single_arch_opening"
    )

def test_portal_with_oculus_adds_circular_front_facade_detail():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert len(result["oculus_meshes"]) == 1

    oculus = result["oculus_meshes"][0]

    assert (
        oculus["architectural_role"]
        == "church_front_facade_oculus"
    )
    assert oculus["facade_side"] == "front"
    assert (
        oculus["facade_composition"]
        == "portal_with_oculus"
    )
    assert (
        oculus["geometry_type"]
        == "circular_facade_panel_prism"
    )


def test_single_arch_portal_does_not_add_oculus():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["oculus_meshes"] == []


def test_window_omit_suppresses_oculus_geometry():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="omit",
        window_resolved_size_mm=0.0,
    )

    assert result["oculus_meshes"] == []
    assert result["panel_count"] == 0


def test_oculus_is_closed_and_manifold():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    report = AtlasMeshValidator._topology_report(
        result["oculus_meshes"][0]
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0

def test_rear_composition_controls_arch_geometry():
    regular = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )
    romanesque = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    regular_rear = next(
        facade
        for facade in regular["end_facades"]
        if facade["facade_side"] == "rear"
    )
    romanesque_rear = next(
        facade
        for facade in romanesque["end_facades"]
        if facade["facade_side"] == "rear"
    )

    assert abs(
        regular_rear["arch_height_ratio"] - 0.35
    ) < 1e-9
    assert abs(
        romanesque_rear["arch_height_ratio"] - 1.00
    ) < 1e-9

    regular_panel = (
        regular_rear["component_meshes"][0]
    )
    romanesque_panel = (
        romanesque_rear["component_meshes"][0]
    )

    regular_arch_rise = (
        max(
            point[2]
            for point in regular_panel["back"]
        )
        - regular_panel["back"][2][2]
    )
    romanesque_arch_rise = (
        max(
            point[2]
            for point in romanesque_panel["back"]
        )
        - romanesque_panel["back"][2][2]
    )

    regular_width = abs(
        regular_panel["back"][1][0]
        - regular_panel["back"][0][0]
    )
    romanesque_width = abs(
        romanesque_panel["back"][1][0]
        - romanesque_panel["back"][0][0]
    )

    assert regular_arch_rise < (
        regular_width * 0.5
    )
    assert abs(
        romanesque_arch_rise
        - romanesque_width * 0.5
    ) < 1e-9


def test_front_portal_arch_ratio_remains_independent_from_rear():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    front = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "front"
    )
    rear = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "rear"
    )

    assert abs(
        front["arch_height_ratio"] - 1.00
    ) < 1e-9
    assert abs(
        rear["arch_height_ratio"] - 1.00
    ) < 1e-9

def test_front_composition_controls_portal_geometry():
    regular = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )
    romanesque = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    regular_front = next(
        facade
        for facade in regular["end_facades"]
        if facade["facade_side"] == "front"
    )
    romanesque_front = next(
        facade
        for facade in romanesque["end_facades"]
        if facade["facade_side"] == "front"
    )

    assert abs(
        regular_front["panel_width_ratio"] - 0.28
    ) < 1e-9
    assert abs(
        regular_front["panel_height_ratio"] - 0.34
    ) < 1e-9
    assert abs(
        regular_front["arch_height_ratio"] - 0.50
    ) < 1e-9

    assert abs(
        romanesque_front["panel_width_ratio"] - 0.34
    ) < 1e-9
    assert abs(
        romanesque_front["panel_height_ratio"] - 0.42
    ) < 1e-9
    assert abs(
        romanesque_front["arch_height_ratio"] - 1.00
    ) < 1e-9


def test_portal_with_oculus_builds_larger_front_portal():
    regular = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "regular"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )
    romanesque = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    regular_front = next(
        facade
        for facade in regular["end_facades"]
        if facade["facade_side"] == "front"
    )
    romanesque_front = next(
        facade
        for facade in romanesque["end_facades"]
        if facade["facade_side"] == "front"
    )

    regular_panel = (
        regular_front["component_meshes"][0]
    )
    romanesque_panel = (
        romanesque_front["component_meshes"][0]
    )

    regular_width = abs(
        regular_panel["back"][1][0]
        - regular_panel["back"][0][0]
    )
    romanesque_width = abs(
        romanesque_panel["back"][1][0]
        - romanesque_panel["back"][0][0]
    )

    regular_height = (
        max(
            point[2]
            for point in regular_panel["back"]
        )
        - min(
            point[2]
            for point in regular_panel["back"]
        )
    )
    romanesque_height = (
        max(
            point[2]
            for point in romanesque_panel["back"]
        )
        - min(
            point[2]
            for point in romanesque_panel["back"]
        )
    )

    assert romanesque_width > regular_width
    assert romanesque_height > regular_height



def test_front_portal_is_ground_anchored_but_rear_opening_is_not():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    front = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "front"
    )
    rear = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "rear"
    )

    front_panel = front["component_meshes"][0]
    rear_panel = rear["component_meshes"][0]

    front_min_z = min(
        point[2]
        for point in front_panel["back"]
    )
    rear_min_z = min(
        point[2]
        for point in rear_panel["back"]
    )

    assert front_min_z == 0.0
    assert rear_min_z > 0.0
    assert front["vertical_alignment"] == "bottom"
    assert rear["vertical_alignment"] == "center"

def test_side_facades_can_target_visible_clerestory_band():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        side_wall_min_z=8.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    side_panels = [
        panel
        for facade in result["side_facades"]
        for panel in facade["component_meshes"]
    ]

    assert result["side_wall_min_z"] == 8.0
    assert result["side_wall_max_z"] == 20.0
    assert result["side_surface_target"] == (
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
    ) >= 8.0

def test_front_composition_can_target_custom_visible_surface():
    frame = _frame()

    front_wall_quad = (
        (4.0, 7.0, 0.0),
        (16.0, 7.0, 0.0),
        (16.0, 7.0, 18.0),
        (4.0, 7.0, 18.0),
    )

    result = AtlasChurchFacadeMesher.build(
        frame=frame,
        wall_height=20.0,
        front_wall_quad=front_wall_quad,
        front_surface_target=(
            "west_tower_center_front"
        ),
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    front = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "front"
    )

    assert result["front_surface_target"] == (
        "west_tower_center_front"
    )
    assert front["surface_target"] == (
        "west_tower_center_front"
    )

    assert all(
        panel["surface_target"]
        == "west_tower_center_front"
        for panel in front["component_meshes"]
    )

    assert len(result["oculus_meshes"]) == 1
    assert (
        result["oculus_meshes"][0][
            "surface_target"
        ]
        == "west_tower_center_front"
    )

    assert all(
        abs(point[1] - 7.0)
        <= result["model_depth_m"]
        for panel in front["component_meshes"]
        for point in (
            *panel["back"],
            *panel["front"],
        )
    )

    oculus = result["oculus_meshes"][0]

    assert abs(
        oculus["center"][1] - 7.0
    ) < 1e-9

def test_rear_composition_can_target_custom_visible_surface():
    rear_wall_quad = (
        (6.0, 52.0, 0.0),
        (24.0, 52.0, 0.0),
        (24.0, 52.0, 14.0),
        (6.0, 52.0, 14.0),
    )

    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        rear_wall_quad=rear_wall_quad,
        rear_surface_target="apse_outer_rear",
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    rear = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "rear"
    )

    assert result["rear_surface_target"] == (
        "apse_outer_rear"
    )
    assert rear["surface_target"] == (
        "apse_outer_rear"
    )

    assert all(
        panel["surface_target"]
        == "apse_outer_rear"
        for panel in rear["component_meshes"]
    )

    assert all(
        abs(point[1] - 52.0)
        <= result["model_depth_m"]
        for panel in rear["component_meshes"]
        for point in (
            *panel["back"],
            *panel["front"],
        )
    )

    rear_panel = rear["component_meshes"][0]

    assert max(
        point[2]
        for point in rear_panel["back"]
    ) <= 14.0


def _panel_surface_dimensions_mm(
    panel,
    *,
    scale_ratio,
):
    points = tuple(panel["back"])

    spans = []
    for axis in range(3):
        values = tuple(
            point[axis]
            for point in points
        )
        span = max(values) - min(values)

        if span > 1e-9:
            spans.append(span)

    return tuple(
        span * 1000.0 / scale_ratio
        for span in sorted(spans)
    )


def test_enlarge_applies_print_minimum_to_side_opening_dimensions():
    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="enlarge",
        window_resolved_size_mm=0.8,
        side_wall_min_z=8.0,
    )

    side_panel = next(
        panel
        for panel in result["component_meshes"]
        if panel["facade_side"] == "left"
    )

    dimensions_mm = (
        _panel_surface_dimensions_mm(
            side_panel,
            scale_ratio=5500.0,
        )
    )

    assert min(dimensions_mm) >= 0.8 - 1e-9


def test_enlarge_applies_print_minimum_to_front_portal_width():
    front_wall_quad = (
        (0.0, 0.0, 0.0),
        (4.4, 0.0, 0.0),
        (4.4, 0.0, 18.0),
        (0.0, 0.0, 18.0),
    )

    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="enlarge",
        window_resolved_size_mm=0.8,
        front_wall_quad=front_wall_quad,
        front_surface_target=(
            "west_tower_center_front"
        ),
    )

    front = next(
        facade
        for facade in result["end_facades"]
        if facade["facade_side"] == "front"
    )
    portal = front["component_meshes"][0]

    dimensions_mm = (
        _panel_surface_dimensions_mm(
            portal,
            scale_ratio=5500.0,
        )
    )

    assert min(dimensions_mm) >= 0.8 - 1e-9


def test_enlarge_applies_print_minimum_to_oculus_diameter():
    front_wall_quad = (
        (0.0, 0.0, 0.0),
        (4.4, 0.0, 0.0),
        (4.4, 0.0, 18.0),
        (0.0, 0.0, 18.0),
    )

    result = AtlasChurchFacadeMesher.build(
        frame=_frame(),
        wall_height=20.0,
        facade_profile=(
            AtlasChurchFacadeProfileSystem.resolve(
                "heavy_round_arch"
            )
        ),
        body_profile=(
            AtlasChurchBodyProfileSystem.resolve(
                "basilica_cross_plan"
            )
        ),
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
        window_action="enlarge",
        window_resolved_size_mm=0.8,
        front_wall_quad=front_wall_quad,
        front_surface_target=(
            "west_tower_center_front"
        ),
    )

    oculus = result["oculus_meshes"][0]

    diameter_mm = (
        oculus["diameter"]
        * 1000.0
        / 5500.0
    )

    assert diameter_mm >= 0.8 - 1e-9

