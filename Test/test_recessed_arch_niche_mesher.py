from CORE.atlas_recessed_arch_niche_mesher import (
    AtlasRecessedArchNicheMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_recessed_arch_niche_builds_closed_planar_niche():
    result = AtlasRecessedArchNicheMesher.build(
        center_x=0.0,
        center_z=2.0,
        width_mm=3.0,
        height_mm=4.0,
        spring_height_mm=2.8,
        recess_depth_mm=0.4,
        front_y=0.0,
        arch_segments=8,
    )

    assert result["component_type"] == "recessed_arch_niche"
    assert result["source_system"] == "recessed_arch_niche_mesher"
    assert result["geometry_type"] == "recessed_arch_niche"
    assert result["recess_depth_mm"] == 0.4
    assert result["arch_segments"] == 8

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
