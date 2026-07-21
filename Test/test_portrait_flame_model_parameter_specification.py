from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from CORE.atlas_portrait_flame_model_parameter_specification import (
    AtlasPortraitFlameModelParameterSpecification,
)


def _specification(
    **overrides,
) -> AtlasPortraitFlameModelParameterSpecification:
    values = {
        "model_family": "flame",
        "model_version": "2023_open",
        "identity_parameter_count": 300,
        "expression_parameter_count": 100,
        "pose_parameter_count": 15,
        "metadata": {
            "parameter_layout": (
                "identity_expression_pose"
            ),
            "source": "flame_model_adapter",
            "synthetic": False,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitFlameModelParameterSpecification(
        **values,
    )


def test_specification_preserves_model_identity():
    specification = _specification()

    assert specification.model_family == "flame"
    assert specification.model_version == "2023_open"


def test_specification_preserves_parameter_counts():
    specification = _specification()

    assert specification.identity_parameter_count == 300
    assert specification.expression_parameter_count == 100
    assert specification.pose_parameter_count == 15


def test_specification_reports_total_parameter_count():
    specification = _specification()

    assert specification.total_parameter_count == 415


def test_specification_is_frozen():
    specification = _specification()

    with pytest.raises(
        FrozenInstanceError,
    ):
        specification.identity_parameter_count = 10


def test_specification_metadata_is_deterministic():
    specification = _specification()

    assert tuple(
        specification.metadata,
    ) == tuple(
        sorted(
            specification.metadata,
        )
    )

    assert specification.metadata == {
        "parameter_layout": (
            "identity_expression_pose"
        ),
        "source": "flame_model_adapter",
        "synthetic": False,
    }


def test_specification_serialization_is_deterministic():
    first = _specification()
    second = _specification()

    assert first.to_dict() == second.to_dict()


def test_specification_to_dict_contains_plain_values():
    specification = _specification()

    assert specification.to_dict() == {
        "model_family": "flame",
        "model_version": "2023_open",
        "identity_parameter_count": 300,
        "expression_parameter_count": 100,
        "pose_parameter_count": 15,
        "total_parameter_count": 415,
        "metadata": {
            "parameter_layout": (
                "identity_expression_pose"
            ),
            "source": "flame_model_adapter",
            "synthetic": False,
        },
    }


@pytest.mark.parametrize(
    "field_name",
    [
        "model_family",
        "model_version",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        None,
    ],
)
def test_specification_rejects_invalid_model_identity(
    field_name,
    value,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _specification(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "identity_parameter_count",
        "expression_parameter_count",
        "pose_parameter_count",
    ],
)
@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        1.5,
        True,
        None,
        "invalid",
    ],
)
def test_specification_rejects_invalid_parameter_counts(
    field_name,
    value,
):
    with pytest.raises(
        (
            TypeError,
            ValueError,
        ),
        match=field_name,
    ):
        _specification(
            **{
                field_name: value,
            }
        )


def test_specification_rejects_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _specification(
            metadata=[
                "invalid",
            ],
        )
