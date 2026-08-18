from __future__ import annotations

from CORE.atlas_physical_feature_resolver import (
    AtlasPhysicalFeatureProfile,
    AtlasPhysicalFeatureResolver,
)


def _profile(product_size_mm=170.0):
    return AtlasPhysicalFeatureProfile(
        name=f"fdm_0_4_premium_{int(product_size_mm)}",
        nozzle_diameter_mm=0.4,
        layer_height_mm=0.2,
        product_size_mm=product_size_mm,
        material="pla",
        minimum_raised_width_mm=0.8,
        minimum_raised_height_mm=0.4,
        minimum_groove_width_mm=0.4,
        minimum_groove_depth_mm=0.2,
        maximum_unsupported_projection_mm=1.5,
        minimum_connection_ratio=0.20,
        maximum_unsupported_slope_degrees=45.0,
    )


def test_same_input_produces_same_physical_feature_decision():
    kwargs = dict(
        feature_id="portal_arch",
        semantic_class="arch",
        measured_width_mm=0.55,
        measured_height_mm=0.25,
        semantic_importance=0.95,
        readability_priority=0.95,
        physical_feature_policy="enlarge_if_needed",
        profile=_profile(),
    )

    first = AtlasPhysicalFeatureResolver.resolve_raised_feature(**kwargs)
    second = AtlasPhysicalFeatureResolver.resolve_raised_feature(**kwargs)

    assert first == second


def test_enlargement_and_omission_are_never_silent():
    enlarged = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="portal_arch",
        semantic_class="arch",
        measured_width_mm=0.55,
        measured_height_mm=0.25,
        semantic_importance=0.95,
        readability_priority=0.95,
        physical_feature_policy="enlarge_if_needed",
        profile=_profile(),
    )
    omitted = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="tiny_rosette",
        semantic_class="ornament",
        measured_width_mm=0.10,
        measured_height_mm=0.08,
        semantic_importance=0.10,
        readability_priority=0.10,
        physical_feature_policy="preserve",
        profile=_profile(),
    )

    assert enlarged.action == "enlarge"
    assert enlarged.reason
    assert enlarged.adjustments

    assert omitted.action == "omit"
    assert omitted.reason
    assert omitted.adjustments


def test_important_unprintable_feature_is_reviewed_not_silently_lost():
    decision = AtlasPhysicalFeatureResolver.resolve_raised_feature(
        feature_id="saint_face",
        semantic_class="face",
        measured_width_mm=0.35,
        measured_height_mm=0.20,
        semantic_importance=1.0,
        readability_priority=1.0,
        physical_feature_policy="preserve",
        profile=_profile(),
    )

    assert decision.action == "require_operator_review"
    assert decision.requires_operator_review is True
    assert decision.resolved_width_mm > 0.0
    assert decision.resolved_height_mm > 0.0


def test_same_feature_changes_explainably_with_product_size():
    small = AtlasPhysicalFeatureResolver.resolve_scaled_raised_feature(
        feature_id="portal_arch",
        semantic_class="arch",
        source_width_mm_at_reference=0.60,
        source_height_mm_at_reference=0.30,
        reference_product_size_mm=170.0,
        semantic_importance=0.9,
        readability_priority=0.9,
        physical_feature_policy="enlarge_if_needed",
        profile=_profile(170.0),
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
        profile=_profile(260.0),
    )

    assert small.action == "enlarge"
    assert large.action == "preserve"
    assert small.reason != large.reason
