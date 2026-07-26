import pytest

from CORE.atlas_foundation_scene_xy_mesh_clipper import (
    AtlasFoundationSceneXYMeshClipper,
)


def _triangle_mesh(triangle):
    return {
        "type": "test_mesh",
        "triangles": [triangle],
    }


def test_triangle_fully_inside_is_preserved():
    mesh = _triangle_mesh(
        (
            (2.0, 2.0, 1.0),
            (8.0, 2.0, 1.0),
            (5.0, 8.0, 1.0),
        )
    )

    result = AtlasFoundationSceneXYMeshClipper.clip_mesh(
        mesh=mesh,
        min_x=0.0,
        max_x=10.0,
        min_y=0.0,
        max_y=10.0,
    )

    assert result["triangles"] == mesh["triangles"]


def test_triangle_fully_outside_is_removed():
    mesh = _triangle_mesh(
        (
            (-8.0, 2.0, 1.0),
            (-2.0, 2.0, 1.0),
            (-5.0, 8.0, 1.0),
        )
    )

    result = AtlasFoundationSceneXYMeshClipper.clip_mesh(
        mesh=mesh,
        min_x=0.0,
        max_x=10.0,
        min_y=0.0,
        max_y=10.0,
    )

    assert result is None


def test_triangle_crossing_left_boundary_is_geometrically_clipped():
    mesh = _triangle_mesh(
        (
            (-5.0, 2.0, 1.0),
            (5.0, 2.0, 1.0),
            (5.0, 8.0, 1.0),
        )
    )

    result = AtlasFoundationSceneXYMeshClipper.clip_mesh(
        mesh=mesh,
        min_x=0.0,
        max_x=10.0,
        min_y=0.0,
        max_y=10.0,
    )

    assert result is not None
    assert len(result["triangles"]) == 2

    vertices = [
        point
        for triangle in result["triangles"]
        for point in triangle
    ]

    assert min(point[0] for point in vertices) == pytest.approx(0.0)
    assert max(point[0] for point in vertices) == pytest.approx(5.0)


def test_clipping_interpolates_z_at_boundary():
    mesh = _triangle_mesh(
        (
            (-5.0, 2.0, 0.0),
            (5.0, 2.0, 10.0),
            (5.0, 8.0, 10.0),
        )
    )

    result = AtlasFoundationSceneXYMeshClipper.clip_mesh(
        mesh=mesh,
        min_x=0.0,
        max_x=10.0,
        min_y=0.0,
        max_y=10.0,
    )

    boundary_vertices = {
        (
            round(point[0], 8),
            round(point[1], 8),
            round(point[2], 8),
        )
        for triangle in result["triangles"]
        for point in triangle
        if abs(point[0]) <= 1e-8
    }

    assert (0.0, 2.0, 5.0) in boundary_vertices
    assert (0.0, 5.0, 5.0) in boundary_vertices


def test_mesh_metadata_is_preserved():
    mesh = {
        "type": "bridge",
        "landmark_id": 123,
        "tags": {"name": "Boundary Bridge"},
        "triangles": [
            (
                (-2.0, 2.0, 1.0),
                (5.0, 2.0, 1.0),
                (5.0, 8.0, 1.0),
            )
        ],
    }

    result = AtlasFoundationSceneXYMeshClipper.clip_mesh(
        mesh=mesh,
        min_x=0.0,
        max_x=10.0,
        min_y=0.0,
        max_y=10.0,
    )

    assert result["type"] == "bridge"
    assert result["landmark_id"] == 123
    assert result["tags"] == {"name": "Boundary Bridge"}
