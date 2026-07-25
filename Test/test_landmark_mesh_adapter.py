from CORE.atlas_landmark_geometry import AtlasLandmarkGeometry
from CORE.atlas_landmark_mesh_adapter import AtlasLandmarkMeshAdapter


def test_adapter_exposes_mesh_builder_contract():
    geometry = AtlasLandmarkGeometry(
        footprint=(
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
        ),
        height_mm=12.0,
    )

    building = AtlasLandmarkMeshAdapter.from_geometry(geometry)

    assert building.geometry == geometry.footprint
    assert building.estimated_height == geometry.height_mm
    assert building.area_m2 > 0.0
    assert building.is_building_part is False
