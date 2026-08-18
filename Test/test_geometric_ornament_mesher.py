from CORE.atlas_geometric_ornament_mesher import (
    AtlasGeometricOrnamentMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_geometric_ornament_builds_closed_polygon_prism():
    result = AtlasGeometricOrnamentMesher.build(
        outline_points=(
            (-1.0, 0.0),
            (-0.3, -0.3),
            (0.0, -1.0),
            (0.3, -0.3),
            (1.0, 0.0),
            (0.3, 0.3),
            (0.0, 1.0),
            (-0.3, 0.3),
        ),
        base_z=0.0,
        depth_mm=0.24,
        metadata={
            "ornament_role": "geometric",
        },
    )

    assert result["component_type"] == "geometric_ornament"
    assert result["source_system"] == "geometric_ornament_mesher"
    assert result["ornament_role"] == "geometric"
    assert result["geometry_type"] == "geometric_ornament_prism"

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
