from CORE.atlas_floral_ornament_mesher import (
    AtlasFloralOrnamentMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_floral_ornament_builds_closed_radial_petal_prism():
    result = AtlasFloralOrnamentMesher.build(
        center_x=0.0,
        center_y=0.0,
        outer_diameter_mm=4.0,
        inner_ratio=0.45,
        petal_count=8,
        base_z=0.0,
        depth_mm=0.24,
    )

    assert result["component_type"] == "floral_ornament"
    assert result["source_system"] == "floral_ornament_mesher"
    assert result["geometry_type"] == "floral_ornament_prism"
    assert result["petal_count"] == 8
    assert result["outer_diameter_mm"] == 4.0

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
