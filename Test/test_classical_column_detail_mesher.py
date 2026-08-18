from CORE.atlas_classical_column_detail_mesher import (
    AtlasClassicalColumnDetailMesher,
)
from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)


def test_column_detail_mesher_builds_base_and_capital():
    result = AtlasClassicalColumnDetailMesher.build(
        center_x=0.0,
        center_y=0.0,
        shaft_base_z=0.4,
        shaft_top_z=3.4,
        base_diameter_mm=1.6,
        base_height_mm=0.4,
        capital_diameter_mm=1.8,
        capital_height_mm=0.5,
        segments=12,
    )

    assert len(result["component_meshes"]) == 2
    assert tuple(
        component["detail_role"]
        for component in result["component_meshes"]
    ) == (
        "base",
        "capital",
    )

    base, capital = result["component_meshes"]

    assert base["component_type"] == "classical_column_detail"
    assert capital["component_type"] == "classical_column_detail"
    assert base["source_system"] == "classical_column_detail_mesher"
    assert capital["source_system"] == "classical_column_detail_mesher"

    assert base["top_z"] == 0.4
    assert capital["base_z"] == 3.4

    for component in result["component_meshes"]:
        report = AtlasMeshValidator._topology_report(
            component
        )

        assert report["open_edge_count"] == 0
        assert report["non_manifold_edge_count"] == 0
