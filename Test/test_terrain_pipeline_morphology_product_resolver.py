import copy

import pytest

import CORE.atlas_terrain_pipeline as terrain_pipeline
from CORE.atlas_terrain_pipeline import AtlasTerrainPipeline


def _source_mesh():
    return {
        "type": "terrain_closed_slab",
        "triangles": [],
        "metadata": {
            "closed": True,
            "delta_height_m": 30.0,
            "min_height_m": 100.0,
            "max_height_m": 130.0,
            "z_scale": 3000.0,
            "size_mm": 150.0,
            "size_x_mm": 150.0,
            "size_y_mm": 150.0,
        },
        "grid": {
            "heights": [
                [100.0, 110.0],
                [120.0, 130.0],
            ],
            "min_height_m": 100.0,
            "max_height_m": 130.0,
            "delta_height_m": 30.0,
        },
        "top_points": [],
        "bottom_points": [],
    }


def _patch_terrain(monkeypatch, source_mesh):
    monkeypatch.setattr(
        terrain_pipeline,
        "AtlasSRTMProvider",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        AtlasTerrainPipeline,
        "_build_closed_mesh",
        staticmethod(
            lambda **kwargs: copy.deepcopy(source_mesh)
        ),
    )


def test_morphology_product_profile_is_disabled_by_default(
    monkeypatch,
):
    source = _source_mesh()
    _patch_terrain(monkeypatch, source)

    result = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(50.0, 8.0, 50.1, 8.1),
        target_size_mm=150.0,
        z_scale=3000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=2,
        debug=False,
    )

    assert "terrain_product_profile" not in result["metadata"]


def test_pipeline_resolves_product_profile_from_terrain_truth(
    monkeypatch,
):
    source = _source_mesh()
    source_grid = copy.deepcopy(source["grid"])
    _patch_terrain(monkeypatch, source)

    result = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(50.0, 8.0, 50.1, 8.1),
        target_size_mm=150.0,
        z_scale=3000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=2,
        scene_morphology="dense_urban",
        urban_density=0.80,
        landmark_present=True,
        terrain_minimum_printable_relief_mm=0.30,
        terrain_maximum_printable_relief_mm=12.0,
        debug=False,
    )

    profile = result["metadata"]["terrain_product_profile"]

    assert profile["scene_morphology"] == "dense_urban"
    assert profile["terrain_emphasis"] == "secondary"
    assert profile["vertical_compression"] == "strong"

    assert profile["source_elevation_range_m"] == pytest.approx(
        30.0
    )
    assert profile["physical_relief_range_mm"] == pytest.approx(
        10.0
    )
    assert profile["resolved_physical_relief_mm"] == pytest.approx(
        10.0
    )
    assert profile["relative_physical_relief"] == pytest.approx(
        10.0 / 150.0
    )

    assert result["grid"] == source_grid
    assert result["metadata"]["delta_height_m"] == pytest.approx(
        30.0
    )
    assert result["metadata"]["z_scale"] == pytest.approx(
        3000.0
    )
    assert profile["source_elevation_modified"] is False


def test_pipeline_clamps_product_relief_without_changing_source_truth(
    monkeypatch,
):
    source = _source_mesh()
    source["metadata"]["delta_height_m"] = 60.0
    source["grid"]["delta_height_m"] = 60.0
    source_grid = copy.deepcopy(source["grid"])

    _patch_terrain(monkeypatch, source)

    result = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(50.0, 8.0, 50.1, 8.1),
        target_size_mm=150.0,
        z_scale=3000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=2,
        scene_morphology="mountain",
        urban_density=0.05,
        landmark_present=False,
        terrain_minimum_printable_relief_mm=0.30,
        terrain_maximum_printable_relief_mm=12.0,
        debug=False,
    )

    profile = result["metadata"]["terrain_product_profile"]

    assert profile["physical_relief_range_mm"] == pytest.approx(
        20.0
    )
    assert profile["resolved_physical_relief_mm"] == pytest.approx(
        12.0
    )
    assert profile["printability_adjustment"] == (
        "limited_to_maximum"
    )

    assert result["grid"] == source_grid
    assert result["metadata"]["delta_height_m"] == pytest.approx(
        60.0
    )
    assert result["metadata"]["z_scale"] == pytest.approx(
        3000.0
    )


def test_pipeline_can_enable_presentation_surface_regularization(
    monkeypatch,
):
    source = _source_mesh()
    source["top_points"] = [
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
    ]
    source["bottom_points"] = [
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
    ]
    source["metadata"]["grid_size"] = 3

    _patch_terrain(
        monkeypatch,
        source,
    )

    result = AtlasTerrainPipeline.build_terrain_slab(
        bbox=(50.0, 8.0, 50.1, 8.1),
        target_size_mm=150.0,
        z_scale=3000.0,
        base_z=0.80,
        bottom_z=0.0,
        grid_size=3,
        presentation_regularization_passes=1,
        presentation_regularization_strength=0.50,
        debug=False,
    )

    assert result["top_points"] == source["top_points"]
    assert "presentation_top_points" in result
    assert result["metadata"]["presentation_regularized"] is True
