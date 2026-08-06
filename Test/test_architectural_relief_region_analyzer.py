import numpy as np
import pytest

from CORE.atlas_architectural_relief_region_analyzer import (
    AtlasArchitecturalReliefRegionAnalyzer,
)


def _material_map():
    return np.array(
        [
            [0, 1, 1, 0, 2],
            [0, 1, 0, 0, 2],
            [0, 0, 0, 2, 2],
            [1, 0, 0, 0, 0],
        ],
        dtype=np.uint8,
    )


def test_analyzes_all_semantic_surface_regions():
    analysis = (
        AtlasArchitecturalReliefRegionAnalyzer
        .analyze(
            material_id_map=_material_map(),
            material_names=(
                "rock",
                "vegetation",
                "tomb_facade",
            ),
        )
    )

    assert analysis.shape == (4, 5)
    assert analysis.total_pixel_count == 20
    assert analysis.region_count == 3

    assert tuple(
        region.material_name
        for region in analysis.regions
    ) == (
        "rock",
        "vegetation",
        "tomb_facade",
    )


def test_region_metrics_include_coverage_and_bounds():
    analysis = (
        AtlasArchitecturalReliefRegionAnalyzer
        .analyze(
            material_id_map=_material_map(),
            material_names=(
                "rock",
                "vegetation",
                "tomb_facade",
            ),
        )
    )

    vegetation = analysis.region_for_material(
        "vegetation"
    )

    assert vegetation.material_id == 1
    assert vegetation.pixel_count == 4
    assert vegetation.coverage_ratio == pytest.approx(
        0.20
    )
    assert vegetation.bounds == (
        0,
        0,
        3,
        2,
    )


def test_disconnected_surface_areas_are_counted():
    analysis = (
        AtlasArchitecturalReliefRegionAnalyzer
        .analyze(
            material_id_map=_material_map(),
            material_names=(
                "rock",
                "vegetation",
                "tomb_facade",
            ),
        )
    )

    vegetation = analysis.region_for_material(
        "vegetation"
    )
    tomb_facade = analysis.region_for_material(
        "tomb_facade"
    )

    assert vegetation.component_count == 2
    assert tomb_facade.component_count == 1

    assert tuple(
        component.pixel_count
        for component in vegetation.components
    ) == (
        3,
        1,
    )


def test_empty_material_region_is_reported_safely():
    analysis = (
        AtlasArchitecturalReliefRegionAnalyzer
        .analyze(
            material_id_map=np.zeros(
                (2, 3),
                dtype=np.uint8,
            ),
            material_names=(
                "rock",
                "portal",
            ),
        )
    )

    portal = analysis.region_for_material(
        "portal"
    )

    assert portal.pixel_count == 0
    assert portal.coverage_ratio == 0.0
    assert portal.bounds is None
    assert portal.component_count == 0
    assert portal.components == ()


def test_rejects_material_ids_outside_name_catalog():
    with pytest.raises(
        ValueError,
        match="material_id_map",
    ):
        AtlasArchitecturalReliefRegionAnalyzer.analyze(
            material_id_map=np.array(
                [[0, 2]],
                dtype=np.uint8,
            ),
            material_names=(
                "rock",
                "facade",
            ),
        )
