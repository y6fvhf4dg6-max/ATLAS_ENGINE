import numpy as np
import pytest

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from fixtures.relief.relief_fixture_catalog import (
    load_fixture,
)


def _build_zero_relief(
    height_map,
    *,
    width_mm=12.0,
    depth_mm=8.0,
    base_thickness_mm=0.8,
    origin_x=0.0,
    origin_y=0.0,
    origin_z=0.0,
):
    return AtlasReliefMeshBuilder.build(
        height_map,
        width_mm=width_mm,
        depth_mm=depth_mm,
        base_thickness_mm=base_thickness_mm,
        relief_height_mm=0.0,
        origin_x=origin_x,
        origin_y=origin_y,
        origin_z=origin_z,
    )


def _triangle_area(triangle):
    points = np.asarray(
        triangle,
        dtype=np.float64,
    )

    first_edge = points[1] - points[0]
    second_edge = points[2] - points[0]

    return 0.5 * float(
        np.linalg.norm(
            np.cross(
                first_edge,
                second_edge,
            )
        )
    )


def _triangle_normal_z(triangle):
    points = np.asarray(
        triangle,
        dtype=np.float64,
    )

    first_edge = points[1] - points[0]
    second_edge = points[2] - points[0]

    return float(
        np.cross(
            first_edge,
            second_edge,
        )[2]
    )


@pytest.mark.parametrize(
    "shape",
    [
        (2, 2),
        (2, 3),
        (3, 2),
        (3, 4),
        (5, 6),
    ],
)
def test_zero_relief_mesh_is_closed_and_manifold(
    shape,
):
    values = np.linspace(
        0.0,
        1.0,
        shape[0] * shape[1],
        dtype=np.float64,
    ).reshape(shape)

    mesh = _build_zero_relief(values)

    report = AtlasMeshValidator._topology_report(
        mesh
    )

    assert report["open_edge_count"] == 0
    assert report["non_manifold_edge_count"] == 0


@pytest.mark.parametrize(
    "shape",
    [
        (2, 2),
        (2, 5),
        (5, 2),
        (4, 7),
    ],
)
def test_zero_relief_triangle_count_matches_formula(
    shape,
):
    values = np.zeros(
        shape,
        dtype=np.float64,
    )

    mesh = _build_zero_relief(values)

    rows, columns = shape

    expected_triangle_count = (
        4 * (rows - 1) * (columns - 1)
        + 4 * (rows + columns - 2)
    )

    assert (
        len(mesh["triangles"])
        == expected_triangle_count
    )


def test_zero_relief_has_planar_top_and_bottom():
    mesh = _build_zero_relief(
        load_fixture("asymmetric_surface_3x4"),
        base_thickness_mm=1.25,
        origin_z=3.5,
    )

    bottom_z_values = {
        point[2]
        for row in mesh["bottom_grid"]
        for point in row
    }

    top_z_values = {
        point[2]
        for row in mesh["top_grid"]
        for point in row
    }

    assert bottom_z_values == {3.5}
    assert top_z_values == {4.75}
    assert mesh["minimum_z"] == pytest.approx(
        3.5
    )
    assert mesh["maximum_z"] == pytest.approx(
        4.75
    )


def test_zero_relief_contains_no_degenerate_triangles():
    mesh = _build_zero_relief(
        load_fixture("asymmetric_surface_3x4")
    )

    triangle_areas = [
        _triangle_area(triangle)
        for triangle in mesh["triangles"]
    ]

    assert min(triangle_areas) > 0.0
    assert np.all(
        np.isfinite(triangle_areas)
    )


def test_zero_relief_top_and_bottom_winding_are_opposite():
    values = load_fixture(
        "asymmetric_surface_3x4"
    )

    mesh = _build_zero_relief(values)

    rows = mesh["row_count"]
    columns = mesh["column_count"]

    surface_triangle_count = (
        2 * (rows - 1) * (columns - 1)
    )

    top_triangles = mesh["triangles"][
        :surface_triangle_count
    ]

    bottom_triangles = mesh["triangles"][
        surface_triangle_count:
        2 * surface_triangle_count
    ]

    assert all(
        _triangle_normal_z(triangle) > 0.0
        for triangle in top_triangles
    )

    assert all(
        _triangle_normal_z(triangle) < 0.0
        for triangle in bottom_triangles
    )


def test_zero_relief_geometry_is_independent_of_height_values():
    first = _build_zero_relief(
        load_fixture("flat_3x3")
    )

    second = _build_zero_relief(
        load_fixture("horizontal_ramp_3x3")
    )

    assert first["triangles"] == second["triangles"]
    assert first["bottom_grid"] == second["bottom_grid"]
    assert first["top_grid"] == second["top_grid"]


def test_zero_relief_preserves_origin_and_dimensions():
    mesh = _build_zero_relief(
        load_fixture("small_reflect_2x3"),
        width_mm=17.5,
        depth_mm=9.25,
        base_thickness_mm=1.1,
        origin_x=-4.0,
        origin_y=6.5,
        origin_z=2.25,
    )

    assert mesh["bottom_grid"][0][0] == (
        -4.0,
        6.5,
        2.25,
    )

    assert mesh["bottom_grid"][-1][-1] == (
        13.5,
        15.75,
        2.25,
    )

    assert mesh["top_grid"][0][0] == (
        -4.0,
        6.5,
        3.35,
    )

    assert mesh["top_grid"][-1][-1] == (
        13.5,
        15.75,
        3.35,
    )
