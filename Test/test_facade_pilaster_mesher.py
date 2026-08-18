from CORE.atlas_facade_pilaster_mesher import (
    AtlasFacadePilasterMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (12.0, 0.0, 0.0),
    (12.0, 0.0, 7.0),
    (0.0, 0.0, 7.0),
)


def test_pilaster_builds_single_vertical_closed_component():
    result = AtlasFacadePilasterMesher.build(
        wall_quad=WALL_QUAD,
        center_u=0.5,
        width_ratio=0.12,
        v_min=0.10,
        v_max=0.90,
        depth_mm=0.24,
        embed_mm=0.04,
    )

    assert result["pilaster_count"] == 1
    assert len(result["component_meshes"]) == 1

    component = result["component_meshes"][0]

    assert component["component_type"] == "facade_pilaster"
    assert component["source_system"] == "facade_pilaster_mesher"

    report = AtlasMeshValidator._topology_report(
        component
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
