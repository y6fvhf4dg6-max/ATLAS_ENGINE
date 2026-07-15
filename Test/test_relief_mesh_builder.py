import numpy as np
import pytest

from CORE.atlas_mesh_validator import (
    AtlasMeshValidator,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)


def _mesh():
    return AtlasReliefMeshBuilder.build(
        np.array(
            [
                [0.0, 0.5, 1.0],
                [0.25, 0.75, 0.5],
                [0.0, 0.25, 1.0],
            ]
        ),
        width_mm=20.0,
        depth_mm=10.0,
        base_thickness_mm=0.8,
        relief_height_mm=2.0,
    )


def test_builds_expected_grid_dimensions():
    mesh = _mesh()

    assert mesh["row_count"] == 3
    assert mesh["column_count"] == 3
    assert len(mesh["top_grid"]) == 3
    assert len(mesh["top_grid"][0]) == 3


def test_relief_height_is_mapped_to_z():
    mesh = _mesh()

    assert mesh["minimum_z"] == pytest.approx(
        0.0
    )
    assert mesh["maximum_z"] == pytest.approx(
        2.8
    )

    assert mesh["top_grid"][0][0][2] == (
        pytest.approx(0.8)
    )

    assert mesh["top_grid"][0][2][2] == (
        pytest.approx(2.8)
    )


def test_mesh_is_closed_and_manifold():
    mesh = _mesh()

    report = AtlasMeshValidator._topology_report(
        mesh
    )

    assert report["open_edge_count"] == 0
    assert (
        report["non_manifold_edge_count"]
        == 0
    )


def test_triangle_count_matches_grid_formula():
    mesh = _mesh()

    rows = mesh["row_count"]
    columns = mesh["column_count"]

    expected = (
        4 * (rows - 1) * (columns - 1)
        + 4 * (rows + columns - 2)
    )

    assert len(mesh["triangles"]) == expected


def test_origin_offsets_geometry():
    mesh = AtlasReliefMeshBuilder.build(
        [[0.0, 1.0], [1.0, 0.0]],
        width_mm=4.0,
        depth_mm=6.0,
        origin_x=10.0,
        origin_y=20.0,
        origin_z=3.0,
    )

    assert mesh["bottom_grid"][0][0] == (
        10.0,
        20.0,
        3.0,
    )

    assert mesh["top_grid"][1][1][0:2] == (
        14.0,
        26.0,
    )


def test_zero_relief_height_is_valid():
    mesh = AtlasReliefMeshBuilder.build(
        [[0.0, 1.0], [1.0, 0.0]],
        width_mm=5.0,
        depth_mm=5.0,
        relief_height_mm=0.0,
    )

    top_z_values = {
        point[2]
        for row in mesh["top_grid"]
        for point in row
    }

    assert top_z_values == {0.8}


def test_output_is_deterministic():
    arguments = {
        "height_map": [
            [0.0, 0.5],
            [1.0, 0.25],
        ],
        "width_mm": 8.0,
        "depth_mm": 6.0,
    }

    first = AtlasReliefMeshBuilder.build(
        **arguments
    )
    second = AtlasReliefMeshBuilder.build(
        **arguments
    )

    assert (
        first["triangles"]
        == second["triangles"]
    )


@pytest.mark.parametrize(
    "height_map",
    [
        [0.0, 1.0],
        [[0.0]],
        np.zeros((2, 2, 2)),
    ],
)
def test_rejects_invalid_height_map_shape(
    height_map,
):
    with pytest.raises(ValueError):
        AtlasReliefMeshBuilder.build(
            height_map,
            width_mm=5.0,
            depth_mm=5.0,
        )


@pytest.mark.parametrize(
    "height_map",
    [
        [[-0.01, 0.0], [0.5, 1.0]],
        [[0.0, 1.01], [0.5, 1.0]],
        [[0.0, np.nan], [0.5, 1.0]],
    ],
)
def test_rejects_invalid_height_values(
    height_map,
):
    with pytest.raises(ValueError):
        AtlasReliefMeshBuilder.build(
            height_map,
            width_mm=5.0,
            depth_mm=5.0,
        )


@pytest.mark.parametrize(
    "parameter,value",
    [
        ("width_mm", 0.0),
        ("depth_mm", 0.0),
        ("base_thickness_mm", 0.0),
        ("relief_height_mm", -0.1),
    ],
)
def test_rejects_invalid_dimensions(
    parameter,
    value,
):
    arguments = {
        "height_map": [
            [0.0, 1.0],
            [1.0, 0.0],
        ],
        "width_mm": 5.0,
        "depth_mm": 5.0,
    }

    arguments[parameter] = value

    with pytest.raises(ValueError):
        AtlasReliefMeshBuilder.build(
            **arguments
        )
