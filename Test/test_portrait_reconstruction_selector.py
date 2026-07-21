from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from CORE.atlas_portrait_reconstruction_evaluation import (
    AtlasPortraitReconstructionEvaluation,
)
from CORE.atlas_portrait_reconstruction_selector import (
    AtlasPortraitReconstructionSelector,
)


def _candidate(
    *,
    model_name,
    model_version="1.0",
    commercial_use_allowed=True,
    supports_single_image=True,
    supports_multi_view=True,
    topology_type="fixed",
    supports_surface_normals=True,
    supports_landmark_vertex_map=True,
    supports_identity_parameters=True,
    supports_pose_parameters=True,
    deterministic_output=True,
    fixture_generation_supported=True,
    atlas_adapter_feasibility="high",
    maintenance_risk="low",
    runtime_seconds=2.0,
    peak_memory_mb=1000.0,
    semantic_regions=(
        "forehead",
        "left_eye_socket",
        "right_eye_socket",
        "nose_bridge",
        "nose_tip",
        "upper_lip",
        "lower_lip",
        "chin",
    ),
):
    return AtlasPortraitReconstructionEvaluation(
        approach_name="synthetic reconstruction",
        model_name=model_name,
        model_version=model_version,
        license_type="synthetic commercial fixture",
        commercial_use_allowed=commercial_use_allowed,
        redistribution_conditions=(
            "Synthetic test fixture only."
        ),
        supports_single_image=supports_single_image,
        supports_multi_view=supports_multi_view,
        topology_type=topology_type,
        vertex_count=5000,
        triangle_count=9900,
        supports_surface_normals=(
            supports_surface_normals
        ),
        supports_uv_coordinates=True,
        semantic_regions=semantic_regions,
        supports_landmark_vertex_map=(
            supports_landmark_vertex_map
        ),
        supports_identity_parameters=(
            supports_identity_parameters
        ),
        supports_expression_parameters=True,
        supports_pose_parameters=(
            supports_pose_parameters
        ),
        supports_confidence=True,
        supports_visibility=True,
        supports_apple_silicon=True,
        supported_python_versions=(
            "3.10",
            "3.11",
        ),
        requires_cpu=True,
        requires_gpu=False,
        runtime_seconds=runtime_seconds,
        peak_memory_mb=peak_memory_mb,
        deterministic_output=deterministic_output,
        fixture_generation_supported=(
            fixture_generation_supported
        ),
        atlas_adapter_feasibility=(
            atlas_adapter_feasibility
        ),
        maintenance_risk=maintenance_risk,
        metadata={
            "fixture": model_name,
        },
    )


def test_selector_requires_at_least_two_candidates():
    with pytest.raises(
        ValueError,
        match="at least two",
    ):
        AtlasPortraitReconstructionSelector.select(
            (
                _candidate(
                    model_name="Only Candidate",
                ),
            )
        )


def test_selector_rejects_non_evaluation_candidates():
    with pytest.raises(
        TypeError,
        match="candidates",
    ):
        AtlasPortraitReconstructionSelector.select(
            (
                _candidate(
                    model_name="Valid Candidate",
                ),
                object(),
            )
        )


def test_selector_returns_primary_and_backup():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Primary Candidate",
                runtime_seconds=1.5,
            ),
            _candidate(
                model_name="Backup Candidate",
                runtime_seconds=3.0,
            ),
        )
    )

    assert result.primary.model_name == (
        "Primary Candidate"
    )
    assert result.backup.model_name == (
        "Backup Candidate"
    )
    assert result.primary is not result.backup


def test_selector_prefers_high_adapter_feasibility():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Medium Adapter",
                atlas_adapter_feasibility="medium",
                runtime_seconds=0.5,
            ),
            _candidate(
                model_name="High Adapter",
                atlas_adapter_feasibility="high",
                runtime_seconds=5.0,
            ),
        )
    )

    assert result.primary.model_name == "High Adapter"


def test_selector_prefers_lower_maintenance_risk():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="High Maintenance",
                maintenance_risk="high",
                runtime_seconds=0.5,
            ),
            _candidate(
                model_name="Low Maintenance",
                maintenance_risk="low",
                runtime_seconds=5.0,
            ),
        )
    )

    assert result.primary.model_name == "Low Maintenance"


def test_selector_prefers_fixed_topology():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Variable Topology",
                topology_type="variable",
                runtime_seconds=0.5,
            ),
            _candidate(
                model_name="Fixed Topology",
                topology_type="fixed",
                runtime_seconds=5.0,
            ),
        )
    )

    assert result.primary.model_name == "Fixed Topology"


def test_selector_prefers_multi_view_support():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Single View Only",
                supports_multi_view=False,
                runtime_seconds=0.5,
            ),
            _candidate(
                model_name="Multi View",
                supports_multi_view=True,
                runtime_seconds=5.0,
            ),
        )
    )

    assert result.primary.model_name == "Multi View"


def test_selector_prefers_landmark_vertex_map():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="No Landmark Map",
                supports_landmark_vertex_map=False,
                runtime_seconds=0.5,
            ),
            _candidate(
                model_name="Landmark Map",
                supports_landmark_vertex_map=True,
                runtime_seconds=5.0,
            ),
        )
    )

    assert result.primary.model_name == "Landmark Map"


def test_selector_prefers_more_semantic_regions():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Few Regions",
                semantic_regions=(
                    "nose_tip",
                    "chin",
                ),
                runtime_seconds=0.5,
            ),
            _candidate(
                model_name="Many Regions",
                semantic_regions=(
                    "forehead",
                    "left_eye_socket",
                    "right_eye_socket",
                    "nose_bridge",
                    "nose_tip",
                    "upper_lip",
                    "lower_lip",
                    "chin",
                ),
                runtime_seconds=5.0,
            ),
        )
    )

    assert result.primary.model_name == "Many Regions"


def test_selector_uses_runtime_after_capabilities():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Slow Candidate",
                runtime_seconds=5.0,
            ),
            _candidate(
                model_name="Fast Candidate",
                runtime_seconds=1.0,
            ),
        )
    )

    assert result.primary.model_name == "Fast Candidate"


def test_selector_uses_memory_after_runtime():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="High Memory",
                runtime_seconds=2.0,
                peak_memory_mb=2000.0,
            ),
            _candidate(
                model_name="Low Memory",
                runtime_seconds=2.0,
                peak_memory_mb=800.0,
            ),
        )
    )

    assert result.primary.model_name == "Low Memory"


def test_selector_uses_deterministic_name_tie_break():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Zulu Model",
            ),
            _candidate(
                model_name="Alpha Model",
            ),
        )
    )

    assert result.primary.model_name == "Alpha Model"
    assert result.backup.model_name == "Zulu Model"


@pytest.mark.parametrize(
    (
        "candidate",
        "expected_reason",
    ),
    [
        (
            _candidate(
                model_name="Non Commercial",
                commercial_use_allowed=False,
            ),
            "commercial_use_not_allowed",
        ),
        (
            _candidate(
                model_name="No Single Image",
                supports_single_image=False,
            ),
            "single_image_not_supported",
        ),
        (
            _candidate(
                model_name="No Normals",
                supports_surface_normals=False,
            ),
            "surface_normals_not_supported",
        ),
        (
            _candidate(
                model_name="No Identity",
                supports_identity_parameters=False,
            ),
            "identity_parameters_not_supported",
        ),
        (
            _candidate(
                model_name="No Pose",
                supports_pose_parameters=False,
            ),
            "pose_parameters_not_supported",
        ),
        (
            _candidate(
                model_name="Not Deterministic",
                deterministic_output=False,
            ),
            "deterministic_output_not_supported",
        ),
        (
            _candidate(
                model_name="No Fixture",
                fixture_generation_supported=False,
            ),
            "fixture_generation_not_supported",
        ),
    ],
)
def test_selector_rejects_ineligible_candidate(
    candidate,
    expected_reason,
):
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Eligible Primary",
            ),
            _candidate(
                model_name="Eligible Backup",
                runtime_seconds=3.0,
            ),
            candidate,
        )
    )

    assert candidate not in result.ranked_candidates
    assert result.rejected_candidates[
        candidate.model_name
    ] == expected_reason


def test_selector_requires_two_eligible_candidates():
    with pytest.raises(
        ValueError,
        match="two eligible",
    ):
        AtlasPortraitReconstructionSelector.select(
            (
                _candidate(
                    model_name="Eligible Candidate",
                ),
                _candidate(
                    model_name="Rejected Candidate",
                    commercial_use_allowed=False,
                ),
            )
        )


def test_selection_result_is_frozen():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Primary Candidate",
            ),
            _candidate(
                model_name="Backup Candidate",
                runtime_seconds=3.0,
            ),
        )
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.primary = result.backup


def test_selection_collections_are_immutable():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Primary Candidate",
            ),
            _candidate(
                model_name="Backup Candidate",
                runtime_seconds=3.0,
            ),
            _candidate(
                model_name="Rejected Candidate",
                commercial_use_allowed=False,
            ),
        )
    )

    assert isinstance(
        result.ranked_candidates,
        tuple,
    )

    assert isinstance(
        result.rejected_candidates,
        MappingProxyType,
    )

    with pytest.raises(
        TypeError,
    ):
        result.rejected_candidates[
            "Rejected Candidate"
        ] = "changed"


def test_selection_records_policy_and_metadata():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Primary Candidate",
            ),
            _candidate(
                model_name="Backup Candidate",
                runtime_seconds=3.0,
            ),
        ),
        policy_version="portrait-reconstruction-v1",
        metadata={
            "fixture": "synthetic-selection",
        },
    )

    assert result.policy_version == (
        "portrait-reconstruction-v1"
    )

    assert result.metadata == {
        "fixture": "synthetic-selection",
    }


def test_selection_to_dict_is_deterministic():
    candidates = (
        _candidate(
            model_name="Primary Candidate",
        ),
        _candidate(
            model_name="Backup Candidate",
            runtime_seconds=3.0,
        ),
        _candidate(
            model_name="Rejected Candidate",
            commercial_use_allowed=False,
        ),
    )

    first = AtlasPortraitReconstructionSelector.select(
        candidates,
    )

    second = AtlasPortraitReconstructionSelector.select(
        tuple(
            reversed(
                candidates,
            )
        )
    )

    assert first.to_dict() == second.to_dict()


def test_selection_to_dict_contains_plain_values():
    result = AtlasPortraitReconstructionSelector.select(
        (
            _candidate(
                model_name="Primary Candidate",
            ),
            _candidate(
                model_name="Backup Candidate",
                runtime_seconds=3.0,
            ),
            _candidate(
                model_name="Rejected Candidate",
                commercial_use_allowed=False,
            ),
        )
    )

    payload = result.to_dict()

    assert payload["primary_model_name"] == (
        "Primary Candidate"
    )

    assert payload["backup_model_name"] == (
        "Backup Candidate"
    )

    assert payload["ranked_model_names"] == [
        "Primary Candidate",
        "Backup Candidate",
    ]

    assert payload["rejected_candidates"] == {
        "Rejected Candidate": (
            "commercial_use_not_allowed"
        ),
    }
