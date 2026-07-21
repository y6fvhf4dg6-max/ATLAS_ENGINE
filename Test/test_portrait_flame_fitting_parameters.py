from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)


def _identity_parameters() -> np.ndarray:
    return np.array(
        [
            0.10,
            -0.05,
            0.025,
            0.0,
        ],
        dtype=np.float64,
    )


def _expression_parameters() -> np.ndarray:
    return np.array(
        [
            0.02,
            -0.01,
            0.0,
        ],
        dtype=np.float64,
    )


def _pose_parameters() -> np.ndarray:
    return np.array(
        [
            0.0,
            0.015,
        ],
        dtype=np.float64,
    )


def _parameters(
    **overrides,
) -> AtlasPortraitFlameFittingParameters:
    values = {
        "identity_parameters": _identity_parameters(),
        "expression_parameters": (
            _expression_parameters()
        ),
        "pose_parameters": _pose_parameters(),
        "metadata": {
            "fitting_stage": "initial",
            "model_family": "flame",
            "model_version": "2023_open",
            "synthetic": True,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitFlameFittingParameters(
        **values,
    )


def test_parameters_preserve_identity_vector():
    parameters = _parameters()

    assert parameters.identity_parameters.shape == (
        4,
    )
    assert parameters.identity_parameters.dtype == (
        np.float64
    )

    assert np.array_equal(
        parameters.identity_parameters,
        _identity_parameters(),
    )


def test_parameters_preserve_expression_vector():
    parameters = _parameters()

    assert parameters.expression_parameters.shape == (
        3,
    )
    assert parameters.expression_parameters.dtype == (
        np.float64
    )

    assert np.array_equal(
        parameters.expression_parameters,
        _expression_parameters(),
    )


def test_parameters_preserve_pose_vector():
    parameters = _parameters()

    assert parameters.pose_parameters.shape == (
        2,
    )
    assert parameters.pose_parameters.dtype == (
        np.float64
    )

    assert np.array_equal(
        parameters.pose_parameters,
        _pose_parameters(),
    )


def test_parameters_report_vector_counts():
    parameters = _parameters()

    assert parameters.identity_parameter_count == 4
    assert parameters.expression_parameter_count == 3
    assert parameters.pose_parameter_count == 2


def test_parameters_are_frozen():
    parameters = _parameters()

    with pytest.raises(
        FrozenInstanceError,
    ):
        parameters.identity_parameters = np.zeros(
            4,
            dtype=np.float64,
        )


def test_parameter_vectors_are_read_only():
    parameters = _parameters()

    for vector in (
        parameters.identity_parameters,
        parameters.expression_parameters,
        parameters.pose_parameters,
    ):
        assert vector.flags.writeable is False

        with pytest.raises(
            ValueError,
        ):
            vector[
                0
            ] = 99.0


def test_parameter_vectors_are_copied():
    identity = _identity_parameters()
    expression = _expression_parameters()
    pose = _pose_parameters()

    parameters = _parameters(
        identity_parameters=identity,
        expression_parameters=expression,
        pose_parameters=pose,
    )

    identity[
        0
    ] = 99.0

    expression[
        0
    ] = 99.0

    pose[
        0
    ] = 99.0

    assert parameters.identity_parameters[
        0
    ] != 99.0

    assert parameters.expression_parameters[
        0
    ] != 99.0

    assert parameters.pose_parameters[
        0
    ] != 99.0


def test_metadata_is_deterministic():
    parameters = _parameters()

    assert tuple(
        parameters.metadata,
    ) == tuple(
        sorted(
            parameters.metadata,
        )
    )

    assert parameters.metadata == {
        "fitting_stage": "initial",
        "model_family": "flame",
        "model_version": "2023_open",
        "synthetic": True,
    }


def test_serialization_is_deterministic():
    first = _parameters()
    second = _parameters()

    assert first.to_dict() == second.to_dict()


def test_to_dict_contains_plain_values():
    parameters = _parameters()

    assert parameters.to_dict() == {
        "identity_parameter_count": 4,
        "expression_parameter_count": 3,
        "pose_parameter_count": 2,
        "identity_parameters": (
            _identity_parameters().tolist()
        ),
        "expression_parameters": (
            _expression_parameters().tolist()
        ),
        "pose_parameters": (
            _pose_parameters().tolist()
        ),
        "metadata": {
            "fitting_stage": "initial",
            "model_family": "flame",
            "model_version": "2023_open",
            "synthetic": True,
        },
    }


@pytest.mark.parametrize(
    "field_name",
    [
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
    ],
)
def test_parameters_reject_multidimensional_vectors(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _parameters(
            **{
                field_name: np.zeros(
                    (
                        2,
                        2,
                    ),
                    dtype=np.float64,
                ),
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
    ],
)
def test_parameters_reject_empty_vectors(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _parameters(
            **{
                field_name: np.zeros(
                    0,
                    dtype=np.float64,
                ),
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
    ],
)
def test_parameters_reject_non_finite_vectors(
    field_name,
):
    value = np.array(
        [
            0.0,
            np.nan,
        ],
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _parameters(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "identity_parameters",
        "expression_parameters",
        "pose_parameters",
    ],
)
def test_parameters_reject_non_numeric_vectors(
    field_name,
):
    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _parameters(
            **{
                field_name: [
                    "invalid",
                ],
            }
        )


def test_parameters_reject_non_mapping_metadata():
    with pytest.raises(
        TypeError,
        match="metadata",
    ):
        _parameters(
            metadata=[
                "invalid",
            ],
        )
