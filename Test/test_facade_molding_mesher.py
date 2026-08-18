from CORE.atlas_facade_molding_mesher import (
    AtlasFacadeMoldingMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


WALL_QUAD = (
    (0.0, 0.0, 0.0),
    (8.0, 0.0, 0.0),
    (8.0, 0.0, 6.0),
    (0.0, 0.0, 6.0),
)


def test_molding_builds_closed_linear_band():
    result = AtlasFacadeMoldingMesher.build(
        wall_quad=WALL_QUAD,
        u_min=0.10,
        u_max=0.90,
        center_v=0.60,
        height_ratio=0.08,
        depth_mm=0.24,
        embed_mm=0.04,
    )

    assert result["molding_count"] == 1

    component = result["component_meshes"][0]

    assert component["component_type"] == "facade_molding"
    assert component["molding_profile"] == "rectangular_band"
    assert component["source_system"] == "facade_molding_mesher"

    report = AtlasMeshValidator._topology_report(
        component
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
