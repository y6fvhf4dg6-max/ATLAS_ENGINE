import pytest

from CORE.atlas_canonical_head_benchmark_evidence_coverage import (
    AtlasCanonicalHeadBenchmarkEvidenceCoverage,
)


QUALITY_CHANNELS = (
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
)


def _coverage(**overrides):
    values = {
        channel: "MISSING"
        for channel in QUALITY_CHANNELS
    }
    values.update(overrides)

    return AtlasCanonicalHeadBenchmarkEvidenceCoverage(
        candidate_id="flame-2023-open",
        **values,
    )


def test_coverage_preserves_candidate_identity_and_all_quality_channels():
    coverage = _coverage(
        identity_preservation_support="PARTIAL",
        multi_view_consistency="MEASURED",
        topology_suitability="DIRECT",
    )

    assert coverage.candidate_id == "flame-2023-open"
    assert coverage.identity_preservation_support == "PARTIAL"
    assert coverage.multi_view_consistency == "MEASURED"
    assert coverage.topology_suitability == "DIRECT"


@pytest.mark.parametrize(
    "state",
    (
        "MEASURED",
        "PARTIAL",
        "DIRECT",
        "MISSING",
    ),
)
def test_coverage_accepts_only_explicit_evidence_states(state):
    coverage = _coverage(
        multi_view_consistency=state,
    )

    assert coverage.multi_view_consistency == state


@pytest.mark.parametrize(
    "state",
    (
        "",
        "UNKNOWN",
        "GO",
        "HOLD",
        "REJECT",
        0.9,
        None,
    ),
)
def test_coverage_rejects_invalid_evidence_states(state):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        )
    ):
        _coverage(
            multi_view_consistency=state,
        )


def test_coverage_rejects_blank_candidate_id():
    with pytest.raises(ValueError):
        AtlasCanonicalHeadBenchmarkEvidenceCoverage(
            candidate_id="   ",
            **{
                channel: "MISSING"
                for channel in QUALITY_CHANNELS
            },
        )


def test_coverage_exposes_missing_channels_without_fabricating_support():
    coverage = _coverage(
        multi_view_consistency="MEASURED",
        topology_suitability="DIRECT",
    )

    assert set(coverage.missing_channels) == (
        set(QUALITY_CHANNELS)
        - {
            "multi_view_consistency",
            "topology_suitability",
        }
    )


def test_coverage_is_not_a_support_or_candidate_decision_contract():
    coverage = _coverage()

    assert not hasattr(coverage, "decision")
    assert not hasattr(coverage, "status")
    assert not hasattr(coverage, "phase_9_authorized")
    assert not hasattr(coverage, "normalized_support")
    assert not hasattr(coverage, "support_score")


def test_coverage_is_immutable():
    coverage = _coverage()

    with pytest.raises(
        (
            AttributeError,
            TypeError,
        )
    ):
        coverage.multi_view_consistency = "MEASURED"
