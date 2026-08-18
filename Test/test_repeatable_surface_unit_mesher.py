from CORE.atlas_repeatable_surface_unit_mesher import (
    AtlasRepeatableSurfaceUnitMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_repeatable_surface_unit_builds_closed_rectangular_unit():
    result = AtlasRepeatableSurfaceUnitMesher.build(
        center_x=0.0,
        center_y=0.0,
        base_z=0.0,
        width_mm=2.4,
        height_mm=1.2,
        depth_mm=0.24,
        unit_kind="brick",
    )

    assert result["component_type"] == "repeatable_surface_unit"
    assert result["unit_kind"] == "brick"
    assert result["source_system"] == "repeatable_surface_unit_mesher"
    assert result["geometry_type"] == "rectangular_surface_unit"

    report = AtlasMeshValidator._topology_report(
        result
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0
