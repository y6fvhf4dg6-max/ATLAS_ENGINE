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


def _polygon_area(points):
    return abs(
        sum(
            x1 * y2 - x2 * y1
            for (x1, y1), (x2, y2) in zip(
                points,
                points[1:] + points[:1],
            )
        )
    ) / 2.0


def _triangle_xy_area(triangle):
    (x1, y1, _), (x2, y2, _), (x3, y3, _) = triangle

    return abs(
        (x1 * (y2 - y3)
         + x2 * (y3 - y1)
         + x3 * (y1 - y2))
        / 2.0
    )


def test_bridge_mesh_triangulates_concave_deck_without_overlap():
    footprint = (
        (0.0, 0.0),
        (8.0, 0.0),
        (8.0, 6.0),
        (5.0, 6.0),
        (5.0, 2.0),
        (3.0, 2.0),
        (3.0, 6.0),
        (0.0, 6.0),
    )

    geometry = AtlasBridgeGeometry(
        footprint=footprint,
        height_m=8.0,
        landmark_kind="bridge",
        metadata={
            "bridge_deck_thickness_m": 1.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    top_triangles = [
        triangle
        for triangle in mesh["triangles"]
        if {point[2] for point in triangle} == {8.0}
    ]

    expected_area = _polygon_area(list(footprint))
    triangulated_area = sum(
        _triangle_xy_area(triangle)
        for triangle in top_triangles
    )

    assert len(top_triangles) == len(footprint) - 2
    assert abs(triangulated_area - expected_area) < 1e-9


def test_bridge_mesh_applies_longitudinal_approach_profile():
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
            "bridge_deck_thickness_m": 1.0,
            "bridge_approach_profile": True,
            "bridge_shore_top_m": 6.0,
            "bridge_approach_ratio": 0.20,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    top_by_x = {}

    for x, y, z in mesh["top"]:
        top_by_x.setdefault(x, set()).add(z)

    bottom_by_x = {}

    for x, y, z in mesh["bottom"]:
        bottom_by_x.setdefault(x, set()).add(z)

    assert top_by_x[0.0] == {6.0}
    assert top_by_x[20.0] == {6.0}

    assert bottom_by_x[0.0] == {5.0}
    assert bottom_by_x[20.0] == {5.0}

    assert mesh["metadata"]["bridge_approach_profile"] is True


def test_bridge_mesh_keeps_flat_deck_without_approach_metadata():
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
            "bridge_deck_thickness_m": 1.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert {point[2] for point in mesh["top"]} == {8.0}
    assert {point[2] for point in mesh["bottom"]} == {7.0}


def test_bridge_mesh_builds_segmented_approach_deck():
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
            "bridge_deck_thickness_m": 1.0,
            "bridge_segmented_deck": True,
            "bridge_shore_top_m": 6.0,
            "bridge_approach_ratio": 0.20,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    sections = mesh["deck_sections"]

    assert len(sections) == 3
    assert [section["kind"] for section in sections] == [
        "start_approach",
        "main_deck",
        "end_approach",
    ]

    start = sections[0]
    center = sections[1]
    end = sections[2]

    assert min(point[2] for point in start["top"]) == 6.0
    assert max(point[2] for point in start["top"]) == 8.0

    assert {point[2] for point in center["top"]} == {8.0}

    assert min(point[2] for point in end["top"]) == 6.0
    assert max(point[2] for point in end["top"]) == 8.0

    for section in sections:
        top_by_xy = {
            (x, y): z
            for x, y, z in section["top"]
        }
        bottom_by_xy = {
            (x, y): z
            for x, y, z in section["bottom"]
        }

        assert top_by_xy.keys() == bottom_by_xy.keys()

        for xy in top_by_xy:
            assert (
                top_by_xy[xy] - bottom_by_xy[xy]
                == 1.0
            )

        assert len(section["triangles"]) > 0


def test_segmented_bridge_mesh_preserves_flat_bridge_compatibility():
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
            "bridge_deck_thickness_m": 1.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)

    assert "deck_sections" not in mesh
    assert {point[2] for point in mesh["top"]} == {8.0}
    assert {point[2] for point in mesh["bottom"]} == {7.0}


def _mesh_edge_topology(triangles):
    from collections import Counter

    def vertex_key(point):
        return tuple(
            round(float(value), 8)
            for value in point
        )

    def edge_key(first, second):
        return tuple(
            sorted(
                (
                    vertex_key(first),
                    vertex_key(second),
                )
            )
        )

    counts = Counter()

    for first, second, third in triangles:
        counts[edge_key(first, second)] += 1
        counts[edge_key(second, third)] += 1
        counts[edge_key(third, first)] += 1

    return {
        "open_edges": sum(
            count == 1
            for count in counts.values()
        ),
        "non_manifold_edges": sum(
            count > 2
            for count in counts.values()
        ),
    }


def test_densified_concave_profiled_bridge_deck_is_closed_and_manifold():
    geometry = AtlasBridgeGeometry(
        footprint=(
            (0.0, -4.0),
            (18.0, -4.0),
            (21.0, -7.0),
            (25.0, -7.0),
            (28.0, -4.0),
            (46.0, -4.0),
            (46.0, 4.0),
            (28.0, 4.0),
            (25.0, 7.0),
            (21.0, 7.0),
            (18.0, 4.0),
            (0.0, 4.0),
        ),
        height_m=8.0,
        landmark_kind="bridge",
        metadata={
            "bridge_deck_thickness_m": 1.0,
            "bridge_full_span_convex": True,
            "bridge_shore_top_m": 6.0,
        },
    )

    mesh = AtlasLandmarkGeometryMesher.build(geometry)
    topology = _mesh_edge_topology(mesh["triangles"])

    assert len(mesh["top"]) > len(geometry.footprint)
    assert topology["open_edges"] == 0
    assert topology["non_manifold_edges"] == 0
