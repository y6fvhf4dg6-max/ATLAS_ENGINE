from __future__ import annotations

import numpy as np
import pytest

from CORE.atlas_portrait_flame_fitting_parameter_initializer import (
    AtlasPortraitFlameFittingParameterInitializer,
)
from CORE.atlas_portrait_flame_fitting_parameters import (
    AtlasPortraitFlameFittingParameters,
)
from CORE.atlas_portrait_flame_model_parameter_specification import (
    AtlasPortraitFlameModelParameterSpecification,
)


def _specification(
    **overrides,
) -> AtlasPortraitFlameModelParameterSpecification:
    values = {
        "model_family": "flame",
        "model_version": "2023_open",
        "identity_parameter_count": 4,
        "expression_parameter_count": 3,
        "pose_parameter_count": 2,
        "metadata": {
            "parameter_layout": (
                "identity_expression_pose"
            ),
            "source": "synthetic_test",
            "synthetic": True,
        },
    }

    values.update(
        overrides,
    )

    return AtlasPortraitFlameModelParameterSpecification(
        **values,
    )


def test_initializer_returns_fitting_parameters():
    parameters = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            _specification(),
        )
    )

    assert isinstance(
        parameters,
        AtlasPortraitFlameFittingParameters,
    )


def test_initializer_creates_zero_identity_parameters():
    parameters = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            _specification(),
        )
    )

    assert np.array_equal(
        parameters.identity_parameters,
        np.zeros(
            4,
            dtype=np.float64,
        ),
    )


def test_initializer_creates_zero_expression_parameters():
    parameters = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            _specification(),
        )
    )

    assert np.array_equal(
        parameters.expression_parameters,
        np.zeros(
            3,
            dtype=np.float64,
        ),
    )


def test_initializer_creates_zero_pose_parameters():
    parameters = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            _specification(),
        )
    )

    assert np.array_equal(
        parameters.pose_parameters,
        np.zeros(
            2,
            dtype=np.float64,
        ),
    )


def test_initializer_uses_specification_counts():
    parameters = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            _specification(
                identity_parameter_count=6,
                expression_parameter_count=5,
                pose_parameter_count=4,
            ),
        )
    )

    assert parameters.identity_parameter_count == 6
    assert parameters.expression_parameter_count == 5
    assert parameters.pose_parameter_count == 4


def test_initializer_metadata_is_deterministic():
    parameters = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            _specification(),
        )
    )

    assert parameters.metadata == {
        "fitting_stage": "neutral_initialization",
        "initialization_method": "zero_parameters",
        "model_family": "flame",
        "model_version": "2023_open",
        "synthetic": True,
    }


def test_initializer_is_deterministic():
    specification = _specification()

    first = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            specification,
        )
    )

    second = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            specification,
        )
    )

    assert first.to_dict() == second.to_dict()
    assert first is not second


def test_initializer_returns_independent_vectors():
    specification = _specification()

    first = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            specification,
        )
    )

    second = (
        AtlasPortraitFlameFittingParameterInitializer
        .initialize(
            specification,
        )
    )

    assert not np.shares_memory(
        first.identity_parameters,
        second.identity_parameters,
    )

    assert not np.shares_memory(
        first.expression_parameters,
        second.expression_parameters,
    )

    assert not np.shares_memory(
        first.pose_parameters,
        second.pose_parameters,
    )


def test_initializer_does_not_modify_specification():
    specification = _specification()

    before = specification.to_dict()

    AtlasPortraitFlameFittingParameterInitializer.initialize(
        specification,
    )

    assert specification.to_dict() == before


def test_initializer_rejects_wrong_specification_type():
    with pytest.raises(
        TypeError,
        match=(
            "AtlasPortraitFlameModelParameterSpecification"
        ),
    ):
        AtlasPortraitFlameFittingParameterInitializer.initialize(
            object(),
        )
