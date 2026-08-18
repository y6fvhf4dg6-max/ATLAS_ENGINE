from CORE.atlas_figurative_plaque_mesher import (
    AtlasFigurativePlaqueMesher,
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


def test_figurative_plaque_builds_closed_rectangular_carrier():
    result = AtlasFigurativePlaqueMesher.build(
        wall_quad=WALL_QUAD,
        center_u=0.5,
        center_v=0.55,
        width_ratio=0.40,
        height_ratio=0.30,
        depth_mm=0.24,
        embed_mm=0.04,
    )

    assert result["plaque_count"] == 1

    component = result["component_meshes"][0]

    assert component["component_type"] == "figurative_plaque"
    assert component["content_role"] == "figurative_carrier"
    assert component["source_system"] == "figurative_plaque_mesher"

    report = AtlasMeshValidator._topology_report(
        component
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
