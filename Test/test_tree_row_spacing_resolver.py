import pytest

from CORE.atlas_tree_row_spacing_resolver import (
    AtlasTreeRowSpacingResolver,
)


def test_spacing_resolver_preserves_printable_source_spacing():
    result = AtlasTreeRowSpacingResolver.resolve(
        source_spacing_m=5.0,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["action"] == "preserve"
    assert result["source_spacing_m"] == pytest.approx(5.0)
    assert result["scaled_spacing_mm"] == pytest.approx(
        5.0 * 1000.0 / 5500.0
    )
    assert result["minimum_printable_mm"] == pytest.approx(0.4)
    assert result["resolved_spacing_mm"] == pytest.approx(
        5.0 * 1000.0 / 5500.0
    )


def test_spacing_resolver_enlarges_sub_printable_spacing():
    result = AtlasTreeRowSpacingResolver.resolve(
        source_spacing_m=1.5,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["action"] == "enlarge"
    assert result["scaled_spacing_mm"] < 0.4
    assert result["resolved_spacing_mm"] == pytest.approx(0.4)


def test_spacing_resolver_omits_extremely_small_spacing():
    result = AtlasTreeRowSpacingResolver.resolve(
        source_spacing_m=0.25,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["action"] == "omit"
    assert result["resolved_spacing_mm"] == 0.0


def test_spacing_resolver_derives_product_fallback_from_tree_symbol_size():
    result = AtlasTreeRowSpacingResolver.resolve_fallback(
        nozzle_diameter_mm=0.4,
    )

    assert result["action"] == "fallback"
    assert result["evidence_source"] == "product_readability"
    assert result["resolved_spacing_mm"] == pytest.approx(1.50)
    assert result["tree_symbol_max_diameter_mm"] == pytest.approx(1.10)
    assert result["clearance_mm"] == pytest.approx(0.40)
