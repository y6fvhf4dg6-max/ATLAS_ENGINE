import pytest


# === PHASE 8 ITEM 10.10 MEASUREMENT UNCERTAINTY RED ===


def test_defines_exact_locked_uncertainty_source_families():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
    )

    assert AtlasCanonicalHeadMetricUncertaintyComponent.SOURCE_FAMILIES == (
        "GT_ACQUISITION_SCANNER",
        "CALIBRATION",
        "SEGMENTATION",
        "LANDMARK_LOCALIZATION",
        "ALIGNMENT",
        "CORRESPONDENCE",
        "SAMPLING",
        "EXPRESSION_POSTURE_MISMATCH",
        "PREDICTION_RECONSTRUCTION",
        "REPEAT_CAPTURE",
    )


def test_quantified_uncertainty_component_requires_numeric_value_and_provenance():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
    )

    component = AtlasCanonicalHeadMetricUncertaintyComponent(
        source_family="CALIBRATION",
        evidence_state="QUANTIFIED",
        uncertainty_mm=0.25,
        provenance_reference="verified calibration evidence",
    )

    assert component.evidence_state == "QUANTIFIED"
    assert component.uncertainty_mm == pytest.approx(0.25)


def test_unresolved_uncertainty_component_cannot_carry_fabricated_numeric_value():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
    )

    with pytest.raises(ValueError, match="UNRESOLVED|uncertainty_mm|numeric"):
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="ALIGNMENT",
            evidence_state="UNRESOLVED",
            uncertainty_mm=0.0,
            provenance_reference="alignment uncertainty unresolved",
        )


def test_quantified_uncertainty_rejects_missing_provenance():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
    )

    with pytest.raises(ValueError, match="provenance"):
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="SAMPLING",
            evidence_state="QUANTIFIED",
            uncertainty_mm=0.1,
            provenance_reference="",
        )


def test_uncertainty_component_rejects_negative_or_nonfinite_numeric_values():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
    )

    for value in (-0.1, float("inf"), float("nan")):
        with pytest.raises(ValueError, match="uncertainty_mm"):
            AtlasCanonicalHeadMetricUncertaintyComponent(
                source_family="LANDMARK_LOCALIZATION",
                evidence_state="QUANTIFIED",
                uncertainty_mm=value,
                provenance_reference="verified uncertainty evidence",
            )


def test_gt_uncertainty_floor_requires_quantified_gt_side_evidence():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    components = (
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="GT_ACQUISITION_SCANNER",
            evidence_state="UNRESOLVED",
            uncertainty_mm=None,
            provenance_reference="scanner uncertainty unresolved",
        ),
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="CALIBRATION",
            evidence_state="UNRESOLVED",
            uncertainty_mm=None,
            provenance_reference="calibration uncertainty unresolved",
        ),
    )

    with pytest.raises(ValueError, match="GT uncertainty floor|quantified|evidence"):
        AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate(
            components=components,
            gt_uncertainty_floor_mm=0.5,
            gt_uncertainty_floor_state="ESTABLISHED",
            observed_metric_error_mm=1.0,
        )


def test_caller_cannot_establish_gt_uncertainty_floor_without_matching_evidence():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    components = (
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="PREDICTION_RECONSTRUCTION",
            evidence_state="QUANTIFIED",
            uncertainty_mm=0.4,
            provenance_reference="prediction reconstruction evidence",
        ),
    )

    with pytest.raises(ValueError, match="GT uncertainty floor|GT|evidence"):
        AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate(
            components=components,
            gt_uncertainty_floor_mm=0.4,
            gt_uncertainty_floor_state="ESTABLISHED",
            observed_metric_error_mm=0.8,
        )


def test_error_at_or_below_gt_uncertainty_floor_is_not_precisely_resolved_anatomical_error():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    components = (
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="GT_ACQUISITION_SCANNER",
            evidence_state="QUANTIFIED",
            uncertainty_mm=0.8,
            provenance_reference="verified scanner uncertainty",
        ),
    )

    result = AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate(
        components=components,
        gt_uncertainty_floor_mm=0.8,
        gt_uncertainty_floor_state="ESTABLISHED",
        observed_metric_error_mm=0.4,
    )

    assert result.precise_anatomical_error_state == "NOT_RESOLVED_BELOW_OR_AT_GT_FLOOR"


def test_prediction_reconstruction_uncertainty_does_not_establish_gt_uncertainty_floor():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    components = (
        AtlasCanonicalHeadMetricUncertaintyComponent(
            source_family="PREDICTION_RECONSTRUCTION",
            evidence_state="QUANTIFIED",
            uncertainty_mm=0.8,
            provenance_reference="prediction uncertainty",
        ),
    )

    with pytest.raises(ValueError, match="GT uncertainty floor|GT|evidence"):
        AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate(
            components=components,
            gt_uncertainty_floor_mm=0.8,
            gt_uncertainty_floor_state="ESTABLISHED",
            observed_metric_error_mm=1.2,
        )


def test_contract_does_not_silently_expose_combined_uncertainty_without_defined_model():
    import inspect

    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    parameters = set(
        inspect.signature(
            AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate
        ).parameters
    )

    assert "combined_uncertainty_mm" not in parameters
    assert "rss_uncertainty_mm" not in parameters

# === PHASE 8 ITEM 10.10 CLOSURE CHALLENGE CORRECTIVE RED ===


def test_established_gt_uncertainty_floor_must_match_quantified_gt_side_evidence():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    scanner = AtlasCanonicalHeadMetricUncertaintyComponent(
        source_family="GT_ACQUISITION_SCANNER",
        evidence_state="QUANTIFIED",
        uncertainty_mm=0.8,
        provenance_reference="verified scanner uncertainty",
    )

    with pytest.raises(
        ValueError,
        match="GT uncertainty floor|quantified|match|evidence",
    ):
        AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate(
            components=(scanner,),
            gt_uncertainty_floor_mm=99.0,
            gt_uncertainty_floor_state="ESTABLISHED",
            observed_metric_error_mm=1.0,
        )


def test_constructor_bypassed_uncertainty_component_cannot_establish_gt_floor():
    from CORE.atlas_canonical_head_metric_uncertainty import (
        AtlasCanonicalHeadMetricUncertaintyComponent,
        AtlasCanonicalHeadMetricUncertaintyEvaluation,
    )

    forged = object.__new__(
        AtlasCanonicalHeadMetricUncertaintyComponent
    )
    object.__setattr__(
        forged,
        "source_family",
        "GT_ACQUISITION_SCANNER",
    )
    object.__setattr__(
        forged,
        "evidence_state",
        "QUANTIFIED",
    )
    object.__setattr__(
        forged,
        "uncertainty_mm",
        0.8,
    )
    object.__setattr__(
        forged,
        "provenance_reference",
        "",
    )

    with pytest.raises(
        (TypeError, ValueError, AttributeError),
    ):
        AtlasCanonicalHeadMetricUncertaintyEvaluation.evaluate(
            components=(forged,),
            gt_uncertainty_floor_mm=0.8,
            gt_uncertainty_floor_state="ESTABLISHED",
            observed_metric_error_mm=1.0,
        )
