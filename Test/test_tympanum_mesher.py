from CORE.atlas_tympanum_mesher import (
    AtlasTympanumMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_tympanum_builds_closed_triangular_pediment_panel():
    result = AtlasTympanumMesher.build(
        center_x=0.0,
        base_z=0.0,
        width_mm=4.0,
        height_mm=1.6,
        depth_mm=0.24,
    )

    assert result["component_type"] == "tympanum"
    assert result["source_system"] == "tympanum_mesher"
    assert result["geometry_type"] == "tympanum_prism"
    assert result["width_mm"] == 4.0
    assert result["height_mm"] == 1.6

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
