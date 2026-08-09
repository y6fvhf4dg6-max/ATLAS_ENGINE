import copy

import pytest

from CORE.atlas_terrain_presentation_surface_regularizer import (
    AtlasTerrainPresentationSurfaceRegularizer,
)


def _source_mesh():
    return {
        "type": "terrain_closed_slab",
        "top_points": [
            [
                (0.0, 0.0, 1.0),
                (1.0, 0.0, 1.0),
                (2.0, 0.0, 1.0),
            ],
            [
                (0.0, 1.0, 1.0),
                (1.0, 1.0, 2.0),
                (2.0, 1.0, 1.0),
            ],
            [
                (0.0, 2.0, 1.0),
                (1.0, 2.0, 1.0),
                (2.0, 2.0, 1.0),
            ],
        ],
        "bottom_points": [
            [
                (0.0, 0.0, 0.0),
                (1.0, 0.0, 0.0),
                (2.0, 0.0, 0.0),
            ],
            [
                (0.0, 1.0, 0.0),
                (1.0, 1.0, 0.0),
                (2.0, 1.0, 0.0),
            ],
            [
                (0.0, 2.0, 0.0),
                (1.0, 2.0, 0.0),
                (2.0, 2.0, 0.0),
            ],
        ],
        "triangles": [],
        "grid": {
            "heights": [
                [100.0, 100.0, 100.0],
                [100.0, 105.5, 100.0],
                [100.0, 100.0, 100.0],
            ],
            "min_height_m": 100.0,
            "max_height_m": 105.5,
            "delta_height_m": 5.5,
        },
        "metadata": {
            "grid_size": 3,
            "size_mm": 2.0,
            "size_x_mm": 2.0,
            "size_y_mm": 2.0,
            "z_scale": 5500.0,
            "bottom_z": 0.0,
            "min_height_m": 100.0,
            "max_height_m": 105.5,
            "delta_height_m": 5.5,
            "closed": True,
        },
    }


def test_regularizer_preserves_canonical_terrain_truth():
    source = _source_mesh()
    source_before = copy.deepcopy(source)

    result = (
        AtlasTerrainPresentationSurfaceRegularizer.regularize(
            mesh=source,
            passes=1,
            strength=0.50,
        )
    )

    assert source == source_before
    assert result["grid"] == source_before["grid"]

    assert result["metadata"]["min_height_m"] == pytest.approx(100.0)
    assert result["metadata"]["max_height_m"] == pytest.approx(105.5)
    assert result["metadata"]["delta_height_m"] == pytest.approx(5.5)


def test_regularizer_changes_only_interior_presentation_surface():
    source = _source_mesh()

    result = (
        AtlasTerrainPresentationSurfaceRegularizer.regularize(
            mesh=source,
            passes=1,
            strength=0.50,
        )
    )

    assert result["top_points"] == source["top_points"]
    assert result["bottom_points"] == source["bottom_points"]

    presentation = result["presentation_top_points"]

    assert presentation[0] == source["top_points"][0]
    assert presentation[-1] == source["top_points"][-1]

    assert presentation[1][0] == source["top_points"][1][0]
    assert presentation[1][-1] == source["top_points"][1][-1]

    assert presentation[1][1][2] < 2.0
    assert presentation[1][1][2] > 1.0

    assert result["metadata"]["presentation_regularized"] is True
    assert result["metadata"]["presentation_regularization_passes"] == 1
    assert result["metadata"]["presentation_regularization_strength"] == (
        pytest.approx(0.50)
    )


def test_regularizer_rebuilds_closed_mesh_triangles_from_presentation_surface():
    from CORE.atlas_terrain_mesh_generator import (
        AtlasTerrainMeshGenerator,
    )

    source = _source_mesh()

    source["triangles"] = [
        *AtlasTerrainMeshGenerator.build_surface_triangles(
            points=source["top_points"],
            grid_size=3,
        ),
        *AtlasTerrainMeshGenerator.build_bottom_triangles(
            bottom_points=source["bottom_points"],
            grid_size=3,
        ),
        *AtlasTerrainMeshGenerator.build_side_wall_triangles(
            top_points=source["top_points"],
            bottom_points=source["bottom_points"],
            grid_size=3,
        ),
    ]

    original_triangles = copy.deepcopy(
        source["triangles"]
    )

    result = (
        AtlasTerrainPresentationSurfaceRegularizer.regularize(
            mesh=source,
            passes=1,
            strength=0.50,
        )
    )

    expected_triangles = [
        *AtlasTerrainMeshGenerator.build_surface_triangles(
            points=result["presentation_top_points"],
            grid_size=3,
        ),
        *AtlasTerrainMeshGenerator.build_bottom_triangles(
            bottom_points=result["bottom_points"],
            grid_size=3,
        ),
        *AtlasTerrainMeshGenerator.build_side_wall_triangles(
            top_points=result["top_points"],
            bottom_points=result["bottom_points"],
            grid_size=3,
        ),
    ]

    assert result["triangles"] != original_triangles
    assert result["triangles"] == expected_triangles
