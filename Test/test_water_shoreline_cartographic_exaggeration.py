import pytest

from CORE.atlas_lod_level_catalog import (
    AtlasLoDLevelCatalog,
)
from CORE.atlas_water_shoreline_composition_resolver import (
    AtlasWaterShorelineCompositionResolver,
)


def test_narrow_waterway_can_resolve_cartographic_exaggeration():
    result = (
        AtlasWaterShorelineCompositionResolver
        .resolve_cartographic_exaggeration(
            semantic_class="narrow_waterway",
            source_width_m=1.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.60,
            minimum_printable_width_mm=0.40,
            semantic_priority=0.80,
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert result.semantic_class == (
        "narrow_waterway"
    )
    assert result.strict_scale_width_mm == pytest.approx(
        1.0 * 1000.0 / 5500.0
    )
    assert result.physical_width_mm == pytest.approx(
        0.60
    )
    assert result.exaggerated is True


def test_shoreline_edge_can_resolve_cartographic_exaggeration():
    result = (
        AtlasWaterShorelineCompositionResolver
        .resolve_cartographic_exaggeration(
            semantic_class="shoreline_edge",
            source_width_m=0.8,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.50,
            minimum_printable_width_mm=0.40,
            semantic_priority=0.70,
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert result.semantic_class == (
        "shoreline_edge"
    )
    assert result.physical_width_mm == pytest.approx(
        0.50
    )


def test_water_shoreline_cartographic_resolution_preserves_strict_scale_when_readable():
    result = (
        AtlasWaterShorelineCompositionResolver
        .resolve_cartographic_exaggeration(
            semantic_class="narrow_waterway",
            source_width_m=8.0,
            scale_ratio=5500.0,
            product_size_mm=150.0,
            nozzle_diameter_mm=0.40,
            minimum_printable_width_mm=0.40,
            semantic_priority=0.80,
            lod_level=(
                AtlasLoDLevelCatalog.resolve(2)
            ),
        )
    )

    assert result.physical_width_mm == pytest.approx(
        8.0 * 1000.0 / 5500.0
    )
    assert result.exaggerated is False
    assert result.reason == (
        "strict_scale_readable"
    )
