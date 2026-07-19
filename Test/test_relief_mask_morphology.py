import numpy as np
import pytest

from CORE.atlas_relief_mask_morphology import (
    AtlasReliefMaskMorphology,
)


def test_mask_morphology_returns_contract():
    mask = np.array(
        [
            [0.0, 1.0],
            [1.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="dilate",
        radius=1,
    )

    assert result["type"] == (
        "relief_mask_morphology_result"
    )
    assert result["operation"] == "dilate"
    assert result["radius"] == 1
    assert result["processed_mask"].shape == (2, 2)
    assert result["processed_mask"].dtype == np.float64


def test_mask_morphology_dilates_single_pixel():
    mask = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    mask[2, 2] = 1.0

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="dilate",
        radius=1,
    )

    expected = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    expected[1:4, 1:4] = 1.0

    np.testing.assert_array_equal(
        result["processed_mask"],
        expected,
    )


def test_mask_morphology_erodes_square():
    mask = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    mask[1:4, 1:4] = 1.0

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="erode",
        radius=1,
    )

    expected = np.zeros(
        (5, 5),
        dtype=np.float64,
    )
    expected[2, 2] = 1.0

    np.testing.assert_array_equal(
        result["processed_mask"],
        expected,
    )


def test_mask_morphology_open_removes_isolated_pixel():
    mask = np.zeros(
        (7, 7),
        dtype=np.float64,
    )
    mask[2:5, 2:5] = 1.0
    mask[0, 0] = 1.0

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="open",
        radius=1,
    )

    assert result["processed_mask"][0, 0] == 0.0
    assert result["processed_mask"][3, 3] == 1.0


def test_mask_morphology_close_fills_single_pixel_hole():
    mask = np.ones(
        (5, 5),
        dtype=np.float64,
    )
    mask[2, 2] = 0.0

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="close",
        radius=1,
    )

    assert result["processed_mask"][2, 2] == 1.0


def test_mask_morphology_radius_zero_is_identity():
    mask = np.array(
        [
            [0.0, 1.0],
            [1.0, 0.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="close",
        radius=0,
    )

    np.testing.assert_array_equal(
        result["processed_mask"],
        mask,
    )


def test_mask_morphology_does_not_modify_input():
    mask = np.zeros(
        (3, 3),
        dtype=np.float64,
    )
    mask[1, 1] = 1.0
    original = mask.copy()

    AtlasReliefMaskMorphology.apply(
        mask,
        operation="dilate",
        radius=1,
    )

    np.testing.assert_array_equal(
        mask,
        original,
    )


def test_mask_morphology_thresholds_soft_mask():
    mask = np.array(
        [
            [0.49, 0.50],
            [0.75, 0.10],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefMaskMorphology.apply(
        mask,
        operation="dilate",
        radius=0,
        threshold=0.50,
    )

    np.testing.assert_array_equal(
        result["processed_mask"],
        np.array(
            [
                [0.0, 1.0],
                [1.0, 0.0],
            ],
            dtype=np.float64,
        ),
    )


@pytest.mark.parametrize(
    "operation",
    [
        "dilate",
        "erode",
        "open",
        "close",
    ],
)
def test_mask_morphology_accepts_supported_operations(
    operation,
):
    result = AtlasReliefMaskMorphology.apply(
        np.ones((2, 2)),
        operation=operation,
        radius=0,
    )

    assert result["operation"] == operation


@pytest.mark.parametrize(
    "invalid_operation",
    [
        "",
        "blur",
        "expand",
        None,
    ],
)
def test_mask_morphology_rejects_invalid_operation(
    invalid_operation,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskMorphology.apply(
            np.ones((2, 2)),
            operation=invalid_operation,
            radius=1,
        )


@pytest.mark.parametrize(
    "invalid_radius",
    [
        -1,
        0.5,
        np.nan,
        np.inf,
    ],
)
def test_mask_morphology_rejects_invalid_radius(
    invalid_radius,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskMorphology.apply(
            np.ones((2, 2)),
            operation="dilate",
            radius=invalid_radius,
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
def test_mask_morphology_rejects_invalid_threshold(
    invalid_threshold,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskMorphology.apply(
            np.ones((2, 2)),
            operation="dilate",
            radius=1,
            threshold=invalid_threshold,
        )


@pytest.mark.parametrize(
    "invalid_mask",
    [
        np.array([0.0, 1.0]),
        np.zeros((2, 2, 1)),
        np.array(
            [
                [0.0, np.nan],
                [1.0, 0.0],
            ]
        ),
        np.array(
            [
                [0.0, np.inf],
                [1.0, 0.0],
            ]
        ),
        np.array(
            [
                [-0.1, 0.0],
                [1.0, 0.5],
            ]
        ),
        np.array(
            [
                [0.0, 1.1],
                [1.0, 0.5],
            ]
        ),
    ],
)
def test_mask_morphology_rejects_invalid_masks(
    invalid_mask,
):
    with pytest.raises(ValueError):
        AtlasReliefMaskMorphology.apply(
            invalid_mask,
            operation="dilate",
            radius=1,
        )
