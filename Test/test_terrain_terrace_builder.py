import pytest

from CORE.atlas_terrain_terrace_builder import (
    AtlasTerrainTerraceBuilder,
)


def _top_points():
    return [
        [
            (0.0, 0.0, 0.80),
            (100.0, 0.0, 0.94),
            (200.0, 0.0, 1.07),
        ],
        [
            (0.0, 100.0, 1.22),
            (100.0, 100.0, 1.39),
            (200.0, 100.0, 1.55),
        ],
    ]


def test_quantize_z_uses_base_relative_terrace_levels():
    assert AtlasTerrainTerraceBuilder.quantize_z(
        z=0.80,
        base_z=0.80,
        terrace_step_mm=0.30,
    ) == pytest.approx(0.80)

    assert AtlasTerrainTerraceBuilder.quantize_z(
        z=0.94,
        base_z=0.80,
        terrace_step_mm=0.30,
    ) == pytest.approx(0.80)

    assert AtlasTerrainTerraceBuilder.quantize_z(
        z=1.07,
        base_z=0.80,
        terrace_step_mm=0.30,
    ) == pytest.approx(0.80)

    assert AtlasTerrainTerraceBuilder.quantize_z(
        z=1.22,
        base_z=0.80,
        terrace_step_mm=0.30,
    ) == pytest.approx(1.10)

    assert AtlasTerrainTerraceBuilder.quantize_z(
        z=1.39,
        base_z=0.80,
        terrace_step_mm=0.30,
    ) == pytest.approx(1.10)

    assert AtlasTerrainTerraceBuilder.quantize_z(
        z=1.55,
        base_z=0.80,
        terrace_step_mm=0.30,
    ) == pytest.approx(1.40)


def test_quantization_never_raises_ground_above_original_height():
    values = [
        0.80,
        0.81,
        0.94,
        1.09,
        1.10,
        1.39,
        1.70,
    ]

    for value in values:
        quantized = AtlasTerrainTerraceBuilder.quantize_z(
            z=value,
            base_z=0.80,
            terrace_step_mm=0.30,
        )

        assert quantized <= value + 1e-12


def test_quantize_top_points_preserves_xy_grid():
    result = AtlasTerrainTerraceBuilder.quantize_top_points(
        top_points=_top_points(),
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    assert [
        [(point[0], point[1]) for point in row]
        for row in result
    ] == [
        [(point[0], point[1]) for point in row]
        for row in _top_points()
    ]


def test_quantize_top_points_produces_expected_level_grid():
    result = AtlasTerrainTerraceBuilder.quantize_top_points(
        top_points=_top_points(),
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    actual_levels = [
        [point[2] for point in row]
        for row in result
    ]

    expected_levels = [
        [0.80, 0.80, 0.80],
        [1.10, 1.10, 1.40],
    ]

    assert len(actual_levels) == len(expected_levels)

    for actual_row, expected_row in zip(
        actual_levels,
        expected_levels,
    ):
        assert actual_row == pytest.approx(
            expected_row,
            abs=1e-12,
        )


def test_flat_ground_remains_flat():
    flat = [
        [
            (0.0, 0.0, 1.40),
            (100.0, 0.0, 1.40),
        ],
        [
            (0.0, 100.0, 1.40),
            (100.0, 100.0, 1.40),
        ],
    ]

    result = AtlasTerrainTerraceBuilder.quantize_top_points(
        top_points=flat,
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    assert result == flat


def test_quantization_is_deterministic():
    first = AtlasTerrainTerraceBuilder.quantize_top_points(
        top_points=_top_points(),
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    second = AtlasTerrainTerraceBuilder.quantize_top_points(
        top_points=_top_points(),
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    assert first == second


def test_invalid_terrace_step_is_rejected():
    with pytest.raises(
        ValueError,
        match="terrace_step_mm",
    ):
        AtlasTerrainTerraceBuilder.quantize_top_points(
            top_points=_top_points(),
            base_z=0.80,
            terrace_step_mm=0.0,
        )


def _terrace_cell_top_points():
    return [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 0.90),
            (20.0, 0.0, 1.30),
        ],
        [
            (0.0, 10.0, 0.90),
            (10.0, 10.0, 1.00),
            (20.0, 10.0, 1.40),
        ],
        [
            (0.0, 20.0, 1.20),
            (10.0, 20.0, 1.30),
            (20.0, 20.0, 1.70),
        ],
    ]


def test_build_cell_level_grid_returns_one_level_per_grid_cell():
    result = AtlasTerrainTerraceBuilder.build_cell_level_grid(
        top_points=_terrace_cell_top_points(),
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    assert len(result) == 2
    assert all(len(row) == 2 for row in result)


def test_cell_level_uses_quantized_average_corner_height():
    result = AtlasTerrainTerraceBuilder.build_cell_level_grid(
        top_points=_terrace_cell_top_points(),
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    expected = [
        [0.80, 1.10],
        [1.10, 1.10],
    ]

    for actual_row, expected_row in zip(
        result,
        expected,
    ):
        assert actual_row == pytest.approx(
            expected_row,
            abs=1e-12,
        )


def test_flat_cells_remain_on_same_terrace_level():
    top_points = [
        [
            (0.0, 0.0, 1.40),
            (10.0, 0.0, 1.40),
            (20.0, 0.0, 1.40),
        ],
        [
            (0.0, 10.0, 1.40),
            (10.0, 10.0, 1.40),
            (20.0, 10.0, 1.40),
        ],
    ]

    result = AtlasTerrainTerraceBuilder.build_cell_level_grid(
        top_points=top_points,
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    assert len(result) == 1
    assert result[0] == pytest.approx(
        [1.40, 1.40],
        abs=1e-12,
    )


def test_cell_level_grid_rejects_ragged_point_rows():
    ragged = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 0.80),
        ],
        [
            (0.0, 10.0, 0.80),
        ],
    ]

    with pytest.raises(
        ValueError,
        match="rectangular",
    ):
        AtlasTerrainTerraceBuilder.build_cell_level_grid(
            top_points=ragged,
            base_z=0.80,
            terrace_step_mm=0.30,
        )


def test_cell_level_grid_requires_at_least_two_rows_and_columns():
    with pytest.raises(
        ValueError,
        match="at least 2",
    ):
        AtlasTerrainTerraceBuilder.build_cell_level_grid(
            top_points=[
                [
                    (0.0, 0.0, 0.80),
                ],
            ],
            base_z=0.80,
            terrace_step_mm=0.30,
        )


def test_quantize_z_preserves_level_boundary_with_float_rounding():
    boundary_value = (
        0.90
        + 1.00
        + 1.20
        + 1.30
    ) / 4.0

    assert boundary_value == pytest.approx(
        1.10,
        abs=1e-12,
    )

    result = AtlasTerrainTerraceBuilder.quantize_z(
        z=boundary_value,
        base_z=0.80,
        terrace_step_mm=0.30,
    )

    assert result == pytest.approx(
        1.10,
        abs=1e-12,
    )



def _two_cell_point_grid():
    return [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 0.80),
            (20.0, 0.0, 0.80),
        ],
        [
            (0.0, 10.0, 0.80),
            (10.0, 10.0, 0.80),
            (20.0, 10.0, 0.80),
        ],
    ]


def test_equal_level_cells_create_only_horizontal_top_triangles():
    triangles = (
        AtlasTerrainTerraceBuilder
        .build_terraced_surface_triangles(
            top_points=_two_cell_point_grid(),
            cell_levels=[
                [0.80, 0.80],
            ],
        )
    )

    assert len(triangles) == 4

    assert all(
        len({point[2] for point in triangle}) == 1
        for triangle in triangles
    )

    assert {
        point[2]
        for triangle in triangles
        for point in triangle
    } == {0.80}


def test_different_level_cells_add_vertical_riser_triangles():
    triangles = (
        AtlasTerrainTerraceBuilder
        .build_terraced_surface_triangles(
            top_points=_two_cell_point_grid(),
            cell_levels=[
                [0.80, 1.10],
            ],
        )
    )

    assert len(triangles) == 6

    horizontal = [
        triangle
        for triangle in triangles
        if len({point[2] for point in triangle}) == 1
    ]

    vertical = [
        triangle
        for triangle in triangles
        if len({point[2] for point in triangle}) > 1
    ]

    assert len(horizontal) == 4
    assert len(vertical) == 2


def test_vertical_riser_uses_shared_cell_edge():
    triangles = (
        AtlasTerrainTerraceBuilder
        .build_terraced_surface_triangles(
            top_points=_two_cell_point_grid(),
            cell_levels=[
                [0.80, 1.10],
            ],
        )
    )

    vertical = [
        triangle
        for triangle in triangles
        if len({point[2] for point in triangle}) > 1
    ]

    vertices = {
        point
        for triangle in vertical
        for point in triangle
    }

    assert vertices == {
        (10.0, 0.0, 0.80),
        (10.0, 10.0, 0.80),
        (10.0, 0.0, 1.10),
        (10.0, 10.0, 1.10),
    }


def test_vertical_riser_is_not_created_for_equal_levels():
    triangles = (
        AtlasTerrainTerraceBuilder
        .build_terraced_surface_triangles(
            top_points=_two_cell_point_grid(),
            cell_levels=[
                [1.10, 1.10],
            ],
        )
    )

    assert all(
        len({point[2] for point in triangle}) == 1
        for triangle in triangles
    )


def test_surface_geometry_supports_vertical_cell_neighbors():
    top_points = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 0.80),
        ],
        [
            (0.0, 10.0, 0.80),
            (10.0, 10.0, 0.80),
        ],
        [
            (0.0, 20.0, 0.80),
            (10.0, 20.0, 0.80),
        ],
    ]

    triangles = (
        AtlasTerrainTerraceBuilder
        .build_terraced_surface_triangles(
            top_points=top_points,
            cell_levels=[
                [0.80],
                [1.10],
            ],
        )
    )

    assert len(triangles) == 6

    vertical_vertices = {
        point
        for triangle in triangles
        if len({point[2] for point in triangle}) > 1
        for point in triangle
    }

    assert vertical_vertices == {
        (0.0, 10.0, 0.80),
        (10.0, 10.0, 0.80),
        (0.0, 10.0, 1.10),
        (10.0, 10.0, 1.10),
    }


def test_surface_geometry_rejects_cell_level_dimension_mismatch():
    with pytest.raises(
        ValueError,
        match="cell_levels",
    ):
        (
            AtlasTerrainTerraceBuilder
            .build_terraced_surface_triangles(
                top_points=_two_cell_point_grid(),
                cell_levels=[
                    [0.80],
                ],
            )
        )


def _edge_statistics(triangles):
    edge_counts = {}

    for triangle in triangles:
        for index in range(3):
            point_a = triangle[index]
            point_b = triangle[(index + 1) % 3]

            edge = tuple(sorted((
                tuple(round(value, 12) for value in point_a),
                tuple(round(value, 12) for value in point_b),
            )))

            edge_counts[edge] = edge_counts.get(edge, 0) + 1

    open_edges = [
        edge
        for edge, count in edge_counts.items()
        if count == 1
    ]

    non_manifold_edges = [
        edge
        for edge, count in edge_counts.items()
        if count > 2
    ]

    return {
        "open_edges": open_edges,
        "non_manifold_edges": non_manifold_edges,
    }


def test_closed_single_cell_terrace_is_watertight():
    top_points = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 0.80),
        ],
        [
            (0.0, 10.0, 0.80),
            (10.0, 10.0, 0.80),
        ],
    ]

    mesh = AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
        top_points=top_points,
        cell_levels=[
            [1.10],
        ],
        bottom_z=0.0,
    )

    statistics = _edge_statistics(
        mesh["triangles"]
    )

    assert statistics["open_edges"] == []
    assert statistics["non_manifold_edges"] == []


def test_closed_single_cell_contains_expected_triangle_groups():
    top_points = [
        [
            (0.0, 0.0, 0.80),
            (10.0, 0.0, 0.80),
        ],
        [
            (0.0, 10.0, 0.80),
            (10.0, 10.0, 0.80),
        ],
    ]

    mesh = AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
        top_points=top_points,
        cell_levels=[
            [1.10],
        ],
        bottom_z=0.0,
    )

    # 2 top + 2 bottom + 8 perimeter-wall triangles.
    assert len(mesh["triangles"]) == 12


def test_closed_two_level_terrace_remains_watertight():
    mesh = AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
        top_points=_two_cell_point_grid(),
        cell_levels=[
            [0.80, 1.10],
        ],
        bottom_z=0.0,
    )

    statistics = _edge_statistics(
        mesh["triangles"]
    )

    assert statistics["open_edges"] == []
    assert statistics["non_manifold_edges"] == []


def test_closed_two_level_terrace_contains_internal_riser():
    mesh = AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
        top_points=_two_cell_point_grid(),
        cell_levels=[
            [0.80, 1.10],
        ],
        bottom_z=0.0,
    )

    internal_riser_vertices = {
        point
        for triangle in mesh["triangles"]
        if all(point[0] == 10.0 for point in triangle)
        for point in triangle
    }

    assert {
        (10.0, 0.0, 0.80),
        (10.0, 10.0, 0.80),
        (10.0, 0.0, 1.10),
        (10.0, 10.0, 1.10),
    }.issubset(internal_riser_vertices)


def test_closed_mesh_preserves_product_xy_bounds():
    mesh = AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
        top_points=_two_cell_point_grid(),
        cell_levels=[
            [0.80, 1.10],
        ],
        bottom_z=0.0,
    )

    vertices = [
        point
        for triangle in mesh["triangles"]
        for point in triangle
    ]

    assert min(point[0] for point in vertices) == 0.0
    assert max(point[0] for point in vertices) == 20.0
    assert min(point[1] for point in vertices) == 0.0
    assert max(point[1] for point in vertices) == 10.0


def test_closed_mesh_records_terrace_metadata():
    mesh = AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
        top_points=_two_cell_point_grid(),
        cell_levels=[
            [0.80, 1.10],
        ],
        bottom_z=0.0,
        terrace_step_mm=0.30,
    )

    assert mesh["type"] == "terrain_terraced_closed_slab"
    assert mesh["metadata"]["closed"] is True
    assert mesh["metadata"]["terraced"] is True
    assert mesh["metadata"]["terrace_step_mm"] == pytest.approx(
        0.30
    )
    assert mesh["metadata"]["cell_rows"] == 1
    assert mesh["metadata"]["cell_columns"] == 2
    assert mesh["metadata"]["terrace_level_count"] == 2
    assert mesh["metadata"]["triangle_count"] == len(
        mesh["triangles"]
    )


def test_closed_mesh_rejects_bottom_at_or_above_terrace():
    with pytest.raises(
        ValueError,
        match="bottom_z",
    ):
        AtlasTerrainTerraceBuilder.build_closed_terraced_mesh(
            top_points=_two_cell_point_grid(),
            cell_levels=[
                [0.80, 1.10],
            ],
            bottom_z=0.80,
        )
