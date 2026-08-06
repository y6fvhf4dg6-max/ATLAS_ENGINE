import pytest

from CORE.atlas_lod_level_catalog import (
    LOD_0,
    LOD_1,
    LOD_2,
    LOD_3,
    LOD_4,
)
from CORE.atlas_lod_resolution_contract import (
    AtlasLoDResolutionInput,
    AtlasLoDResolutionResult,
)
from CORE.atlas_lod_resolver import (
    AtlasLoDResolver,
)


def _source(**overrides):
    values = {
        "product_size_mm": 170.0,
        "scale_ratio": 3000.0,
        "nozzle_diameter_mm": 0.4,
        "layer_height_mm": 0.2,
        "minimum_wall_thickness_mm": 0.8,
        "landmark_importance": 0.75,
        "viewing_distance_mm": 600.0,
        "available_color_count": 4,
    }
    values.update(overrides)

    return AtlasLoDResolutionInput(
        **values
    )


def test_resolver_returns_resolution_result():
    source = _source()

    result = AtlasLoDResolver.resolve(
        source
    )

    assert isinstance(
        result,
        AtlasLoDResolutionResult,
    )
    assert result.source is source


def test_typical_wall_collection_resolves_lod_3():
    result = AtlasLoDResolver.resolve(
        _source()
    )

    assert result.level is LOD_3
    assert (
        "standard_print_resolution"
        in result.supporting_factors
    )


def test_fine_close_premium_configuration_resolves_lod_4():
    result = AtlasLoDResolver.resolve(
        _source(
            product_size_mm=200.0,
            scale_ratio=2000.0,
            nozzle_diameter_mm=0.2,
            layer_height_mm=0.08,
            minimum_wall_thickness_mm=0.4,
            landmark_importance=1.0,
            viewing_distance_mm=350.0,
            available_color_count=5,
        )
    )

    assert result.level is LOD_4


def test_coarse_print_resolution_caps_lod_2():
    result = AtlasLoDResolver.resolve(
        _source(
            nozzle_diameter_mm=0.6,
            layer_height_mm=0.3,
            minimum_wall_thickness_mm=1.2,
        )
    )

    assert result.level is LOD_2
    assert (
        "print_resolution"
        in result.limiting_factors
    )


def test_small_distant_product_caps_lod_1():
    result = AtlasLoDResolver.resolve(
        _source(
            product_size_mm=80.0,
            scale_ratio=7000.0,
            viewing_distance_mm=1500.0,
        )
    )

    assert result.level is LOD_1
    assert (
        "product_visibility"
        in result.limiting_factors
    )


def test_extreme_physical_limits_resolve_lod_0():
    result = AtlasLoDResolver.resolve(
        _source(
            product_size_mm=50.0,
            scale_ratio=12000.0,
            nozzle_diameter_mm=1.0,
            layer_height_mm=0.5,
            minimum_wall_thickness_mm=2.0,
            viewing_distance_mm=2500.0,
            available_color_count=1,
        )
    )

    assert result.level is LOD_0


def test_low_landmark_importance_cannot_remove_primary_form():
    result = AtlasLoDResolver.resolve(
        _source(
            landmark_importance=0.0,
        )
    )

    assert result.level is LOD_3


def test_importance_cannot_override_physical_cap():
    result = AtlasLoDResolver.resolve(
        _source(
            nozzle_diameter_mm=0.6,
            layer_height_mm=0.3,
            minimum_wall_thickness_mm=1.2,
            landmark_importance=1.0,
            available_color_count=5,
        )
    )

    assert result.level is LOD_2


def test_color_count_does_not_remove_geometry_levels():
    monochrome = AtlasLoDResolver.resolve(
        _source(
            available_color_count=1,
        )
    )
    multicolor = AtlasLoDResolver.resolve(
        _source(
            available_color_count=5,
        )
    )

    assert monochrome.level is LOD_3
    assert multicolor.level is LOD_3
    assert (
        "multicolor_capacity"
        in multicolor.supporting_factors
    )
    assert (
        "multicolor_capacity"
        not in monochrome.supporting_factors
    )


def test_resolution_is_deterministic():
    source = _source()

    first = AtlasLoDResolver.resolve(
        source
    )
    second = AtlasLoDResolver.resolve(
        source
    )

    assert first == second


@pytest.mark.parametrize(
    "source",
    (
        None,
        object(),
        {},
    ),
)
def test_resolver_rejects_invalid_source(
    source,
):
    with pytest.raises(
        TypeError,
        match="source",
    ):
        AtlasLoDResolver.resolve(
            source
        )


def test_finer_print_settings_never_reduce_lod():
    coarse = AtlasLoDResolver.resolve(
        _source(
            nozzle_diameter_mm=0.6,
            layer_height_mm=0.3,
            minimum_wall_thickness_mm=1.2,
        )
    )
    fine = AtlasLoDResolver.resolve(
        _source(
            nozzle_diameter_mm=0.2,
            layer_height_mm=0.08,
            minimum_wall_thickness_mm=0.4,
        )
    )

    assert fine.level.level >= coarse.level.level


def test_larger_closer_product_never_reduces_lod():
    constrained = AtlasLoDResolver.resolve(
        _source(
            product_size_mm=80.0,
            scale_ratio=7000.0,
            viewing_distance_mm=1500.0,
        )
    )
    visible = AtlasLoDResolver.resolve(
        _source(
            product_size_mm=200.0,
            scale_ratio=2000.0,
            viewing_distance_mm=350.0,
        )
    )

    assert visible.level.level >= constrained.level.level
