import numpy as np
import pytest

from CORE.atlas_portrait_contact_plane_gradient_limited_compressor import (
    AtlasPortraitContactPlaneGradientLimitedCompressor,
)
from CORE.atlas_portrait_contact_plane_projection_result import (
    AtlasPortraitContactPlaneProjectionResult,
)


def _projection_result():
    return AtlasPortraitContactPlaneProjectionResult(
        distance_to_plane=np.array(
            [
                [0.8, 0.4, 0.8],
                [0.7, 0.0, 0.7],
            ],
            dtype=np.float64,
        ),
        contact_plane_z=0.8,
        contact_row=1,
        contact_column=1,
        maximum_distance=0.8,
        source_shape=(2, 3),
        metadata={
            "projection_mode": "frontal_contact_plane",
        },
    )


def test_compressor_returns_float64_height_grid():
    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
            gamma=0.6,
            gradient_percentile=70.0,
            blend_strength=0.6,
        )
    )

    assert result["compressed_height"].dtype == np.float64
    assert result["compressed_height"].shape == (2, 3)


def test_compressor_blends_gamma_and_linear_heights():
    projection = _projection_result()

    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
            gamma=0.6,
            gradient_percentile=70.0,
            blend_strength=0.6,
        )
    )

    source_height = (
        projection.maximum_distance
        - projection.distance_to_plane
    )

    normalized = source_height / projection.maximum_distance

    linear_height = normalized * 0.2
    gamma_height = np.power(
        normalized,
        0.6,
    ) * 0.2

    row_gradient, column_gradient = np.gradient(
        gamma_height,
    )

    gradient_magnitude = np.hypot(
        row_gradient,
        column_gradient,
    )

    threshold = float(
        np.percentile(
            gradient_magnitude,
            70.0,
        )
    )

    maximum_gradient = float(
        gradient_magnitude.max()
    )

    if maximum_gradient <= threshold:
        base_weight = np.zeros_like(
            gradient_magnitude,
            dtype=np.float64,
        )
    else:
        base_weight = np.clip(
            (
                gradient_magnitude
                - threshold
            )
            / (
                maximum_gradient
                - threshold
            ),
            0.0,
            1.0,
        )

    weight = np.clip(
        base_weight * 0.6,
        0.0,
        1.0,
    )

    expected = (
        gamma_height * (1.0 - weight)
        + linear_height * weight
    )

    assert result["compressed_height"] == pytest.approx(
        expected,
        abs=1.0e-15,
    )


def test_contact_point_remains_target_maximum():
    projection = _projection_result()

    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
        )
    )

    height = result["compressed_height"]

    assert height[
        projection.contact_index
    ] == pytest.approx(
        0.2,
    )
    assert float(
        height.max()
    ) == pytest.approx(
        0.2,
    )


def test_farthest_points_remain_zero():
    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
        )
    )

    assert result["compressed_height"][0, 0] == pytest.approx(
        0.0,
    )
    assert result["compressed_height"][0, 2] == pytest.approx(
        0.0,
    )


def test_output_stays_between_linear_and_gamma_surfaces():
    projection = _projection_result()

    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
        )
    )

    source_height = (
        projection.maximum_distance
        - projection.distance_to_plane
    )

    normalized = source_height / projection.maximum_distance

    linear_height = normalized * 0.2
    gamma_height = np.power(
        normalized,
        0.6,
    ) * 0.2

    lower = np.minimum(
        linear_height,
        gamma_height,
    )
    upper = np.maximum(
        linear_height,
        gamma_height,
    )

    assert np.all(
        result["compressed_height"]
        >= lower - 1.0e-15
    )
    assert np.all(
        result["compressed_height"]
        <= upper + 1.0e-15
    )


def test_compressor_records_calibrated_defaults():
    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
        )
    )

    assert result["type"] == (
        "portrait_contact_plane_gradient_limited_compression"
    )
    assert result["compression_mode"] == (
        "global_gamma_gradient_limited_linear_blend"
    )
    assert result["gamma"] == pytest.approx(
        0.6,
    )
    assert result["gradient_percentile"] == pytest.approx(
        70.0,
    )
    assert result["blend_strength"] == pytest.approx(
        0.6,
    )


def test_compressor_reports_weight_grid_metrics():
    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
        )
    )

    weight = result["gradient_weight"]

    assert weight.dtype == np.float64
    assert weight.shape == (2, 3)
    assert float(
        weight.min()
    ) >= 0.0
    assert float(
        weight.max()
    ) <= 0.6 + 1.0e-15
    assert result[
        "gradient_threshold"
    ] >= 0.0
    assert result[
        "maximum_gradient"
    ] >= result[
        "gradient_threshold"
    ]


def test_compressor_does_not_modify_projection():
    projection = _projection_result()
    original = projection.distance_to_plane.copy()

    AtlasPortraitContactPlaneGradientLimitedCompressor.compress(
        projection,
        target_maximum_height=0.2,
    )

    assert projection.distance_to_plane == pytest.approx(
        original,
    )


def test_compressor_is_deterministic():
    projection = _projection_result()

    first = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
        )
    )
    second = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
        )
    )

    assert first["compressed_height"] == pytest.approx(
        second["compressed_height"],
        abs=0.0,
    )
    assert first["gradient_weight"] == pytest.approx(
        second["gradient_weight"],
        abs=0.0,
    )


def test_zero_depth_range_produces_zero_height_and_weight():
    projection = AtlasPortraitContactPlaneProjectionResult(
        distance_to_plane=np.zeros(
            (
                2,
                2,
            ),
            dtype=np.float64,
        ),
        contact_plane_z=0.5,
        contact_row=0,
        contact_column=0,
        maximum_distance=0.0,
        source_shape=(2, 2),
        metadata={
            "projection_mode": "frontal_contact_plane",
        },
    )

    result = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
        )
    )

    assert result["compressed_height"] == pytest.approx(
        np.zeros(
            (
                2,
                2,
            ),
            dtype=np.float64,
        )
    )
    assert result["gradient_weight"] == pytest.approx(
        np.zeros(
            (
                2,
                2,
            ),
            dtype=np.float64,
        )
    )


@pytest.mark.parametrize(
    "invalid_value",
    [
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
        "invalid",
        None,
    ],
)
def test_compressor_rejects_invalid_target_height(
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match="target_maximum_height",
    ):
        (
            AtlasPortraitContactPlaneGradientLimitedCompressor
            .compress(
                _projection_result(),
                target_maximum_height=invalid_value,
            )
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
        "invalid",
        None,
    ],
)
def test_compressor_rejects_invalid_gamma(
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match="gamma",
    ):
        (
            AtlasPortraitContactPlaneGradientLimitedCompressor
            .compress(
                _projection_result(),
                target_maximum_height=0.2,
                gamma=invalid_value,
            )
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        -0.1,
        100.1,
        float("nan"),
        float("inf"),
        "invalid",
        None,
    ],
)
def test_compressor_rejects_invalid_gradient_percentile(
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match="gradient_percentile",
    ):
        (
            AtlasPortraitContactPlaneGradientLimitedCompressor
            .compress(
                _projection_result(),
                target_maximum_height=0.2,
                gradient_percentile=invalid_value,
            )
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        -0.1,
        1.1,
        float("nan"),
        float("inf"),
        "invalid",
        None,
    ],
)
def test_compressor_rejects_invalid_blend_strength(
    invalid_value,
):
    with pytest.raises(
        ValueError,
        match="blend_strength",
    ):
        (
            AtlasPortraitContactPlaneGradientLimitedCompressor
            .compress(
                _projection_result(),
                target_maximum_height=0.2,
                blend_strength=invalid_value,
            )
        )


def test_compressor_rejects_wrong_projection_type():
    with pytest.raises(
        TypeError,
        match="projection",
    ):
        (
            AtlasPortraitContactPlaneGradientLimitedCompressor
            .compress(
                object(),
                target_maximum_height=0.2,
            )
        )
