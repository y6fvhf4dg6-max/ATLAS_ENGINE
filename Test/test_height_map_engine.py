import numpy as np
import pytest

from CORE.atlas_height_map_engine import (
    AtlasHeightMapEngine,
)


def test_normalize_maps_values_to_unit_range():
    result = AtlasHeightMapEngine.normalize(
        [
            [10.0, 20.0],
            [30.0, 40.0],
        ]
    )

    assert result.dtype == np.float64
    assert result.min() == pytest.approx(0.0)
    assert result.max() == pytest.approx(1.0)
    assert result[0, 1] == pytest.approx(
        1.0 / 3.0
    )


def test_normalize_preserves_shape():
    result = AtlasHeightMapEngine.normalize(
        np.arange(12).reshape(3, 4)
    )

    assert result.shape == (3, 4)


def test_normalize_supports_inversion():
    normal = AtlasHeightMapEngine.normalize(
        [[0.0, 1.0]]
    )

    inverted = AtlasHeightMapEngine.normalize(
        [[0.0, 1.0]],
        invert=True,
    )

    assert inverted[0, 0] == pytest.approx(
        1.0
    )
    assert inverted[0, 1] == pytest.approx(
        0.0
    )
    assert np.allclose(
        inverted,
        1.0 - normal,
    )


def test_constant_input_returns_zero_map():
    result = AtlasHeightMapEngine.normalize(
        [
            [5.0, 5.0],
            [5.0, 5.0],
        ]
    )

    assert np.array_equal(
        result,
        np.zeros((2, 2)),
    )


@pytest.mark.parametrize(
    "values",
    [
        [],
        [1.0, 2.0, 3.0],
        np.zeros((2, 2, 2)),
    ],
)
def test_rejects_invalid_dimensions(values):
    with pytest.raises(ValueError):
        AtlasHeightMapEngine.normalize(values)


@pytest.mark.parametrize(
    "invalid_value",
    [
        np.nan,
        np.inf,
        -np.inf,
    ],
)
def test_rejects_non_finite_values(
    invalid_value,
):
    with pytest.raises(ValueError):
        AtlasHeightMapEngine.normalize(
            [
                [0.0, invalid_value],
                [1.0, 2.0],
            ]
        )


def test_output_is_deterministic():
    values = np.array(
        [
            [7.0, 2.0, 9.0],
            [4.0, 8.0, 1.0],
        ]
    )

    first = AtlasHeightMapEngine.normalize(
        values
    )
    second = AtlasHeightMapEngine.normalize(
        values
    )

    assert np.array_equal(first, second)
