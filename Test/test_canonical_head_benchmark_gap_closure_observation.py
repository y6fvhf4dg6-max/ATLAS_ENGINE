import pytest

from CORE.atlas_canonical_head_benchmark_evidence_coverage import (
    AtlasCanonicalHeadBenchmarkEvidenceCoverage,
)
from CORE.atlas_canonical_head_benchmark_gap_closure_observation import (
    AtlasCanonicalHeadBenchmarkGapClosureObservation,
)


def _coverage(**overrides):
    values = {
        "candidate_id": "candidate-a",
        "identity_preservation_support": "PARTIAL",
        "multi_view_consistency": "MEASURED",
        "silhouette_profile_support": "MISSING",
        "head_ratio_support": "MISSING",
        "jaw_chin_support": "MISSING",
        "nose_projection_support": "MISSING",
        "orbital_cheek_volume_support": "MISSING",
        "expression_separation_support": "MISSING",
        "pose_separation_support": "PARTIAL",
        "topology_suitability": "DIRECT",
        "physical_suitability": "MISSING",
        "apple_silicon_runtime_support": "DIRECT",
        "reproducibility_support": "DIRECT",
    }
    values.update(overrides)
    return AtlasCanonicalHeadBenchmarkEvidenceCoverage(**values)


def test_records_unresolved_quality_channels_without_support_fabrication():
    observation = AtlasCanonicalHeadBenchmarkGapClosureObservation(
        candidate_id="candidate-a",
        architecture_kind="parametric_fixed_topology",
        coverage=_coverage(),
        commercial_license_state="ACCEPTABLE",
        privacy_data_retention_state="UNRESOLVED",
        model_weight_restrictions_state="UNRESOLVED",
        dataset_restrictions_state="UNRESOLVED",
        evidence_limitations=(
            "NO_METRIC_3D_GROUND_TRUTH",
        ),
    )

    assert observation.unresolved_quality_channels == (
        "identity_preservation_support",
        "silhouette_profile_support",
        "head_ratio_support",
        "jaw_chin_support",
        "nose_projection_support",
        "orbital_cheek_volume_support",
        "expression_separation_support",
        "pose_separation_support",
        "physical_suitability",
    )

    assert observation.blocked_policy_channels == ()
    assert observation.unresolved_policy_channels == (
        "privacy_data_retention_state",
        "model_weight_restrictions_state",
        "dataset_restrictions_state",
    )

    assert observation.evidence_limitations == (
        "NO_METRIC_3D_GROUND_TRUTH",
    )

    assert not hasattr(observation, "support_score")
    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "phase_9_authorized")


def test_records_verified_policy_blockers_separately_from_unresolved_policy():
    observation = AtlasCanonicalHeadBenchmarkGapClosureObservation(
        candidate_id="prnet",
        architecture_kind="direct_neural_dense",
        coverage=_coverage(candidate_id="prnet"),
        commercial_license_state="BLOCKED",
        privacy_data_retention_state="UNRESOLVED",
        model_weight_restrictions_state="BLOCKED",
        dataset_restrictions_state="BLOCKED",
        evidence_limitations=(
            "PRETRAINED_MODEL_TRAINING_DATA_NONCOMMERCIAL",
        ),
    )

    assert observation.blocked_policy_channels == (
        "commercial_license_state",
        "model_weight_restrictions_state",
        "dataset_restrictions_state",
    )
    assert observation.unresolved_policy_channels == (
        "privacy_data_retention_state",
    )


@pytest.mark.parametrize(
    "state",
    ("ACCEPTABLE", "BLOCKED", "UNRESOLVED"),
)
def test_accepts_only_explicit_policy_evidence_states(state):
    observation = AtlasCanonicalHeadBenchmarkGapClosureObservation(
        candidate_id="candidate-a",
        architecture_kind="hybrid_canonical_detail",
        coverage=_coverage(),
        commercial_license_state=state,
        privacy_data_retention_state=state,
        model_weight_restrictions_state=state,
        dataset_restrictions_state=state,
        evidence_limitations=(),
    )

    assert observation.commercial_license_state == state


def test_rejects_candidate_id_mismatch_with_coverage():
    with pytest.raises(ValueError, match="candidate_id"):
        AtlasCanonicalHeadBenchmarkGapClosureObservation(
            candidate_id="candidate-b",
            architecture_kind="parametric_fixed_topology",
            coverage=_coverage(),
            commercial_license_state="ACCEPTABLE",
            privacy_data_retention_state="UNRESOLVED",
            model_weight_restrictions_state="UNRESOLVED",
            dataset_restrictions_state="UNRESOLVED",
            evidence_limitations=(),
        )


def test_rejects_unknown_policy_state():
    with pytest.raises(ValueError, match="commercial_license_state"):
        AtlasCanonicalHeadBenchmarkGapClosureObservation(
            candidate_id="candidate-a",
            architecture_kind="parametric_fixed_topology",
            coverage=_coverage(),
            commercial_license_state="MAYBE",
            privacy_data_retention_state="UNRESOLVED",
            model_weight_restrictions_state="UNRESOLVED",
            dataset_restrictions_state="UNRESOLVED",
            evidence_limitations=(),
        )
