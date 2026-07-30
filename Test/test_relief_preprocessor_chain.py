import numpy as np
import pytest

from CORE.atlas_relief_preprocessor_chain import (
    AtlasReliefPreprocessorChain,
)


def test_preprocessor_chain_applies_steps_in_order():
    source = np.array(
        [
            [0.10, 0.20],
            [0.30, 0.40],
        ],
        dtype=np.float64,
    )

    def add_offset(values):
        return values + 0.10

    def multiply(values):
        return values * 2.0

    result = AtlasReliefPreprocessorChain.apply(
        source,
        preprocessors=(
            add_offset,
            multiply,
        ),
    )

    expected = np.array(
        [
            [0.40, 0.60],
            [0.80, 1.00],
        ],
        dtype=np.float64,
    )

    assert result.dtype == np.float64
    assert np.allclose(result, expected)


def test_preprocessor_chain_returns_copy_without_steps():
    source = np.array(
        [
            [0.10, 0.20],
            [0.30, 0.40],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefPreprocessorChain.apply(
        source,
        preprocessors=(),
    )

    assert np.array_equal(result, source)
    assert result is not source


def test_preprocessor_chain_rejects_shape_change():
    source = np.ones(
        (4, 6),
        dtype=np.float64,
    )

    def invalid_step(values):
        return values[:, :-1]

    with pytest.raises(
        ValueError,
        match="preserve image shape",
    ):
        AtlasReliefPreprocessorChain.apply(
            source,
            preprocessors=(invalid_step,),
        )


def test_preprocessor_chain_rejects_non_finite_output():
    source = np.ones(
        (4, 6),
        dtype=np.float64,
    )

    def invalid_step(values):
        result = values.copy()
        result[0, 0] = np.nan
        return result

    with pytest.raises(
        ValueError,
        match="finite",
    ):
        AtlasReliefPreprocessorChain.apply(
            source,
            preprocessors=(invalid_step,),
        )
