from dataclasses import FrozenInstanceError
from types import MappingProxyType

import pytest

from CORE.atlas_portrait_reconstruction_evaluation import (
    AtlasPortraitReconstructionEvaluation,
)


def _evaluation(
    **overrides,
):
    values = {
        "approach_name": "FLAME fitting",
        "model_name": "Candidate Face Model",
        "model_version": "1.2.0",
        "license_type": "Research and commercial license",
        "commercial_use_allowed": True,
        "redistribution_conditions": (
            "Model weights may not be redistributed."
        ),
        "supports_single_image": True,
        "supports_multi_view": True,
        "topology_type": "fixed",
        "vertex_count": 5023,
        "triangle_count": 9976,
        "supports_surface_normals": True,
        "supports_uv_coordinates": True,
        "semantic_regions": (
            "nose_tip",
            "left_eye_socket",
            "right_eye_socket",
            "upper_lip",
            "lower_lip",
        ),
        "supports_landmark_vertex_map": True,
        "supports_identity_parameters": True,
        "supports_expression_parameters": True,
        "supports_pose_parameters": True,
        "supports_confidence": True,
        "supports_visibility": True,
        "supports_apple_silicon": True,
        "supported_python_versions": (
            "3.10",
            "3.11",
        ),
        "requires_cpu": True,
        "requires_gpu": False,
        "runtime_seconds": 2.75,
        "peak_memory_mb": 1840.0,
        "deterministic_output": True,
        "fixture_generation_supported": True,
        "atlas_adapter_feasibility": "high",
        "maintenance_risk": "medium",
        "metadata": {
            "provider": "synthetic-fixture",
            "evaluation_version": 1,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitReconstructionEvaluation(
        **values,
    )


def test_evaluation_preserves_normalized_contract():
    result = _evaluation()

    assert result.approach_name == "FLAME fitting"
    assert result.model_name == "Candidate Face Model"
    assert result.model_version == "1.2.0"

    assert result.topology_type == "fixed"
    assert result.vertex_count == 5023
    assert result.triangle_count == 9976

    assert result.atlas_adapter_feasibility == "high"
    assert result.maintenance_risk == "medium"


def test_evaluation_preserves_capability_flags():
    result = _evaluation()

    assert result.commercial_use_allowed
    assert result.supports_single_image
    assert result.supports_multi_view
    assert result.supports_surface_normals
    assert result.supports_uv_coordinates
    assert result.supports_landmark_vertex_map
    assert result.supports_identity_parameters
    assert result.supports_expression_parameters
    assert result.supports_pose_parameters
    assert result.supports_confidence
    assert result.supports_visibility
    assert result.supports_apple_silicon
    assert result.requires_cpu
    assert not result.requires_gpu
    assert result.deterministic_output
    assert result.fixture_generation_supported


def test_evaluation_normalizes_semantic_regions():
    result = _evaluation(
        semantic_regions=(
            " upper_lip ",
            "nose_tip",
            "upper_lip",
            "left_eye_socket",
        ),
    )

    assert result.semantic_regions == (
        "left_eye_socket",
        "nose_tip",
        "upper_lip",
    )


def test_evaluation_normalizes_python_versions():
    result = _evaluation(
        supported_python_versions=(
            " 3.11 ",
            "3.10",
            "3.11",
        ),
    )

    assert result.supported_python_versions == (
        "3.10",
        "3.11",
    )


def test_evaluation_is_frozen():
    result = _evaluation()

    with pytest.raises(
        FrozenInstanceError,
    ):
        result.model_name = "Changed"


def test_evaluation_metadata_is_read_only():
    result = _evaluation()

    assert isinstance(
        result.metadata,
        MappingProxyType,
    )

    with pytest.raises(
        TypeError,
    ):
        result.metadata["provider"] = "changed"


def test_evaluation_does_not_share_input_metadata():
    metadata = {
        "provider": "synthetic-fixture",
    }

    result = _evaluation(
        metadata=metadata,
    )

    metadata["provider"] = "changed"

    assert result.metadata["provider"] == (
        "synthetic-fixture"
    )


def test_evaluation_to_dict_is_deterministic():
    first = _evaluation()
    second = _evaluation()

    assert first.to_dict() == second.to_dict()


def test_evaluation_to_dict_contains_plain_serializable_values():
    payload = _evaluation().to_dict()

    assert payload["approach_name"] == "FLAME fitting"
    assert payload["vertex_count"] == 5023

    assert payload["semantic_regions"] == [
        "left_eye_socket",
        "lower_lip",
        "nose_tip",
        "right_eye_socket",
        "upper_lip",
    ]

    assert payload["supported_python_versions"] == [
        "3.10",
        "3.11",
    ]

    assert payload["metadata"] == {
        "evaluation_version": 1,
        "provider": "synthetic-fixture",
    }


@pytest.mark.parametrize(
    "field_name",
    [
        "approach_name",
        "model_name",
        "model_version",
        "license_type",
        "redistribution_conditions",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "   ",
        None,
    ],
)
def test_evaluation_rejects_invalid_required_text(
    field_name,
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _evaluation(
            **{
                field_name: invalid_value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "commercial_use_allowed",
        "supports_single_image",
        "supports_multi_view",
        "supports_surface_normals",
        "supports_uv_coordinates",
        "supports_landmark_vertex_map",
        "supports_identity_parameters",
        "supports_expression_parameters",
        "supports_pose_parameters",
        "supports_confidence",
        "supports_visibility",
        "supports_apple_silicon",
        "requires_cpu",
        "requires_gpu",
        "deterministic_output",
        "fixture_generation_supported",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        1,
        0,
        "true",
        None,
    ],
)
def test_evaluation_rejects_non_boolean_flags(
    field_name,
    invalid_value,
):
    with pytest.raises(
        TypeError,
        match=field_name,
    ):
        _evaluation(
            **{
                field_name: invalid_value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "vertex_count",
        "triangle_count",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        0,
        -1,
        1.5,
        True,
        "100",
        None,
    ],
)
def test_evaluation_rejects_invalid_mesh_counts(
    field_name,
    invalid_value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field_name,
    ):
        _evaluation(
            **{
                field_name: invalid_value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "runtime_seconds",
        "peak_memory_mb",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        -0.1,
        float("nan"),
        float("inf"),
        "invalid",
        None,
    ],
)
def test_evaluation_rejects_invalid_measurements(
    field_name,
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _evaluation(
            **{
                field_name: invalid_value,
            }
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "adaptive",
        "unknown",
        None,
    ],
)
def test_evaluation_rejects_invalid_topology_type(
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match="topology_type",
    ):
        _evaluation(
            topology_type=invalid_value,
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "atlas_adapter_feasibility",
        "maintenance_risk",
    ],
)
@pytest.mark.parametrize(
    "invalid_value",
    [
        "",
        "very_high",
        "unknown",
        None,
    ],
)
def test_evaluation_rejects_invalid_risk_level(
    field_name,
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _evaluation(
            **{
                field_name: invalid_value,
            }
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        (),
        ("",),
        ("nose_tip", ""),
        "nose_tip",
        None,
    ],
)
def test_evaluation_rejects_invalid_semantic_regions(
    invalid_value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="semantic_regions",
    ):
        _evaluation(
            semantic_regions=invalid_value,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        (),
        ("",),
        ("3.11", ""),
        "3.11",
        None,
    ],
)
def test_evaluation_rejects_invalid_python_versions(
    invalid_value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match="supported_python_versions",
    ):
        _evaluation(
            supported_python_versions=invalid_value,
        )


def test_evaluation_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _evaluation(
            metadata=[
                (
                    "provider",
                    "invalid",
                )
            ],
        )
