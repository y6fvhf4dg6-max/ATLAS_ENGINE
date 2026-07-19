import numpy as np
import pytest

from CORE.atlas_relief_multiscale_decomposer import (
    AtlasReliefMultiscaleDecomposer,
)


def test_decomposer_separates_three_frequency_bands():
    values = np.zeros(
        (9, 9),
        dtype=np.float64,
    )
    values[4, 4] = 1.0

    result = AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=2.0,
        detail_sigma=0.8,
    )

    assert result["form"].shape == values.shape
    assert result["detail"].shape == values.shape
    assert result["micro_detail"].shape == values.shape


def test_frequency_bands_reconstruct_original_input():
    values = np.array(
        [
            [0.0, 0.1, 0.2, 0.3],
            [0.2, 0.4, 0.6, 0.8],
            [0.3, 0.5, 0.7, 0.9],
            [0.4, 0.6, 0.8, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=1.5,
        detail_sigma=0.6,
    )

    reconstructed = (
        result["form"]
        + result["detail"]
        + result["micro_detail"]
    )

    assert np.allclose(
        reconstructed,
        values,
        atol=1e-12,
    )


def test_constant_input_has_no_detail_bands():
    values = np.full(
        (7, 7),
        0.4,
        dtype=np.float64,
    )

    result = AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=2.0,
        detail_sigma=0.8,
    )

    assert np.allclose(
        result["form"],
        values,
    )
    assert np.allclose(
        result["detail"],
        0.0,
        atol=1e-12,
    )
    assert np.allclose(
        result["micro_detail"],
        0.0,
        atol=1e-12,
    )


def test_form_band_is_smoother_than_original():
    values = np.zeros(
        (11, 11),
        dtype=np.float64,
    )
    values[5, 5] = 1.0

    result = AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=2.0,
        detail_sigma=0.8,
    )

    assert result["form"][5, 5] < 1.0
    assert result["form"][5, 5] > 0.0


def test_detail_sigma_must_be_lower_than_form_sigma():
    values = np.zeros(
        (5, 5),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match=(
            "detail_sigma must be lower than "
            "form_sigma"
        ),
    ):
        AtlasReliefMultiscaleDecomposer.decompose(
            values,
            form_sigma=1.0,
            detail_sigma=1.0,
        )


@pytest.mark.parametrize(
    "form_sigma,detail_sigma",
    [
        (0.0, 0.5),
        (-1.0, 0.5),
        (2.0, 0.0),
        (2.0, -0.5),
        (float("nan"), 0.5),
        (2.0, float("inf")),
        ("invalid", 0.5),
        (2.0, None),
    ],
)
def test_rejects_invalid_sigma_values(
    form_sigma,
    detail_sigma,
):
    values = np.zeros(
        (5, 5),
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        AtlasReliefMultiscaleDecomposer.decompose(
            values,
            form_sigma=form_sigma,
            detail_sigma=detail_sigma,
        )


def test_decomposition_is_deterministic():
    values = np.arange(
        64,
        dtype=np.float64,
    ).reshape(8, 8)

    first = AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=2.0,
        detail_sigma=0.7,
    )
    second = AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=2.0,
        detail_sigma=0.7,
    )

    for key in (
        "form",
        "detail",
        "micro_detail",
    ):
        assert np.array_equal(
            first[key],
            second[key],
        )


def test_decomposition_does_not_mutate_input():
    values = np.arange(
        36,
        dtype=np.float64,
    ).reshape(6, 6)
    original = values.copy()

    AtlasReliefMultiscaleDecomposer.decompose(
        values,
        form_sigma=1.5,
        detail_sigma=0.6,
    )

    assert np.array_equal(
        values,
        original,
    )
