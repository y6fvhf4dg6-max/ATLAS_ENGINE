from CORE.atlas_foundation_sampler import AtlasFoundationSampler
from CORE.atlas_foundation_surface_builder import (
    AtlasFoundationSurfaceBuilder,
)


def _terrain_mesh():
    top_points = []

    for y in range(5):
        row = []

        for x in range(5):
            row.append(
                (
                    float(x),
                    float(y),
                    float(x + y),
                )
            )

        top_points.append(row)

    return {
        "top_points": top_points,
        "metadata": {
            "size_x_mm": 4.0,
            "size_y_mm": 4.0,
        },
    }


def test_sample_polygon_excludes_points_outside_real_footprint():
    terrain_mesh = _terrain_mesh()

    footprint = [
        (2.0, 2.0),
        (4.0, 2.0),
        (4.0, 4.0),
        (2.0, 4.0),
    ]

    values = AtlasFoundationSampler.sample_polygon(
        terrain_mesh=terrain_mesh,
        footprint_points=footprint,
        sample_grid=5,
    )

    assert values
    assert min(values) >= 4.0
    assert max(values) == 8.0


def test_surface_uses_robust_lower_percentile_instead_of_minimum():
    terrain_mesh = _terrain_mesh()

    footprint = [
        (0.0, 0.0),
        (4.0, 0.0),
        (4.0, 4.0),
        (0.0, 4.0),
    ]

    surface = AtlasFoundationSurfaceBuilder.build_surface(
        terrain_mesh=terrain_mesh,
        bounds={
            "min_x": 0.0,
            "max_x": 4.0,
            "min_y": 0.0,
            "max_y": 4.0,
        },
        footprint_points=footprint,
        sample_grid=5,
        embed_depth_mm=0.30,
    )

    assert surface is not None
    assert surface["placement_percentile"] == 0.10
    assert surface["reference_z"] > surface["lowest_z"]
    assert surface["foundation_z"] == (
        surface["reference_z"] - 0.30
    )


def test_surface_keeps_legacy_bounds_sampling_without_footprint():
    terrain_mesh = _terrain_mesh()

    surface = AtlasFoundationSurfaceBuilder.build_surface(
        terrain_mesh=terrain_mesh,
        bounds={
            "min_x": 0.0,
            "max_x": 4.0,
            "min_y": 0.0,
            "max_y": 4.0,
        },
        sample_grid=5,
        embed_depth_mm=0.30,
    )

    assert surface is not None
    assert surface["sample_mode"] == "bounds"
