import pytest


# === PHASE 8 ITEM 10.11 REPEAT CAPTURE / REPEATABILITY RED ===


def test_defines_exact_locked_repeatability_dimensions():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    assert AtlasCanonicalHeadMetricRepeatabilityObservation.DIMENSIONS == (
        "REPEATED_SENSOR_ACQUISITION",
        "REPEATED_PREPROCESSING",
        "REPEATED_RECONSTRUCTION",
        "REPEATED_REGISTRATION_EVALUATION",
        "INTRA_RUN_REPEATABILITY",
        "INTER_RUN_REPEATABILITY",
        "INTER_CAPTURE_REPEATABILITY",
        "INTER_OPERATOR_REPEATABILITY",
    )


def test_quantified_repeatability_requires_numeric_value_and_provenance():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    observation = AtlasCanonicalHeadMetricRepeatabilityObservation(
        dimension="INTRA_RUN_REPEATABILITY",
        evidence_state="QUANTIFIED",
        repeatability_mm=0.18,
        provenance_reference="verified repeated reconstruction evidence",
    )

    assert observation.dimension == "INTRA_RUN_REPEATABILITY"
    assert observation.evidence_state == "QUANTIFIED"
    assert observation.repeatability_mm == pytest.approx(0.18)


def test_unresolved_repeatability_cannot_carry_fabricated_numeric_value():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    with pytest.raises(
        ValueError,
        match="UNRESOLVED|repeatability_mm|numeric",
    ):
        AtlasCanonicalHeadMetricRepeatabilityObservation(
            dimension="INTER_CAPTURE_REPEATABILITY",
            evidence_state="UNRESOLVED",
            repeatability_mm=0.0,
            provenance_reference="repeat capture unavailable",
        )


def test_quantified_repeatability_rejects_missing_provenance():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    with pytest.raises(ValueError, match="provenance"):
        AtlasCanonicalHeadMetricRepeatabilityObservation(
            dimension="INTER_RUN_REPEATABILITY",
            evidence_state="QUANTIFIED",
            repeatability_mm=0.25,
            provenance_reference="",
        )


def test_repeatability_rejects_negative_or_nonfinite_numeric_values():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    for value in (-0.1, float("inf"), float("nan")):
        with pytest.raises(ValueError, match="repeatability_mm"):
            AtlasCanonicalHeadMetricRepeatabilityObservation(
                dimension="REPEATED_RECONSTRUCTION",
                evidence_state="QUANTIFIED",
                repeatability_mm=value,
                provenance_reference="verified repeated measurement evidence",
            )


def test_unavailable_evidence_state_is_explicit_and_cannot_carry_numeric_value():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    observation = AtlasCanonicalHeadMetricRepeatabilityObservation(
        dimension="INTER_OPERATOR_REPEATABILITY",
        evidence_state="NOT_AVAILABLE",
        repeatability_mm=None,
        provenance_reference="operator-controlled dataset not available",
    )

    assert observation.evidence_state == "NOT_AVAILABLE"
    assert observation.repeatability_mm is None

    with pytest.raises(
        ValueError,
        match="NOT_AVAILABLE|repeatability_mm|numeric",
    ):
        AtlasCanonicalHeadMetricRepeatabilityObservation(
            dimension="INTER_OPERATOR_REPEATABILITY",
            evidence_state="NOT_AVAILABLE",
            repeatability_mm=0.2,
            provenance_reference="operator-controlled dataset not available",
        )


def test_repeatability_dimensions_remain_semantically_distinct():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    intra = AtlasCanonicalHeadMetricRepeatabilityObservation(
        dimension="INTRA_RUN_REPEATABILITY",
        evidence_state="QUANTIFIED",
        repeatability_mm=0.10,
        provenance_reference="same-run repeat evidence",
    )
    inter_run = AtlasCanonicalHeadMetricRepeatabilityObservation(
        dimension="INTER_RUN_REPEATABILITY",
        evidence_state="QUANTIFIED",
        repeatability_mm=0.15,
        provenance_reference="independent-run repeat evidence",
    )
    inter_capture = AtlasCanonicalHeadMetricRepeatabilityObservation(
        dimension="INTER_CAPTURE_REPEATABILITY",
        evidence_state="QUANTIFIED",
        repeatability_mm=0.30,
        provenance_reference="repeat-capture evidence",
    )

    assert intra.dimension != inter_run.dimension
    assert inter_run.dimension != inter_capture.dimension
    assert intra.repeatability_mm != inter_capture.repeatability_mm


def test_repeatability_summary_requires_unique_dimensions():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityEvaluation,
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    observation = AtlasCanonicalHeadMetricRepeatabilityObservation(
        dimension="INTRA_RUN_REPEATABILITY",
        evidence_state="QUANTIFIED",
        repeatability_mm=0.10,
        provenance_reference="same-run repeat evidence",
    )

    with pytest.raises(ValueError, match="duplicate|unique|dimension"):
        AtlasCanonicalHeadMetricRepeatabilityEvaluation.evaluate(
            observations=(observation, observation),
        )


def test_repeatability_evaluation_preserves_unresolved_and_not_available_states():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityEvaluation,
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    result = AtlasCanonicalHeadMetricRepeatabilityEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricRepeatabilityObservation(
                dimension="INTRA_RUN_REPEATABILITY",
                evidence_state="QUANTIFIED",
                repeatability_mm=0.12,
                provenance_reference="verified intra-run repeats",
            ),
            AtlasCanonicalHeadMetricRepeatabilityObservation(
                dimension="INTER_CAPTURE_REPEATABILITY",
                evidence_state="UNRESOLVED",
                repeatability_mm=None,
                provenance_reference="repeat-capture evidence unresolved",
            ),
            AtlasCanonicalHeadMetricRepeatabilityObservation(
                dimension="INTER_OPERATOR_REPEATABILITY",
                evidence_state="NOT_AVAILABLE",
                repeatability_mm=None,
                provenance_reference="operator-controlled dataset absent",
            ),
        ),
    )

    assert result.quantified_dimensions == (
        "INTRA_RUN_REPEATABILITY",
    )
    assert result.unresolved_dimensions == (
        "INTER_CAPTURE_REPEATABILITY",
    )
    assert result.not_available_dimensions == (
        "INTER_OPERATOR_REPEATABILITY",
    )


def test_repeatability_contract_does_not_expose_accuracy_or_trueness_claims():
    import inspect

    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityEvaluation,
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    observation_fields = {
        field.name
        for field in AtlasCanonicalHeadMetricRepeatabilityObservation.__dataclass_fields__.values()
    }
    evaluation_parameters = set(
        inspect.signature(
            AtlasCanonicalHeadMetricRepeatabilityEvaluation.evaluate
        ).parameters
    )

    forbidden = {
        "accuracy_mm",
        "accuracy",
        "trueness_mm",
        "trueness",
    }

    assert observation_fields.isdisjoint(forbidden)
    assert evaluation_parameters.isdisjoint(forbidden)


# === PHASE 8 ITEM 10.11 CLOSURE CHALLENGE CORRECTIVE RED ===


def test_partial_repeatability_evaluation_explicitly_reports_incomplete_dimension_coverage():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityEvaluation,
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    result = AtlasCanonicalHeadMetricRepeatabilityEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricRepeatabilityObservation(
                dimension="INTRA_RUN_REPEATABILITY",
                evidence_state="QUANTIFIED",
                repeatability_mm=0.10,
                provenance_reference="verified same-run repeat evidence",
            ),
        ),
    )

    assert result.coverage_state == "INCOMPLETE"
    assert result.missing_dimensions == (
        "REPEATED_SENSOR_ACQUISITION",
        "REPEATED_PREPROCESSING",
        "REPEATED_RECONSTRUCTION",
        "REPEATED_REGISTRATION_EVALUATION",
        "INTER_RUN_REPEATABILITY",
        "INTER_CAPTURE_REPEATABILITY",
        "INTER_OPERATOR_REPEATABILITY",
    )


def test_repeatability_evaluation_reports_complete_only_when_all_locked_dimensions_are_present():
    from CORE.atlas_canonical_head_metric_repeatability import (
        AtlasCanonicalHeadMetricRepeatabilityEvaluation,
        AtlasCanonicalHeadMetricRepeatabilityObservation,
    )

    observations = tuple(
        AtlasCanonicalHeadMetricRepeatabilityObservation(
            dimension=dimension,
            evidence_state="UNRESOLVED",
            repeatability_mm=None,
            provenance_reference=f"{dimension} evidence unresolved",
        )
        for dimension in AtlasCanonicalHeadMetricRepeatabilityObservation.DIMENSIONS
    )

    result = AtlasCanonicalHeadMetricRepeatabilityEvaluation.evaluate(
        observations=observations,
    )

    assert result.coverage_state == "COMPLETE"
    assert result.missing_dimensions == ()
