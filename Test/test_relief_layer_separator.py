import numpy as np
import pytest

from CORE.atlas_relief_layer_separator import (
    AtlasReliefLayerSeparator,
)


def test_separates_foreground_and_background_depth_ranges():
    depth = np.array(
        [
            [0.0, 0.5, 1.0],
            [0.0, 0.5, 1.0],
        ],
        dtype=np.float64,
    )

    subject_mask = np.array(
        [
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
        background_range=(0.0, 0.35),
        foreground_range=(0.55, 1.0),
    )

    separated = result["separated_depth"]

    assert separated.shape == depth.shape
    assert separated.dtype == np.float64

    assert separated[0, 0] == pytest.approx(0.0)
    assert separated[0, 1] == pytest.approx(0.175)
    assert separated[0, 2] == pytest.approx(1.0)
    assert separated[1, 1] == pytest.approx(0.775)


def test_soft_mask_blends_layer_depths():
    depth = np.array(
        [[0.5]],
        dtype=np.float64,
    )

    subject_mask = np.array(
        [[0.25]],
        dtype=np.float64,
    )

    result = AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
        background_range=(0.0, 0.4),
        foreground_range=(0.6, 1.0),
    )

    assert result["separated_depth"][0, 0] == (
        pytest.approx(0.35)
    )


def test_binary_mask_preserves_clear_layer_gap():
    depth = np.array(
        [
            [1.0, 0.0],
        ],
        dtype=np.float64,
    )

    subject_mask = np.array(
        [
            [0.0, 1.0],
        ],
        dtype=np.float64,
    )

    result = AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
        background_range=(0.0, 0.30),
        foreground_range=(0.60, 1.0),
    )

    separated = result["separated_depth"]

    assert separated[0, 0] == pytest.approx(0.30)
    assert separated[0, 1] == pytest.approx(0.60)


def test_result_records_effective_layer_settings():
    depth = np.zeros(
        (2, 2),
        dtype=np.float64,
    )
    subject_mask = np.zeros_like(depth)

    result = AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
        background_range=(0.05, 0.40),
        foreground_range=(0.65, 0.95),
    )

    assert result["type"] == (
        "relief_layer_separation"
    )
    assert result["background_range"] == (
        0.05,
        0.40,
    )
    assert result["foreground_range"] == (
        0.65,
        0.95,
    )


def test_does_not_mutate_inputs():
    depth = np.array(
        [
            [0.0, 0.5],
            [0.5, 1.0],
        ],
        dtype=np.float64,
    )
    subject_mask = np.array(
        [
            [0.0, 1.0],
            [0.25, 0.75],
        ],
        dtype=np.float64,
    )

    original_depth = depth.copy()
    original_mask = subject_mask.copy()

    AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
    )

    assert np.array_equal(
        depth,
        original_depth,
    )
    assert np.array_equal(
        subject_mask,
        original_mask,
    )


def test_layer_separation_is_deterministic():
    depth = np.arange(
        16,
        dtype=np.float64,
    ).reshape(4, 4) / 15.0

    subject_mask = np.linspace(
        0.0,
        1.0,
        16,
        dtype=np.float64,
    ).reshape(4, 4)

    first = AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
    )
    second = AtlasReliefLayerSeparator.separate(
        depth,
        subject_mask,
    )

    assert np.array_equal(
        first["separated_depth"],
        second["separated_depth"],
    )


@pytest.mark.parametrize(
    "depth,subject_mask",
    [
        (
            [[0.0, 1.0]],
            [[0.0], [1.0]],
        ),
        (
            [0.0, 1.0],
            [0.0, 1.0],
        ),
        (
            [[[0.0]]],
            [[[1.0]]],
        ),
        (
            [[0.0, float("nan")]],
            [[0.0, 1.0]],
        ),
        (
            [[0.0, 1.0]],
            [[0.0, float("inf")]],
        ),
        (
            [["invalid"]],
            [[0.0]],
        ),
    ],
)
def test_rejects_invalid_layer_arrays(
    depth,
    subject_mask,
):
    with pytest.raises(ValueError):
        AtlasReliefLayerSeparator.separate(
            depth,
            subject_mask,
        )


@pytest.mark.parametrize(
    "background_range,foreground_range",
    [
        ((-0.1, 0.4), (0.6, 1.0)),
        ((0.0, 1.1), (0.6, 1.0)),
        ((0.5, 0.5), (0.6, 1.0)),
        ((0.7, 0.4), (0.6, 1.0)),
        ((0.0, 0.4), (-0.1, 1.0)),
        ((0.0, 0.4), (0.6, 1.1)),
        ((0.0, 0.4), (0.8, 0.8)),
        ((0.0, 0.4), (0.9, 0.7)),
        ((0.0, 0.7), (0.6, 1.0)),
        ("invalid", (0.6, 1.0)),
        ((0.0, 0.4), None),
    ],
)
def test_rejects_invalid_layer_ranges(
    background_range,
    foreground_range,
):
    depth = np.zeros(
        (2, 2),
        dtype=np.float64,
    )
    subject_mask = np.zeros_like(depth)

    with pytest.raises(ValueError):
        AtlasReliefLayerSeparator.separate(
            depth,
            subject_mask,
            background_range=background_range,
            foreground_range=foreground_range,
        )


@pytest.mark.parametrize(
    "subject_mask",
    [
        [[-0.1, 0.0]],
        [[0.0, 1.1]],
    ],
)
def test_rejects_mask_values_outside_normalized_range(
    subject_mask,
):
    depth = np.zeros(
        (1, 2),
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        AtlasReliefLayerSeparator.separate(
            depth,
            subject_mask,
        )
