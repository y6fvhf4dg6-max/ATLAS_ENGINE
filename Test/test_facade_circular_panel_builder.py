import pytest

from CORE.atlas_facade_circular_panel_builder import (
    AtlasFacadeCircularPanelBuilder,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def _wall_quad():
    return (
        (0.0, 0.0, 0.0),
        (10.0, 0.0, 0.0),
        (10.0, 0.0, 12.0),
        (0.0, 0.0, 12.0),
    )


def test_circular_facade_panel_builds_closed_prism():
    result = AtlasFacadeCircularPanelBuilder.build(
        wall_quad=_wall_quad(),
        center_u=0.50,
        center_v=0.68,
        diameter_ratio=0.24,
        depth_mm=0.8,
        embed_mm=0.2,
        segments=16,
    )

    assert result["type"] == "circular_facade_panel"
    assert result["geometry_type"] == (
        "circular_facade_panel_prism"
    )
    assert result["segments"] == 16
    assert len(result["back_ring"]) == 16
    assert len(result["front_ring"]) == 16

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


def test_circular_facade_panel_preserves_metadata():
    result = AtlasFacadeCircularPanelBuilder.build(
        wall_quad=_wall_quad(),
        center_u=0.50,
        center_v=0.68,
        diameter_ratio=0.24,
        depth_mm=0.8,
        embed_mm=0.2,
        metadata={
            "architectural_role": (
                "church_front_facade_oculus"
            ),
            "facade_side": "front",
        },
    )

    assert (
        result["architectural_role"]
        == "church_front_facade_oculus"
    )
    assert result["facade_side"] == "front"


def test_circular_panel_depth_and_embed_are_preserved():
    result = AtlasFacadeCircularPanelBuilder.build(
        wall_quad=_wall_quad(),
        center_u=0.50,
        center_v=0.68,
        diameter_ratio=0.24,
        depth_mm=0.8,
        embed_mm=0.2,
    )

    assert result["depth_mm"] == pytest.approx(0.8)
    assert result["embed_mm"] == pytest.approx(0.2)


@pytest.mark.parametrize(
    "diameter_ratio",
    (0.0, -0.1, 1.1),
)
def test_circular_panel_rejects_invalid_diameter_ratio(
    diameter_ratio,
):
    with pytest.raises(ValueError):
        AtlasFacadeCircularPanelBuilder.build(
            wall_quad=_wall_quad(),
            center_u=0.50,
            center_v=0.68,
            diameter_ratio=diameter_ratio,
            depth_mm=0.8,
            embed_mm=0.2,
        )


def test_circular_panel_rejects_degenerate_wall():
    with pytest.raises(
        ValueError,
        match="wall_quad is degenerate",
    ):
        AtlasFacadeCircularPanelBuilder.build(
            wall_quad=(
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
                (0.0, 0.0, 0.0),
            ),
            center_u=0.50,
            center_v=0.68,
            diameter_ratio=0.24,
            depth_mm=0.8,
            embed_mm=0.2,
        )
