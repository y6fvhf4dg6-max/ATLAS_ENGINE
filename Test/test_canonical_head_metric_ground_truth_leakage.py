import pytest


# === PHASE 8 ITEM 10.13 GROUND-TRUTH LEAKAGE RED ===


def test_defines_exact_locked_ground_truth_leakage_dimensions():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    assert AtlasCanonicalHeadMetricGroundTruthLeakageObservation.DIMENSIONS == (
        "GROUND_TRUTH_USAGE",
        "SUBJECT_TRAINING_OVERLAP",
        "VALIDATION_OVERLAP",
        "REGISTRATION_LEAKAGE",
        "CORRESPONDENCE_LEAKAGE",
        "EVALUATION_REGION_LEAKAGE",
        "POST_HOC_REGION_SELECTION",
        "REPEATED_BENCHMARK_ADAPTATION",
    )


def test_ground_truth_usage_classification_is_explicit():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    usage = AtlasCanonicalHeadMetricGroundTruthUsage(
        evaluation_only=True,
        used_during_fitting=False,
        used_during_tuning=False,
        used_during_model_selection=False,
        provenance_reference="benchmark protocol",
    )

    assert usage.evaluation_only is True
    assert usage.used_during_fitting is False
    assert usage.used_during_tuning is False
    assert usage.used_during_model_selection is False


def test_ground_truth_cannot_be_evaluation_only_and_used_for_optimization():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    for field in (
        "used_during_fitting",
        "used_during_tuning",
        "used_during_model_selection",
    ):
        kwargs = {
            "evaluation_only": True,
            "used_during_fitting": False,
            "used_during_tuning": False,
            "used_during_model_selection": False,
            "provenance_reference": "benchmark protocol",
        }
        kwargs[field] = True

        with pytest.raises(
            ValueError,
            match="evaluation_only|fitting|tuning|model",
        ):
            AtlasCanonicalHeadMetricGroundTruthUsage(**kwargs)


def test_ground_truth_usage_requires_provenance():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    with pytest.raises(ValueError, match="provenance"):
        AtlasCanonicalHeadMetricGroundTruthUsage(
            evaluation_only=True,
            used_during_fitting=False,
            used_during_tuning=False,
            used_during_model_selection=False,
            provenance_reference="",
        )


def test_leakage_observation_supports_explicit_evidence_states():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    clean = AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
        dimension="SUBJECT_TRAINING_OVERLAP",
        evidence_state="NO_LEAKAGE_IDENTIFIED",
        provenance_reference="subject split audit",
    )
    present = AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
        dimension="VALIDATION_OVERLAP",
        evidence_state="LEAKAGE_PRESENT",
        provenance_reference="validation split audit",
    )
    unresolved = AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
        dimension="REPEATED_BENCHMARK_ADAPTATION",
        evidence_state="UNRESOLVED",
        provenance_reference="adaptation history unavailable",
    )
    not_applicable = AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
        dimension="POST_HOC_REGION_SELECTION",
        evidence_state="NOT_APPLICABLE",
        provenance_reference="no region selection stage",
    )

    assert clean.evidence_state == "NO_LEAKAGE_IDENTIFIED"
    assert present.evidence_state == "LEAKAGE_PRESENT"
    assert unresolved.evidence_state == "UNRESOLVED"
    assert not_applicable.evidence_state == "NOT_APPLICABLE"


def test_leakage_observation_rejects_unknown_dimension_or_state():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    with pytest.raises(ValueError, match="dimension"):
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
            dimension="SILENT_GT_REUSE",
            evidence_state="UNRESOLVED",
            provenance_reference="audit",
        )

    with pytest.raises(ValueError, match="evidence_state"):
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
            dimension="CORRESPONDENCE_LEAKAGE",
            evidence_state="PROBABLY_FINE",
            provenance_reference="audit",
        )


def test_leakage_observation_requires_provenance():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    with pytest.raises(ValueError, match="provenance"):
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
            dimension="REGISTRATION_LEAKAGE",
            evidence_state="UNRESOLVED",
            provenance_reference="",
        )


def test_evaluation_requires_unique_dimensions():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    observation = AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
        dimension="CORRESPONDENCE_LEAKAGE",
        evidence_state="UNRESOLVED",
        provenance_reference="correspondence audit pending",
    )

    with pytest.raises(ValueError, match="unique|duplicate"):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(observation, observation),
        )


def test_partial_leakage_audit_reports_incomplete_coverage():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="SUBJECT_TRAINING_OVERLAP",
                evidence_state="NO_LEAKAGE_IDENTIFIED",
                provenance_reference="subject split audit",
            ),
        ),
    )

    assert result.coverage_state == "INCOMPLETE"
    assert "VALIDATION_OVERLAP" in result.missing_dimensions
    assert "REGISTRATION_LEAKAGE" in result.missing_dimensions


def test_complete_coverage_requires_all_locked_dimensions():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    observations = tuple(
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
            dimension=dimension,
            evidence_state=(
                "NO_LEAKAGE_IDENTIFIED"
                if dimension == "GROUND_TRUTH_USAGE"
                else "UNRESOLVED"
            ),
            provenance_reference=(
                "evaluation-only benchmark protocol"
                if dimension == "GROUND_TRUTH_USAGE"
                else f"{dimension} audit unresolved"
            ),
        )
        for dimension in AtlasCanonicalHeadMetricGroundTruthLeakageObservation.DIMENSIONS
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=observations,
        ground_truth_usage=AtlasCanonicalHeadMetricGroundTruthUsage(
            evaluation_only=True,
            used_during_fitting=False,
            used_during_tuning=False,
            used_during_model_selection=False,
            provenance_reference="evaluation-only benchmark protocol",
        ),
    )

    assert result.coverage_state == "COMPLETE"
    assert result.missing_dimensions == ()


def test_evaluation_preserves_present_and_unresolved_leakage_states():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="REGISTRATION_LEAKAGE",
                evidence_state="LEAKAGE_PRESENT",
                provenance_reference="registration dependency audit",
            ),
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="CORRESPONDENCE_LEAKAGE",
                evidence_state="UNRESOLVED",
                provenance_reference="correspondence dependency unresolved",
            ),
        ),
    )

    assert result.leakage_present_dimensions == ("REGISTRATION_LEAKAGE",)
    assert result.unresolved_dimensions == ("CORRESPONDENCE_LEAKAGE",)


def test_constructor_bypassed_observation_is_revalidated():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    forged = object.__new__(
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation
    )
    object.__setattr__(forged, "dimension", "REGISTRATION_LEAKAGE")
    object.__setattr__(forged, "evidence_state", "SAFE")
    object.__setattr__(
        forged,
        "provenance_reference",
        "forged invalid observation",
    )

    with pytest.raises(
        ValueError,
        match="complete|contract|evidence_state",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(forged,),
        )


def test_contract_does_not_convert_unresolved_leakage_into_clean_evidence():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="EVALUATION_REGION_LEAKAGE",
                evidence_state="UNRESOLVED",
                provenance_reference="region audit unavailable",
            ),
        ),
    )

    assert result.no_leakage_identified_dimensions == ()
    assert result.unresolved_dimensions == ("EVALUATION_REGION_LEAKAGE",)


# === ITEM 10.13 CLOSURE CHALLENGE V1 CORRECTIVE RED ===


def test_evaluation_requires_explicit_ground_truth_usage_object():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    with pytest.raises(
        (TypeError, ValueError),
        match="ground_truth_usage|usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="NO_LEAKAGE_IDENTIFIED",
                    provenance_reference="claimed evaluation-only use",
                ),
            ),
            ground_truth_usage=None,
        )


def test_ground_truth_usage_observation_cannot_claim_clean_when_gt_was_used_for_fitting():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    usage = AtlasCanonicalHeadMetricGroundTruthUsage(
        evaluation_only=False,
        used_during_fitting=True,
        used_during_tuning=False,
        used_during_model_selection=False,
        provenance_reference="fitting protocol",
    )

    with pytest.raises(
        ValueError,
        match="GROUND_TRUTH_USAGE|fitting|LEAKAGE_PRESENT|usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="NO_LEAKAGE_IDENTIFIED",
                    provenance_reference="contradictory clean claim",
                ),
            ),
            ground_truth_usage=usage,
        )


def test_ground_truth_usage_observation_can_report_leakage_when_dependency_is_explicit():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    usage = AtlasCanonicalHeadMetricGroundTruthUsage(
        evaluation_only=False,
        used_during_fitting=False,
        used_during_tuning=True,
        used_during_model_selection=False,
        provenance_reference="tuning protocol",
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="GROUND_TRUTH_USAGE",
                evidence_state="LEAKAGE_PRESENT",
                provenance_reference="GT dependency explicitly classified",
            ),
        ),
        ground_truth_usage=usage,
    )

    assert result.leakage_present_dimensions == ("GROUND_TRUTH_USAGE",)


def test_evaluation_only_gt_cannot_be_classified_as_usage_leakage_present():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    usage = AtlasCanonicalHeadMetricGroundTruthUsage(
        evaluation_only=True,
        used_during_fitting=False,
        used_during_tuning=False,
        used_during_model_selection=False,
        provenance_reference="evaluation protocol",
    )

    with pytest.raises(
        ValueError,
        match="GROUND_TRUTH_USAGE|evaluation_only|NO_LEAKAGE_IDENTIFIED|usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="LEAKAGE_PRESENT",
                    provenance_reference="contradictory leakage claim",
                ),
            ),
            ground_truth_usage=usage,
        )


# === ITEM 10.13 CLOSURE CHALLENGE V2 CORRECTIVE RED ===


def test_unresolved_ground_truth_usage_does_not_require_known_usage_object():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="GROUND_TRUTH_USAGE",
                evidence_state="UNRESOLVED",
                provenance_reference="historical GT usage record unavailable",
            ),
        ),
    )

    assert result.unresolved_dimensions == ("GROUND_TRUTH_USAGE",)


def test_not_applicable_ground_truth_usage_does_not_require_usage_object():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    result = AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
        observations=(
            AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                dimension="GROUND_TRUTH_USAGE",
                evidence_state="NOT_APPLICABLE",
                provenance_reference="no ground-truth dataset in this evaluation path",
            ),
        ),
    )

    assert result.not_applicable_dimensions == ("GROUND_TRUTH_USAGE",)


def test_known_ground_truth_usage_still_requires_explicit_usage_object_for_clean_claim():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    with pytest.raises(
        (TypeError, ValueError),
        match="GROUND_TRUTH_USAGE|ground_truth_usage|usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="NO_LEAKAGE_IDENTIFIED",
                    provenance_reference="claimed clean GT usage",
                ),
            ),
        )


def test_known_ground_truth_usage_still_requires_explicit_usage_object_for_leakage_claim():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
    )

    with pytest.raises(
        (TypeError, ValueError),
        match="GROUND_TRUTH_USAGE|ground_truth_usage|usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="LEAKAGE_PRESENT",
                    provenance_reference="claimed GT dependency",
                ),
            ),
        )


# === ITEM 10.13 CLOSURE CHALLENGE V3 CORRECTIVE RED ===


def test_known_evaluation_only_usage_cannot_remain_unresolved():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    with pytest.raises(
        ValueError,
        match="GROUND_TRUTH_USAGE|UNRESOLVED|known|ground_truth_usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="UNRESOLVED",
                    provenance_reference="claimed unresolved usage",
                ),
            ),
            ground_truth_usage=AtlasCanonicalHeadMetricGroundTruthUsage(
                evaluation_only=True,
                used_during_fitting=False,
                used_during_tuning=False,
                used_during_model_selection=False,
                provenance_reference="known evaluation-only protocol",
            ),
        )


def test_known_fitting_dependency_cannot_be_not_applicable():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    with pytest.raises(
        ValueError,
        match="GROUND_TRUTH_USAGE|NOT_APPLICABLE|known|ground_truth_usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="NOT_APPLICABLE",
                    provenance_reference="claimed not applicable",
                ),
            ),
            ground_truth_usage=AtlasCanonicalHeadMetricGroundTruthUsage(
                evaluation_only=False,
                used_during_fitting=True,
                used_during_tuning=False,
                used_during_model_selection=False,
                provenance_reference="known fitting dependency",
            ),
        )


def test_known_tuning_dependency_cannot_remain_unresolved():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    with pytest.raises(
        ValueError,
        match="GROUND_TRUTH_USAGE|UNRESOLVED|known|ground_truth_usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="UNRESOLVED",
                    provenance_reference="claimed unresolved tuning usage",
                ),
            ),
            ground_truth_usage=AtlasCanonicalHeadMetricGroundTruthUsage(
                evaluation_only=False,
                used_during_fitting=False,
                used_during_tuning=True,
                used_during_model_selection=False,
                provenance_reference="known tuning dependency",
            ),
        )


def test_known_model_selection_dependency_cannot_be_not_applicable():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    with pytest.raises(
        ValueError,
        match="GROUND_TRUTH_USAGE|NOT_APPLICABLE|known|ground_truth_usage",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="NOT_APPLICABLE",
                    provenance_reference="claimed not applicable model-selection usage",
                ),
            ),
            ground_truth_usage=AtlasCanonicalHeadMetricGroundTruthUsage(
                evaluation_only=False,
                used_during_fitting=False,
                used_during_tuning=False,
                used_during_model_selection=True,
                provenance_reference="known model-selection dependency",
            ),
        )


# === ITEM 10.13 CLOSURE CHALLENGE V4 CORRECTIVE RED ===


def test_ground_truth_usage_rejects_all_false_known_usage_state():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    with pytest.raises(
        ValueError,
        match="usage|evaluation_only|fitting|tuning|model",
    ):
        AtlasCanonicalHeadMetricGroundTruthUsage(
            evaluation_only=False,
            used_during_fitting=False,
            used_during_tuning=False,
            used_during_model_selection=False,
            provenance_reference="usage audit",
        )


def test_all_false_usage_cannot_drive_clean_ground_truth_usage_claim():
    from CORE.atlas_canonical_head_metric_ground_truth_leakage import (
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation,
        AtlasCanonicalHeadMetricGroundTruthLeakageObservation,
        AtlasCanonicalHeadMetricGroundTruthUsage,
    )

    forged = object.__new__(AtlasCanonicalHeadMetricGroundTruthUsage)
    object.__setattr__(forged, "evaluation_only", False)
    object.__setattr__(forged, "used_during_fitting", False)
    object.__setattr__(forged, "used_during_tuning", False)
    object.__setattr__(forged, "used_during_model_selection", False)
    object.__setattr__(forged, "provenance_reference", "forged all-false usage")

    with pytest.raises(
        ValueError,
        match="usage|evaluation_only|fitting|tuning|model",
    ):
        AtlasCanonicalHeadMetricGroundTruthLeakageEvaluation.evaluate(
            observations=(
                AtlasCanonicalHeadMetricGroundTruthLeakageObservation(
                    dimension="GROUND_TRUTH_USAGE",
                    evidence_state="NO_LEAKAGE_IDENTIFIED",
                    provenance_reference="claimed clean usage",
                ),
            ),
            ground_truth_usage=forged,
        )
