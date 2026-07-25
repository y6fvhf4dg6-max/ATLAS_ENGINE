import pytest

from CORE.atlas_foundation_sampler import (
    AtlasFoundationSampler,
)


def _terraced_mesh():
    return {
        "type": "terrain_terraced_closed_slab",
        "top_points": [
            [
                (0.0, 0.0, 0.80),
                (10.0, 0.0, 0.80),
                (20.0, 0.0, 1.10),
            ],
            [
                (0.0, 10.0, 0.80),
                (10.0, 10.0, 0.80),
                (20.0, 10.0, 1.10),
            ],
            [
                (0.0, 20.0, 1.10),
                (10.0, 20.0, 1.10),
                (20.0, 20.0, 1.40),
            ],
        ],
        "cell_levels": [
            [0.80, 1.10],
            [1.10, 1.40],
        ],
        "metadata": {
            "size_mm": 20.0,
            "size_x_mm": 20.0,
            "size_y_mm": 20.0,
            "closed": True,
            "terraced": True,
        },
    }


def _normal_mesh():
    return {
        "type": "terrain_closed_slab",
        "top_points": [
            [
                (0.0, 0.0, 0.0),
                (10.0, 0.0, 10.0),
            ],
            [
                (0.0, 10.0, 10.0),
                (10.0, 10.0, 20.0),
            ],
        ],
        "metadata": {
            "size_mm": 10.0,
            "size_x_mm": 10.0,
            "size_y_mm": 10.0,
        },
    }


def test_terraced_sampler_returns_constant_level_inside_each_cell():
    mesh = _terraced_mesh()

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=2.0,
        y=3.0,
    ) == pytest.approx(0.80)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=8.0,
        y=9.0,
    ) == pytest.approx(0.80)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=12.0,
        y=4.0,
    ) == pytest.approx(1.10)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=5.0,
        y=15.0,
    ) == pytest.approx(1.10)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=18.0,
        y=18.0,
    ) == pytest.approx(1.40)


def test_terraced_sampler_does_not_interpolate_across_riser():
    mesh = _terraced_mesh()

    left = AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=9.999,
        y=5.0,
    )

    right = AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=10.001,
        y=5.0,
    )

    assert left == pytest.approx(0.80)
    assert right == pytest.approx(1.10)


def test_terraced_sampler_assigns_internal_boundary_to_next_cell():
    mesh = _terraced_mesh()

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=10.0,
        y=5.0,
    ) == pytest.approx(1.10)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=5.0,
        y=10.0,
    ) == pytest.approx(1.10)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=10.0,
        y=10.0,
    ) == pytest.approx(1.40)


def test_terraced_sampler_maps_maximum_bounds_to_last_cell():
    mesh = _terraced_mesh()

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=20.0,
        y=5.0,
    ) == pytest.approx(1.10)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=5.0,
        y=20.0,
    ) == pytest.approx(1.10)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=20.0,
        y=20.0,
    ) == pytest.approx(1.40)


def test_terraced_sampler_clamps_coordinates_to_product_bounds():
    mesh = _terraced_mesh()

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=-5.0,
        y=-2.0,
    ) == pytest.approx(0.80)

    assert AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=25.0,
        y=25.0,
    ) == pytest.approx(1.40)


def test_normal_terrain_keeps_existing_bilinear_sampling():
    mesh = _normal_mesh()

    result = AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=5.0,
        y=5.0,
    )

    assert result == pytest.approx(10.0)


def test_missing_cell_levels_falls_back_to_existing_sampling():
    mesh = _normal_mesh()
    mesh["type"] = "terrain_terraced_closed_slab"
    mesh["metadata"]["terraced"] = True

    result = AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=5.0,
        y=5.0,
    )

    assert result == pytest.approx(10.0)


def test_invalid_cell_level_dimensions_fall_back_safely():
    mesh = _terraced_mesh()
    mesh["cell_levels"] = [
        [0.80],
    ]

    result = AtlasFoundationSampler.terrain_z_at_xy(
        terrain_mesh=mesh,
        x=10.0,
        y=10.0,
    )

    assert result == pytest.approx(0.80)
