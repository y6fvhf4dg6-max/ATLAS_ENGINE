from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_canonical_head_benchmark_candidate_observation import (
    AtlasCanonicalHeadBenchmarkCandidateObservation,
)


def _observation(**overrides):
    values = {
        "candidate_id": "hybrid-head-v1",
        "architecture_kind": "hybrid_canonical_detail",
        "identity_preservation_support": 0.90,
        "multi_view_consistency": 0.86,
        "silhouette_profile_support": 0.84,
        "head_ratio_support": 0.82,
        "jaw_chin_support": 0.80,
        "nose_projection_support": 0.81,
        "orbital_cheek_volume_support": 0.79,
        "expression_separation_support": 0.92,
        "pose_separation_support": 0.94,
        "topology_suitability": 0.96,
        "physical_suitability": 0.85,
        "apple_silicon_runtime_support": 0.88,
        "reproducibility_support": 0.90,
        "commercial_license_acceptable": True,
        "privacy_data_retention_acceptable": True,
        "model_weight_restrictions_acceptable": True,
        "dataset_restrictions_acceptable": True,
        "processing_time_seconds": 18.0,
        "processing_cost_eur": 0.05,
    }
    values.update(overrides)
    return AtlasCanonicalHeadBenchmarkCandidateObservation(**values)


def test_normalizes_candidate_id_and_architecture_kind():
    observation = _observation(
        candidate_id="  Hybrid Head V1  ",
        architecture_kind="  HYBRID CANONICAL DETAIL  ",
    )

    assert observation.candidate_id == "Hybrid Head V1"
    assert observation.architecture_kind == "hybrid_canonical_detail"


@pytest.mark.parametrize(
    "architecture_kind",
    (
        "parametric_fixed_topology",
        "direct_neural_dense",
        "hybrid_canonical_detail",
    ),
)
def test_supported_architecture_kinds_are_accepted(
    architecture_kind,
):
    assert (
        _observation(
            architecture_kind=architecture_kind,
        ).architecture_kind
        == architecture_kind
    )


def test_unknown_architecture_kind_is_rejected():
    with pytest.raises(
        ValueError,
        match="architecture_kind",
    ):
        _observation(
            architecture_kind="generic_face_mesh",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "identity_preservation_support",
        "multi_view_consistency",
        "silhouette_profile_support",
        "head_ratio_support",
        "jaw_chin_support",
        "nose_projection_support",
        "orbital_cheek_volume_support",
        "expression_separation_support",
        "pose_separation_support",
        "topology_suitability",
        "physical_suitability",
        "apple_silicon_runtime_support",
        "reproducibility_support",
    ),
)
@pytest.mark.parametrize(
    "value",
    (-0.01, 1.01),
)
def test_support_channels_must_be_unit_interval(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _observation(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    (
        "commercial_license_acceptable",
        "privacy_data_retention_acceptable",
        "model_weight_restrictions_acceptable",
        "dataset_restrictions_acceptable",
    ),
)
def test_policy_evidence_must_be_boolean(field_name):
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _observation(**{field_name: 1})


def test_processing_time_must_be_finite_and_nonnegative():
    with pytest.raises(
        ValueError,
        match="processing_time_seconds",
    ):
        _observation(processing_time_seconds=-0.01)


def test_processing_cost_must_be_finite_and_nonnegative():
    with pytest.raises(
        ValueError,
        match="processing_cost_eur",
    ):
        _observation(processing_cost_eur=-0.01)


def test_observation_is_immutable():
    observation = _observation()

    with pytest.raises(FrozenInstanceError):
        observation.identity_preservation_support = 1.0


def test_observation_does_not_claim_final_benchmark_decision():
    observation = _observation()

    assert not hasattr(observation, "decision")
    assert not hasattr(observation, "production_status")
    assert not hasattr(observation, "selected_candidate")
    assert not hasattr(observation, "provider_id")
