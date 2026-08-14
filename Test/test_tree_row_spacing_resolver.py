import pytest

from CORE.atlas_tree_row_spacing_resolver import (
    AtlasTreeRowSpacingResolver,
)
from CORE.atlas_tree_foundation_builder import (
    AtlasTreeFoundationBuilder,
)


def test_spacing_resolver_preserves_printable_source_spacing():
    result = AtlasTreeRowSpacingResolver.resolve(
        source_spacing_m=5.0,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["action"] == "enlarge"
    assert result["source_spacing_m"] == pytest.approx(5.0)
    assert result["scaled_spacing_mm"] == pytest.approx(
        5.0 * 1000.0 / 5500.0
    )
    assert result["minimum_printable_mm"] == pytest.approx(0.4)
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert result["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )


def test_spacing_resolver_enlarges_sub_printable_spacing():
    result = AtlasTreeRowSpacingResolver.resolve(
        source_spacing_m=1.5,
        scale_ratio=5500.0,
        nozzle_diameter_mm=0.4,
    )

    assert result["action"] == "enlarge"
    assert result["scaled_spacing_mm"] < 0.4
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert result["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )


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
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    assert result["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )
    assert result["tree_symbol_max_diameter_mm"] == pytest.approx(
        canonical["crown_diameter_mm"]
    )
    assert result["clearance_mm"] == pytest.approx(0.40)


def test_fallback_spacing_uses_canonical_tree_crown_diameter():
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    result = AtlasTreeRowSpacingResolver.resolve_fallback(
        nozzle_diameter_mm=0.40,
    )

    assert result["tree_symbol_max_diameter_mm"] == pytest.approx(
        canonical["crown_diameter_mm"]
    )
    assert result["resolved_spacing_mm"] == pytest.approx(
        canonical["crown_diameter_mm"] + 0.40
    )


def test_explicit_tree_row_spacing_cannot_overlap_canonical_crowns():
    canonical = (
        AtlasTreeFoundationBuilder
        ._canonical_tree_dimensions()
    )

    result = AtlasTreeRowSpacingResolver.resolve(
        source_spacing_m=2.0,
        scale_ratio=3000.0,
        nozzle_diameter_mm=0.40,
    )

    minimum_spacing_mm = (
        canonical["crown_diameter_mm"]
        + 0.40
    )

    assert result["resolved_spacing_mm"] >= minimum_spacing_mm
