from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_tower_builder import AtlasTowerGeometry


def test_observation_profile_creates_multi_ring_mesh():
    geometry = AtlasTowerGeometry(
        footprint=(
            (0.0, 0.0),
            (2.0, 0.0),
            (2.0, 2.0),
            (0.0, 2.0),
        ),
        height_m=100.0,
        profile="observation",
    )

    mesh = AtlasLandmarkGeometryMesher._build_tower_mesh(
        geometry
    )

    # Generic extrusion = 4 wall quads.
    # Observation profile must create multiple stacked rings.
    assert len(mesh["walls"]) > 4

    # Observation profile should also generate
    # substantially more triangles than a simple extrusion.
    assert len(mesh["triangles"]) > 40
