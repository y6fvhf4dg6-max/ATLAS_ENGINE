from CORE.atlas_landmark_geometry_mesher import AtlasLandmarkGeometryMesher
from CORE.atlas_tower_builder import AtlasTowerGeometry


def test_mesher_builds_mesh_from_tower_geometry():
    geometry = AtlasTowerGeometry(
        footprint=[
            (0.0, 0.0),
            (2.0, 0.0),
            (2.0, 2.0),
            (0.0, 2.0),
        ],
        height_m=40.0,
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert isinstance(mesh, dict)
    assert "bottom" in mesh
    assert "top" in mesh
    assert "walls" in mesh
    assert "triangles" in mesh
    assert len(mesh["triangles"]) > 0
