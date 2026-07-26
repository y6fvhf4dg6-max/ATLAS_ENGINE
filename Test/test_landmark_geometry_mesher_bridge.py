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


def test_bridge_mesh_uses_deck_thickness_below_bridge_height():
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
            "bridge_deck_thickness_m": 1.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert {point[2] for point in mesh["bottom"]} == {7.0}
    assert {point[2] for point in mesh["top"]} == {8.0}
    assert mesh["metadata"]["bridge_deck_thickness_m"] == 1.0

def test_bridge_mesh_adds_closed_pier_prisms():
    geometry = AtlasBridgeGeometry(
        footprint=(
            (0.0, -3.0),
            (20.0, -3.0),
            (20.0, 3.0),
            (0.0, 3.0),
        ),
        height_m=8.0,
        landmark_kind="bridge",
        metadata={
            "bridge_span_m": 20.0,
            "bridge_width_m": 6.0,
            "bridge_deck_thickness_m": 1.0,
            "bridge_pier_count": 2,
            "bridge_pier_positions": (
                (20.0 / 3.0, 0.0),
                (40.0 / 3.0, 0.0),
            ),
            "bridge_pier_width_m": 2.0,
            "bridge_pier_depth_m": 1.0,
            "bridge_pier_base_m": 0.0,
            "bridge_pier_top_m": 7.0,
            "bridge_pier_height_m": 7.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert len(mesh["piers"]) == 2
    assert all(len(pier["bottom"]) == 4 for pier in mesh["piers"])
    assert all(len(pier["top"]) == 4 for pier in mesh["piers"])
    assert all(len(pier["triangles"]) == 12 for pier in mesh["piers"])
    assert len(mesh["triangles"]) == 36

def test_bridge_piers_follow_diagonal_bridge_axis():
    geometry = AtlasBridgeGeometry(
        footprint=(
            (1.0, -1.0),
            (11.0, 9.0),
            (9.0, 11.0),
            (-1.0, 1.0),
        ),
        height_m=8.0,
        landmark_kind="bridge",
        metadata={
            "bridge_deck_thickness_m": 1.0,
            "bridge_pier_positions": ((5.0, 5.0),),
            "bridge_pier_width_m": 2.0,
            "bridge_pier_depth_m": 1.0,
            "bridge_pier_base_m": 0.0,
            "bridge_pier_top_m": 7.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)
    bottom = mesh["piers"][0]["bottom"]

    axis_edge = (
        bottom[1][0] - bottom[0][0],
        bottom[1][1] - bottom[0][1],
    )

    assert axis_edge[0] > 0.0
    assert axis_edge[1] > 0.0
    assert abs(axis_edge[0] - axis_edge[1]) < 1e-12
