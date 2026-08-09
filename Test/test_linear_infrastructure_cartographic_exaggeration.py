import pytest

from CORE.atlas_linear_infrastructure_resolver import (
    AtlasLinearInfrastructureResolver,
)
from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)


def test_linear_infrastructure_can_use_cartographic_exaggeration():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "railway": "tram",
            "width": "1.0",
        },
        scale_ratio=5500.0,
        minimum_printable_width_mm=0.40,
        line_width_mm=0.40,
        minimum_gap_mm=0.20,
        cartographic_product_size_mm=150.0,
        cartographic_nozzle_diameter_mm=0.60,
        cartographic_lod_level=(
            AtlasLoDLevelCatalog.resolve(2)
        ),
    )

    assert profile is not None
    assert profile.semantic_class == "tram"

    assert profile.physical_width_mm == pytest.approx(
        0.60
    )


def test_linear_infrastructure_preserves_strict_scale_when_readable():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "railway": "rail",
            "width": "8.0",
        },
        scale_ratio=5500.0,
        minimum_printable_width_mm=0.40,
        line_width_mm=0.40,
        minimum_gap_mm=0.20,
        cartographic_product_size_mm=150.0,
        cartographic_nozzle_diameter_mm=0.40,
        cartographic_lod_level=(
            AtlasLoDLevelCatalog.resolve(2)
        ),
    )

    assert profile is not None

    assert profile.physical_width_mm == pytest.approx(
        8.0 * 1000.0 / 5500.0
    )


def test_linear_infrastructure_cartographic_exaggeration_is_opt_in():
    profile = AtlasLinearInfrastructureResolver.resolve_profile(
        tags={
            "railway": "tram",
            "width": "1.0",
        },
        scale_ratio=5500.0,
        minimum_printable_width_mm=0.40,
        line_width_mm=0.40,
        minimum_gap_mm=0.20,
    )

    assert profile is not None

    assert profile.physical_width_mm == pytest.approx(
        0.40
    )
