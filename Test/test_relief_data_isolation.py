import numpy as np

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)
from CORE.atlas_relief_mesh_builder import (
    AtlasReliefMeshBuilder,
)
from CORE.atlas_relief_pipeline import (
    AtlasReliefPipeline,
)
from fixtures.relief.relief_fixture_catalog import (
    load_fixture,
)


def test_normalize_does_not_mutate_input():
    values = load_fixture("asymmetric_surface_3x4")
    original = values.copy()

    AtlasHeightMapEngine.normalize(values)

    assert np.array_equal(values, original)


def test_contrast_remap_does_not_mutate_input():
    values = load_fixture("asymmetric_surface_3x4")
    original = values.copy()

    AtlasHeightMapEngine.remap_contrast(
        values,
        black_point=0.1,
        white_point=0.9,
        gamma=0.8,
    )

    assert np.array_equal(values, original)


def test_bilinear_resampling_does_not_mutate_input():
    values = load_fixture("asymmetric_surface_3x4")
    original = values.copy()

    AtlasHeightMapEngine.resample_bilinear(
        values,
        target_rows=7,
        target_columns=9,
    )

    assert np.array_equal(values, original)


def test_gaussian_smoothing_does_not_mutate_input():
    values = load_fixture("impulse_7x7")
    original = values.copy()

    AtlasHeightMapEngine.smooth_gaussian(
        values,
        sigma=1.0,
        radius=3,
    )

    assert np.array_equal(values, original)


def test_relief_mesh_builder_does_not_mutate_input():
    values = load_fixture("asymmetric_surface_3x4")
    original = values.copy()

    AtlasReliefMeshBuilder.build(
        values,
        width_mm=20.0,
        depth_mm=15.0,
    )

    assert np.array_equal(values, original)


def test_relief_mesh_contains_independent_height_map_copy():
    values = load_fixture("asymmetric_surface_3x4")

    mesh = AtlasReliefMeshBuilder.build(
        values,
        width_mm=20.0,
        depth_mm=15.0,
    )

    mesh_height_map = mesh["height_map"]

    assert mesh_height_map is not values
    assert np.array_equal(mesh_height_map, values)

    mesh_height_map[0, 0] = 123.0

    assert values[0, 0] != 123.0


def test_pipeline_does_not_mutate_input():
    values = load_fixture("asymmetric_surface_3x4")
    original = values.copy()

    AtlasReliefPipeline.build(
        values,
        width_mm=20.0,
        depth_mm=15.0,
        target_rows=6,
        target_columns=8,
        smoothing_sigma=0.8,
        smoothing_radius=2,
    )

    assert np.array_equal(values, original)


def test_pipeline_intermediate_arrays_do_not_share_memory():
    result = AtlasReliefPipeline.build(
        load_fixture("asymmetric_surface_3x4"),
        width_mm=20.0,
        depth_mm=15.0,
        target_rows=6,
        target_columns=8,
        smoothing_sigma=0.8,
        smoothing_radius=2,
    )

    normalized = result["normalized_height_map"]
    contrast = result["contrast_height_map"]
    resampled = result["resampled_height_map"]
    processed = result["processed_height_map"]

    assert not np.shares_memory(normalized, contrast)
    assert not np.shares_memory(normalized, resampled)
    assert not np.shares_memory(normalized, processed)
    assert not np.shares_memory(contrast, resampled)
    assert not np.shares_memory(contrast, processed)
    assert not np.shares_memory(resampled, processed)


def test_pipeline_mesh_height_map_is_independent_from_processed_map():
    result = AtlasReliefPipeline.build(
        load_fixture("asymmetric_surface_3x4"),
        width_mm=20.0,
        depth_mm=15.0,
        target_rows=6,
        target_columns=8,
        smoothing_sigma=0.8,
        smoothing_radius=2,
    )

    processed = result["processed_height_map"]
    mesh_height_map = result["mesh"]["height_map"]

    assert mesh_height_map is not processed
    assert not np.shares_memory(
        mesh_height_map,
        processed,
    )
    assert np.array_equal(
        mesh_height_map,
        processed,
    )


def test_mutating_one_pipeline_stage_does_not_change_other_stages():
    result = AtlasReliefPipeline.build(
        load_fixture("asymmetric_surface_3x4"),
        width_mm=20.0,
        depth_mm=15.0,
        target_rows=6,
        target_columns=8,
        smoothing_sigma=0.8,
        smoothing_radius=2,
    )

    contrast_before = result["contrast_height_map"].copy()
    resampled_before = result["resampled_height_map"].copy()
    processed_before = result["processed_height_map"].copy()
    mesh_before = result["mesh"]["height_map"].copy()

    result["normalized_height_map"][0, 0] = 123.0

    assert np.array_equal(
        result["contrast_height_map"],
        contrast_before,
    )
    assert np.array_equal(
        result["resampled_height_map"],
        resampled_before,
    )
    assert np.array_equal(
        result["processed_height_map"],
        processed_before,
    )
    assert np.array_equal(
        result["mesh"]["height_map"],
        mesh_before,
    )
