import numpy as np
import pytest

from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from fixtures.relief.relief_fixture_catalog import (
    load_fixture,
)


def _triangle_normal(triangle):
    points = np.asarray(
        triangle,
        dtype=np.float64,
    )

    first_edge = points[1] - points[0]
    second_edge = points[2] - points[0]

    return np.cross(
        first_edge,
        second_edge,
    )


def _surface_triangle_count(
    rows,
    columns,
):
    return (
        2
        * (rows - 1)
        * (columns - 1)
    )


def _build_mesh(
    height_map,
    *,
    width_mm=18.0,
    depth_mm=12.0,
    base_thickness_mm=0.8,
    relief_height_mm=2.5,
    origin_x=0.0,
    origin_y=0.0,
    origin_z=0.0,
):
    return AtlasReliefMeshBuilder.build(
        height_map,
        width_mm=width_mm,
        depth_mm=depth_mm,
        base_thickness_mm=base_thickness_mm,
        relief_height_mm=relief_height_mm,
        origin_x=origin_x,
        origin_y=origin_y,
        origin_z=origin_z,
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "horizontal_ramp_3x3",
        "vertical_ramp_3x3",
        "asymmetric_surface_3x4",
        "checkerboard_4x4",
    ],
)
def test_top_surface_triangles_face_upward(
    fixture_name,
):
    mesh = _build_mesh(
        load_fixture(fixture_name)
    )

    surface_count = _surface_triangle_count(
        mesh["row_count"],
        mesh["column_count"],
    )

    top_triangles = mesh["triangles"][
        :surface_count
    ]

    normals = [
        _triangle_normal(triangle)
        for triangle in top_triangles
    ]

    assert all(
        normal[2] > 0.0
        for normal in normals
    )

    assert all(
        np.all(np.isfinite(normal))
        for normal in normals
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "horizontal_ramp_3x3",
        "vertical_ramp_3x3",
        "asymmetric_surface_3x4",
        "checkerboard_4x4",
    ],
)
def test_bottom_surface_triangles_face_downward(
    fixture_name,
):
    mesh = _build_mesh(
        load_fixture(fixture_name)
    )

    surface_count = _surface_triangle_count(
        mesh["row_count"],
        mesh["column_count"],
    )

    bottom_triangles = mesh["triangles"][
        surface_count:
        2 * surface_count
    ]

    normals = [
        _triangle_normal(triangle)
        for triangle in bottom_triangles
    ]

    assert all(
        normal[2] < 0.0
        for normal in normals
    )

    assert all(
        np.all(np.isfinite(normal))
        for normal in normals
    )


def test_perimeter_wall_normals_face_outward():
    mesh = _build_mesh(
        load_fixture(
            "asymmetric_surface_3x4"
        ),
        width_mm=20.0,
        depth_mm=10.0,
        origin_x=-7.0,
        origin_y=4.0,
        origin_z=1.5,
    )

    rows = mesh["row_count"]
    columns = mesh["column_count"]

    surface_count = _surface_triangle_count(
        rows,
        columns,
    )

    wall_triangles = mesh["triangles"][
        2 * surface_count:
    ]

    south_count = 2 * (columns - 1)
    east_count = 2 * (rows - 1)
    north_count = 2 * (columns - 1)
    west_count = 2 * (rows - 1)

    south = wall_triangles[
        :south_count
    ]

    east_start = south_count
    east_end = east_start + east_count
    east = wall_triangles[
        east_start:east_end
    ]

    north_start = east_end
    north_end = north_start + north_count
    north = wall_triangles[
        north_start:north_end
    ]

    west_start = north_end
    west_end = west_start + west_count
    west = wall_triangles[
        west_start:west_end
    ]

    assert len(wall_triangles) == (
        south_count
        + east_count
        + north_count
        + west_count
    )

    assert all(
        _triangle_normal(triangle)[1] < 0.0
        for triangle in south
    )

    assert all(
        _triangle_normal(triangle)[0] > 0.0
        for triangle in east
    )

    assert all(
        _triangle_normal(triangle)[1] > 0.0
        for triangle in north
    )

    assert all(
        _triangle_normal(triangle)[0] < 0.0
        for triangle in west
    )


@pytest.mark.parametrize(
    "origin",
    [
        (0.0, 0.0, 0.0),
        (-15.5, 8.25, 3.0),
        (120.0, -75.0, -2.5),
    ],
)
def test_triangle_winding_is_origin_independent(
    origin,
):
    mesh = _build_mesh(
        load_fixture(
            "asymmetric_surface_3x4"
        ),
        origin_x=origin[0],
        origin_y=origin[1],
        origin_z=origin[2],
    )

    surface_count = _surface_triangle_count(
        mesh["row_count"],
        mesh["column_count"],
    )

    top_triangles = mesh["triangles"][
        :surface_count
    ]

    bottom_triangles = mesh["triangles"][
        surface_count:
        2 * surface_count
    ]

    assert all(
        _triangle_normal(triangle)[2] > 0.0
        for triangle in top_triangles
    )

    assert all(
        _triangle_normal(triangle)[2] < 0.0
        for triangle in bottom_triangles
    )


def test_all_triangle_normals_are_nonzero_and_finite():
    mesh = _build_mesh(
        load_fixture(
            "asymmetric_surface_3x4"
        )
    )

    normals = [
        _triangle_normal(triangle)
        for triangle in mesh["triangles"]
    ]

    magnitudes = [
        float(np.linalg.norm(normal))
        for normal in normals
    ]

    assert all(
        magnitude > 0.0
        for magnitude in magnitudes
    )

    assert np.all(
        np.isfinite(magnitudes)
    )
