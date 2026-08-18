from CORE.atlas_facade_tracery_mesher import (
    AtlasFacadeTraceryMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (6.0, 0.0, 0.0),
    (6.0, 0.0, 6.0),
    (0.0, 0.0, 6.0),
)


def test_tracery_builds_closed_vertical_and_horizontal_bars():
    result = AtlasFacadeTraceryMesher.build(
        wall_quad=WALL_QUAD,
        u_min=0.25,
        u_max=0.75,
        v_min=0.20,
        v_max=0.80,
        mullion_width_ratio=0.08,
        transom_height_ratio=0.08,
        depth_mm=0.24,
        embed_mm=0.04,
    )

    assert result["tracery_count"] == 2
    assert tuple(
        component["tracery_part"]
        for component in result["component_meshes"]
    ) == (
        "mullion",
        "transom",
    )

    for component in result["component_meshes"]:
        assert component["component_type"] == "facade_tracery"
        assert component["source_system"] == "facade_tracery_mesher"

        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0
