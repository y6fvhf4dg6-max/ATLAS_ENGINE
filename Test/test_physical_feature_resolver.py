from __future__ import annotations

import pytest

from CORE.atlas_physical_feature_resolver import (
    AtlasPhysicalFeatureProfile,
    AtlasPhysicalFeatureResolver,
)


def test_preserves_readable_raised_feature_above_profile_minimums():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="portal_arch",
        semantic_class="arch",
        measured_width_mm=1.2,
        measured_height_mm=0.8,
        semantic_importance=0.9,
        readability_priority=0.9,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.feature_id == "portal_arch"
    assert decision.semantic_class == "arch"
    assert decision.action == "preserve"
    assert decision.measured_width_mm == pytest.approx(1.2)
    assert decision.measured_height_mm == pytest.approx(0.8)
    assert decision.resolved_width_mm == pytest.approx(1.2)
    assert decision.resolved_height_mm == pytest.approx(0.8)
    assert decision.reason == "feature_already_readable"
    assert decision.requires_operator_review is False
    assert decision.adjustments == ()


def test_enlarges_important_raised_feature_below_profile_minimums():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="portal_arch",
        semantic_class="arch",
        measured_width_mm=0.55,
        measured_height_mm=0.25,
        semantic_importance=0.95,
        readability_priority=0.95,
        physical_feature_policy="enlarge_if_needed",
        profile=profile,
    )

    assert decision.action == "enlarge"
    assert decision.resolved_width_mm == pytest.approx(0.8)
    assert decision.resolved_height_mm == pytest.approx(0.4)
    assert decision.reason == "raised_feature_below_minimum"
    assert decision.requires_operator_review is False
    assert decision.adjustments == (
        {
            "field": "width_mm",
            "from": pytest.approx(0.55),
            "to": pytest.approx(0.8),
        },
        {
            "field": "height_mm",
            "from": pytest.approx(0.25),
            "to": pytest.approx(0.4),
        },
    )


def test_reports_omission_for_extremely_small_low_priority_raised_feature():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="tiny_rosette",
        semantic_class="ornament",
        measured_width_mm=0.10,
        measured_height_mm=0.08,
        semantic_importance=0.10,
        readability_priority=0.10,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.action == "omit"
    assert decision.resolved_width_mm == pytest.approx(0.0)
    assert decision.resolved_height_mm == pytest.approx(0.0)
    assert decision.reason == "feature_below_meaningful_printable_scale"
    assert decision.requires_operator_review is False
    assert decision.adjustments == (
        {
            "field": "feature",
            "from": "present",
            "to": "omitted",
        },
    )


def test_requires_operator_review_for_high_priority_subminimum_feature_without_enlarge_policy():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="saint_face",
        semantic_class="face",
        measured_width_mm=0.35,
        measured_height_mm=0.20,
        semantic_importance=1.0,
        readability_priority=1.0,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.action == "require_operator_review"
    assert decision.resolved_width_mm == pytest.approx(0.35)
    assert decision.resolved_height_mm == pytest.approx(0.20)
    assert decision.reason == "important_feature_below_physical_minimum"
    assert decision.requires_operator_review is True
    assert decision.adjustments == ()


def test_merges_adjacent_repeated_features_below_minimum_spacing():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_adjacent_features(
        feature_ids=("tracery_left", "tracery_right"),
        semantic_class="tracery",
        measured_spacing_mm=0.20,
        minimum_spacing_mm=0.40,
        semantic_importance=0.70,
        readability_priority=0.80,
        physical_feature_policy="merge_if_needed",
        profile=profile,
    )

    assert decision.action == "merge"
    assert decision.feature_ids == (
        "tracery_left",
        "tracery_right",
    )
    assert decision.measured_spacing_mm == pytest.approx(0.20)
    assert decision.minimum_spacing_mm == pytest.approx(0.40)
    assert decision.reason == "adjacent_features_below_minimum_spacing"
    assert decision.requires_operator_review is False
    assert decision.adjustments == (
        {
            "field": "feature_count",
            "from": 2,
            "to": 1,
        },
    )


def test_simplifies_repeated_detail_density_above_profile_budget():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_repeated_detail(
        feature_id="rose_window_tracery",
        semantic_class="tracery",
        measured_repeat_count=12,
        maximum_readable_repeat_count=6,
        semantic_importance=0.80,
        readability_priority=0.90,
        physical_feature_policy="simplify_if_needed",
        profile=profile,
    )

    assert decision.action == "simplify"
    assert decision.measured_repeat_count == 12
    assert decision.resolved_repeat_count == 6
    assert decision.reason == "repeated_detail_density_above_readable_budget"
    assert decision.requires_operator_review is False
    assert decision.adjustments == (
        {
            "field": "repeat_count",
            "from": 12,
            "to": 6,
        },
    )


def test_converts_thin_readable_raised_detail_to_engraving():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="robe_fold",
        semantic_class="garment_fold",
        measured_width_mm=0.30,
        measured_height_mm=0.18,
        semantic_importance=0.70,
        readability_priority=0.85,
        physical_feature_policy="engrave_if_needed",
        profile=profile,
    )

    assert decision.action == "convert_to_engraving"
    assert decision.resolved_width_mm == pytest.approx(0.40)
    assert decision.resolved_height_mm == pytest.approx(0.20)
    assert decision.reason == "raised_feature_better_preserved_as_engraving"
    assert decision.requires_operator_review is False
    assert decision.adjustments == (
        {
            "field": "representation",
            "from": "raised",
            "to": "engraving",
        },
        {
            "field": "width_mm",
            "from": pytest.approx(0.30),
            "to": pytest.approx(0.40),
        },
        {
            "field": "depth_mm",
            "from": pytest.approx(0.18),
            "to": pytest.approx(0.20),
        },
    )


def test_preserves_groove_above_profile_width_and_depth_minimums():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
        minimum_groove_width_mm=0.4,
        minimum_groove_depth_mm=0.2,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_groove_feature(
        feature_id="robe_fold",
        semantic_class="garment_fold",
        measured_width_mm=0.55,
        measured_depth_mm=0.30,
        semantic_importance=0.70,
        readability_priority=0.85,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.action == "preserve"
    assert decision.resolved_width_mm == pytest.approx(0.55)
    assert decision.resolved_depth_mm == pytest.approx(0.30)
    assert decision.reason == "groove_already_readable"
    assert decision.requires_operator_review is False
    assert decision.adjustments == ()


def test_enlarges_groove_below_profile_width_or_depth_minimum():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
        minimum_groove_width_mm=0.4,
        minimum_groove_depth_mm=0.2,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_groove_feature(
        feature_id="robe_fold",
        semantic_class="garment_fold",
        measured_width_mm=0.30,
        measured_depth_mm=0.12,
        semantic_importance=0.75,
        readability_priority=0.90,
        physical_feature_policy="enlarge_if_needed",
        profile=profile,
    )

    assert decision.action == "enlarge"
    assert decision.resolved_width_mm == pytest.approx(0.40)
    assert decision.resolved_depth_mm == pytest.approx(0.20)
    assert decision.reason == "groove_below_minimum"
    assert decision.requires_operator_review is False
    assert decision.adjustments == (
        {
            "field": "width_mm",
            "from": pytest.approx(0.30),
            "to": pytest.approx(0.40),
        },
        {
            "field": "depth_mm",
            "from": pytest.approx(0.12),
            "to": pytest.approx(0.20),
        },
    )


def test_requires_review_for_projection_beyond_profile_limit():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
        minimum_groove_width_mm=0.4,
        minimum_groove_depth_mm=0.2,
        maximum_unsupported_projection_mm=1.5,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_projection_feature(
        feature_id="angel_wing_tip",
        semantic_class="wing",
        unsupported_projection_mm=2.4,
        semantic_importance=0.95,
        readability_priority=0.90,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.action == "require_operator_review"
    assert decision.unsupported_projection_mm == pytest.approx(2.4)
    assert decision.maximum_unsupported_projection_mm == pytest.approx(1.5)
    assert decision.reason == "unsupported_projection_exceeds_profile_limit"
    assert decision.requires_operator_review is True
    assert decision.adjustments == ()


def test_requires_review_for_fragile_connection_below_profile_ratio():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
        minimum_groove_width_mm=0.4,
        minimum_groove_depth_mm=0.2,
        maximum_unsupported_projection_mm=1.5,
        minimum_connection_ratio=0.20,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_connection_feature(
        feature_id="angel_wing",
        semantic_class="wing",
        connection_width_mm=0.45,
        component_span_mm=3.0,
        semantic_importance=0.95,
        readability_priority=0.90,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.action == "require_operator_review"
    assert decision.connection_ratio == pytest.approx(0.15)
    assert decision.minimum_connection_ratio == pytest.approx(0.20)
    assert decision.reason == "fragile_connection_below_profile_ratio"
    assert decision.requires_operator_review is True
    assert decision.adjustments == ()


def test_requires_review_for_unsupported_slope_beyond_profile_limit():
    profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
        minimum_groove_width_mm=0.4,
        minimum_groove_depth_mm=0.2,
        maximum_unsupported_projection_mm=1.5,
        minimum_connection_ratio=0.20,
        maximum_unsupported_slope_degrees=45.0,
    )

    decision = AtlasPhysicalFeatureResolver.resolve_slope_feature(
        feature_id="angel_wing_lower_edge",
        semantic_class="wing",
        unsupported_slope_degrees=62.0,
        semantic_importance=0.95,
        readability_priority=0.90,
        physical_feature_policy="preserve",
        profile=profile,
    )

    assert decision.action == "require_operator_review"
    assert decision.unsupported_slope_degrees == pytest.approx(62.0)
    assert decision.maximum_unsupported_slope_degrees == pytest.approx(45.0)
    assert decision.reason == "unsupported_slope_exceeds_profile_limit"
    assert decision.requires_operator_review is True
    assert decision.adjustments == ()


def test_same_feature_can_resolve_differently_at_different_product_sizes():
    small_profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium_170",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=170.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )
    large_profile = AtlasPhysicalFeatureProfile(
        name="fdm_0_4_premium_260",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=260.0,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
    )

    small = AtlasPhysicalFeatureResolver.resolve_scaled_raised_feature(
        feature_id="portal_arch",
        semantic_class="arch",
        source_width_mm_at_reference=0.60,
        source_height_mm_at_reference=0.30,
        reference_product_size_mm=170.0,
        semantic_importance=0.9,
        readability_priority=0.9,
        physical_feature_policy="enlarge_if_needed",
        profile=small_profile,
    )
    large = AtlasPhysicalFeatureResolver.resolve_scaled_raised_feature(
        feature_id="portal_arch",
        semantic_class="arch",
        source_width_mm_at_reference=0.60,
        source_height_mm_at_reference=0.30,
        reference_product_size_mm=170.0,
        semantic_importance=0.9,
        readability_priority=0.9,
        physical_feature_policy="enlarge_if_needed",
        profile=large_profile,
    )

    assert small.action == "enlarge"
    assert large.action == "preserve"
    assert small.reason == "raised_feature_below_minimum"
    assert large.reason == "feature_already_readable"
    assert small.resolved_width_mm == pytest.approx(0.8)
    assert large.measured_width_mm == pytest.approx(
        0.60 * 260.0 / 170.0
    )
