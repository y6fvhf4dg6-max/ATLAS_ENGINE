from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_lighthouse_builder import (
    AtlasLighthouseGeometry,
)


def test_lighthouse_mesh_has_multistage_profile():
    geometry = AtlasLighthouseGeometry(
        footprint=(
            (0.0, 0.0),
            (4.0, 0.0),
            (4.0, 4.0),
            (0.0, 4.0),
        ),
        height_m=35.0,
    )

    mesh = AtlasLandmarkGeometryMesher.build(
        geometry
    )

    z_levels = {
        round(point[2], 6)
        for triangle in mesh["triangles"]
        for point in triangle
    }

    assert mesh["type"] == "lighthouse"
    assert mesh["profile"] == "multistage"
    assert len(z_levels) >= 5
    assert len(mesh["triangles"]) > 28
