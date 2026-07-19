import numpy as np
import pytest

from CORE.atlas_relief_mask_processor import (
    AtlasReliefMaskProcessor,
)


def test_mask_processor_returns_contract():
    mask = np.array(
        [
            [0.0, 0.5],
            [0.75, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskProcessor.process(mask)

    assert result["type"] == (
        "relief_mask_processing_result"
    )
    assert result["processed_mask"].shape == (2, 2)
    assert result["processed_mask"].dtype == np.float64
    assert result["threshold"] is None
    assert result["feather_sigma"] == pytest.approx(0.0)


def test_mask_processor_clamps_values_to_unit_range():
    mask = np.array(
        [
            [-0.5, 0.25],
            [1.25, 2.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskProcessor.process(mask)

    np.testing.assert_allclose(
        result["processed_mask"],
        np.array(
            [
                [0.0, 0.25],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
    )


def test_mask_processor_applies_threshold():
    mask = np.array(
        [
            [0.10, 0.49],
            [0.50, 0.90],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskProcessor.process(
        mask,
        threshold=0.50,
    )

    np.testing.assert_allclose(
        result["processed_mask"],
        np.array(
            [
                [0.0, 0.0],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
    )
    assert result["threshold"] == pytest.approx(0.50)


def test_mask_processor_feathers_hard_edge():
    mask = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    mask[2, 2] = 1.0

    result = AtlasReliefMaskProcessor.process(
        mask,
        feather_sigma=1.0,
    )

    processed = result["processed_mask"]

    assert processed[2, 2] < 1.0
    assert processed[2, 2] > processed[0, 0]
    assert processed[2, 1] > 0.0
    assert processed.min() >= 0.0
    assert processed.max() <= 1.0
    assert result["feather_sigma"] == pytest.approx(1.0)


def test_mask_processor_applies_threshold_before_feather():
    mask = np.array(
        [
            [0.0, 0.0, 0.0],
            [0.0, 0.6, 0.0],
            [0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskProcessor.process(
        mask,
        threshold=0.5,
        feather_sigma=0.8,
    )

    processed = result["processed_mask"]

    assert processed[1, 1] > processed[0, 0]
    assert processed[1, 0] > 0.0
    assert processed.max() <= 1.0


def test_mask_processor_does_not_modify_input():
    mask = np.array(
        [
            [-1.0, 0.4],
            [0.8, 2.0],
        ],
        dtype=np.float64,
    )
    original = mask.copy()

    AtlasReliefMaskProcessor.process(
        mask,
        threshold=0.5,
    )

    np.testing.assert_array_equal(
        mask,
        original,
    )


@pytest.mark.parametrize(
    "invalid_mask",
    [
        np.array([0.0, 1.0]),
        np.zeros((2, 2, 1)),
        np.array(
            [
                [0.0, np.nan],
                [0.5, 1.0],
            ]
        ),
        np.array(
            [
                [0.0, np.inf],
                [0.5, 1.0],
            ]
        ),
    ],
)
def test_mask_processor_rejects_invalid_masks(
    invalid_mask,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskProcessor.process(
            invalid_mask
        )


@pytest.mark.parametrize(
    "invalid_threshold",
    [
        -0.01,
        1.01,
        np.nan,
        np.inf,
    ],
)
def test_mask_processor_rejects_invalid_threshold(
    invalid_threshold,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskProcessor.process(
            np.ones((2, 2)),
            threshold=invalid_threshold,
        )


@pytest.mark.parametrize(
    "invalid_sigma",
    [
        -0.01,
        np.nan,
        np.inf,
    ],
)
def test_mask_processor_rejects_invalid_feather_sigma(
    invalid_sigma,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskProcessor.process(
            np.ones((2, 2)),
            feather_sigma=invalid_sigma,
        )
