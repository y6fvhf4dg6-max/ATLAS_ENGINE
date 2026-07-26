from CORE.atlas_bridge_builder import AtlasBridgeGeometry
from CORE.atlas_landmark_geometry_mesher import AtlasLandmarkGeometryMesher


def test_bridge_geometry_builds_closed_prism_mesh():
    geometry = AtlasBridgeGeometry(
        footprint=(
            (0.0, 0.0),
            (20.0, 0.0),
            (20.0, 6.0),
            (0.0, 6.0),
        ),
        height_m=8.0,
        landmark_kind="bridge",
        metadata={
            "bridge_span_m": 20.0,
            "bridge_width_m": 6.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert mesh["type"] == "bridge"
    assert len(mesh["bottom"]) == 4
    assert len(mesh["top"]) == 4
    assert len(mesh["triangles"]) == 12
