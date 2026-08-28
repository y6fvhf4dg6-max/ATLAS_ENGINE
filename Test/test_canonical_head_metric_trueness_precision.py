import pytest


# === PHASE 8 ITEM 10.12 TRUENESS VS PRECISION RED ===


def test_defines_exact_locked_measurement_concepts():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    assert AtlasCanonicalHeadMetricTruenessPrecisionObservation.CONCEPTS == (
        "TRUENESS",
        "PRECISION",
    )


def test_trueness_and_precision_have_distinct_evidence_roles():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    trueness = AtlasCanonicalHeadMetricTruenessPrecisionObservation(
        concept="TRUENESS",
        evidence_state="QUANTIFIED",
        value_mm=0.42,
        provenance_reference="admissible reference-truth comparison",
        evidence_basis="REFERENCE_TRUTH_COMPARISON",
    )
    precision = AtlasCanonicalHeadMetricTruenessPrecisionObservation(
        concept="PRECISION",
        evidence_state="QUANTIFIED",
        value_mm=0.18,
        provenance_reference="repeated-measurement dispersion evidence",
        evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
    )

    assert trueness.concept == "TRUENESS"
    assert precision.concept == "PRECISION"
    assert trueness.value_mm == pytest.approx(0.42)
    assert precision.value_mm == pytest.approx(0.18)


def test_quantified_measurement_concept_requires_numeric_value_and_provenance():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    with pytest.raises(ValueError, match="value_mm|QUANTIFIED"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="TRUENESS",
            evidence_state="QUANTIFIED",
            value_mm=None,
            provenance_reference="reference truth available",
            evidence_basis="REFERENCE_TRUTH_COMPARISON",
        )

    with pytest.raises(ValueError, match="provenance"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="PRECISION",
            evidence_state="QUANTIFIED",
            value_mm=0.2,
            provenance_reference="",
            evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
        )


def test_unresolved_measurement_concept_cannot_carry_fabricated_numeric_value():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    with pytest.raises(ValueError, match="UNRESOLVED|value_mm|numeric"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="TRUENESS",
            evidence_state="UNRESOLVED",
            value_mm=0.0,
            provenance_reference="reference truth unresolved",
        )


def test_measurement_values_reject_negative_or_nonfinite_numbers():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    for value in (-0.1, float("inf"), float("-inf"), float("nan")):
        with pytest.raises(ValueError, match="value_mm"):
            AtlasCanonicalHeadMetricTruenessPrecisionObservation(
                concept="PRECISION",
                evidence_state="QUANTIFIED",
                value_mm=value,
                provenance_reference="repeated measurement evidence",
                evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
            )


def test_evaluation_requires_unique_trueness_and_precision_concepts():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluation,
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    observation = AtlasCanonicalHeadMetricTruenessPrecisionObservation(
        concept="TRUENESS",
        evidence_state="UNRESOLVED",
        value_mm=None,
        provenance_reference="reference truth unresolved",
    )

    with pytest.raises(ValueError, match="unique|duplicate"):
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluation.evaluate(
            observations=(observation, observation),
        )


def test_evaluation_reports_missing_concepts_explicitly():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluation,
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    result = AtlasCanonicalHeadMetricTruenessPrecisionEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricTruenessPrecisionObservation(
                concept="PRECISION",
                evidence_state="QUANTIFIED",
                value_mm=0.15,
                provenance_reference="repeat measurement evidence",
                evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
            ),
        ),
    )

    assert result.coverage_state == "INCOMPLETE"
    assert result.missing_concepts == ("TRUENESS",)


def test_complete_coverage_requires_both_trueness_and_precision():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluation,
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    result = AtlasCanonicalHeadMetricTruenessPrecisionEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricTruenessPrecisionObservation(
                concept="TRUENESS",
                evidence_state="UNRESOLVED",
                value_mm=None,
                provenance_reference="reference-truth evidence unresolved",
            ),
            AtlasCanonicalHeadMetricTruenessPrecisionObservation(
                concept="PRECISION",
                evidence_state="QUANTIFIED",
                value_mm=0.15,
                provenance_reference="repeat measurement evidence",
                evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
            ),
        ),
    )

    assert result.coverage_state == "COMPLETE"
    assert result.quantified_concepts == ("PRECISION",)
    assert result.unresolved_concepts == ("TRUENESS",)


def test_repeatability_is_not_accepted_as_a_trueness_or_accuracy_alias():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    for forbidden_concept in ("REPEATABILITY", "ACCURACY"):
        with pytest.raises(ValueError, match="concept"):
            AtlasCanonicalHeadMetricTruenessPrecisionObservation(
                concept=forbidden_concept,
                evidence_state="QUANTIFIED",
                value_mm=0.1,
                provenance_reference="repeatability evidence",
            )


def test_contract_does_not_expose_accuracy_or_repeatability_result_fields():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluationResult,
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    observation_fields = {
        field.name
        for field in AtlasCanonicalHeadMetricTruenessPrecisionObservation.__dataclass_fields__.values()
    }
    result_fields = {
        field.name
        for field in AtlasCanonicalHeadMetricTruenessPrecisionEvaluationResult.__dataclass_fields__.values()
    }

    forbidden = {
        "accuracy",
        "accuracy_mm",
        "repeatability",
        "repeatability_mm",
    }

    assert observation_fields.isdisjoint(forbidden)
    assert result_fields.isdisjoint(forbidden)


def test_constructor_bypassed_observation_is_revalidated_during_evaluation():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluation,
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    forged = object.__new__(
        AtlasCanonicalHeadMetricTruenessPrecisionObservation
    )
    object.__setattr__(forged, "concept", "TRUENESS")
    object.__setattr__(forged, "evidence_state", "QUANTIFIED")
    object.__setattr__(forged, "value_mm", None)
    object.__setattr__(
        forged,
        "provenance_reference",
        "forged incomplete observation",
    )

    with pytest.raises(ValueError, match="complete|contract|QUANTIFIED|value_mm"):
        AtlasCanonicalHeadMetricTruenessPrecisionEvaluation.evaluate(
            observations=(forged,),
        )


# === ITEM 10.12 CLOSURE CHALLENGE V1 CORRECTIVE RED ===


def test_measurement_concepts_require_exact_semantic_evidence_basis():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    trueness = AtlasCanonicalHeadMetricTruenessPrecisionObservation(
        concept="TRUENESS",
        evidence_state="QUANTIFIED",
        value_mm=0.42,
        provenance_reference="admissible reference-truth comparison",
        evidence_basis="REFERENCE_TRUTH_COMPARISON",
    )
    precision = AtlasCanonicalHeadMetricTruenessPrecisionObservation(
        concept="PRECISION",
        evidence_state="QUANTIFIED",
        value_mm=0.18,
        provenance_reference="repeated-measurement consistency evidence",
        evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
    )

    assert trueness.evidence_basis == "REFERENCE_TRUTH_COMPARISON"
    assert precision.evidence_basis == "REPEATED_MEASUREMENT_CONSISTENCY"


def test_trueness_rejects_repeated_measurement_basis():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    with pytest.raises(ValueError, match="evidence_basis|TRUENESS|reference"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="TRUENESS",
            evidence_state="QUANTIFIED",
            value_mm=0.20,
            provenance_reference="repeat measurement evidence",
            evidence_basis="REPEATED_MEASUREMENT_CONSISTENCY",
        )


def test_precision_rejects_reference_truth_basis():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    with pytest.raises(ValueError, match="evidence_basis|PRECISION|repeated"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="PRECISION",
            evidence_state="QUANTIFIED",
            value_mm=0.20,
            provenance_reference="reference truth evidence",
            evidence_basis="REFERENCE_TRUTH_COMPARISON",
        )


# === ITEM 10.12 CLOSURE CHALLENGE V2 CORRECTIVE RED ===


def test_quantified_trueness_requires_explicit_reference_truth_basis():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    with pytest.raises(ValueError, match="evidence_basis|explicit|required"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="TRUENESS",
            evidence_state="QUANTIFIED",
            value_mm=0.20,
            provenance_reference="measurement evidence without explicit basis",
        )


def test_quantified_precision_requires_explicit_repeated_measurement_basis():
    from CORE.atlas_canonical_head_metric_trueness_precision import (
        AtlasCanonicalHeadMetricTruenessPrecisionObservation,
    )

    with pytest.raises(ValueError, match="evidence_basis|explicit|required"):
        AtlasCanonicalHeadMetricTruenessPrecisionObservation(
            concept="PRECISION",
            evidence_state="QUANTIFIED",
            value_mm=0.20,
            provenance_reference="measurement evidence without explicit basis",
        )
