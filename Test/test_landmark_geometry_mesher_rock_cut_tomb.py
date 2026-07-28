from CORE.atlas_landmark_geometry_mesher import (
    AtlasLandmarkGeometryMesher,
)
from CORE.atlas_rock_cut_tomb_builder import (
    AtlasRockCutTombGeometry,
)


def test_rock_cut_tomb_mesher_builds_closed_prism():
    geometry = AtlasRockCutTombGeometry(
        footprint=(
            (-4.0, -1.0),
            (4.0, -1.0),
            (4.0, 1.0),
            (-4.0, 1.0),
        ),
        height_m=3.0,
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert len(mesh["triangles"]) == 12
    assert mesh["bottom"] == (
        (-4.0, -1.0, 0.0),
        (4.0, -1.0, 0.0),
        (4.0, 1.0, 0.0),
        (-4.0, 1.0, 0.0),
    )
    assert mesh["top"] == (
        (-4.0, -1.0, 3.0),
        (4.0, -1.0, 3.0),
        (4.0, 1.0, 3.0),
        (-4.0, 1.0, 3.0),
    )
