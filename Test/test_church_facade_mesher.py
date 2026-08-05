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
    assert result["panel_count"] == 10

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

    assert all(
        panel["architectural_role"]
        == "church_main_nave_facade_bay"
        and panel["facade_rhythm"]
        == "heavy_round_arch"
        and panel["arch_shape"]
        == "round_arch"
        for panel in result["component_meshes"]
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

