import numpy as np
import pytest

from CORE.atlas_portrait_contact_plane_global_gamma_compressor import (
    AtlasPortraitContactPlaneGlobalGammaCompressor,
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
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    assert result["compressed_height"].dtype == np.float64
    assert result["compressed_height"].shape == (2, 3)


def test_compressor_applies_global_gamma_shaping():
    result = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    source_height = np.array(
        [
            [0.0, 0.4, 0.0],
            [0.1, 0.8, 0.1],
        ],
        dtype=np.float64,
    )

    expected = (
        np.power(
            source_height / 0.8,
            0.6,
        )
        * 0.2
    )

    assert result["compressed_height"] == pytest.approx(
        expected,
        abs=1.0e-15,
    )


def test_contact_point_becomes_target_maximum_height():
    projection = _projection_result()

    result = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    assert result["compressed_height"][
        projection.contact_index
    ] == pytest.approx(
        0.2,
    )


def test_farthest_points_remain_zero():
    result = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    assert result["compressed_height"][0, 0] == pytest.approx(
        0.0,
    )
    assert result["compressed_height"][0, 2] == pytest.approx(
        0.0,
    )


def test_gamma_below_one_raises_mid_height():
    projection = _projection_result()

    nonlinear = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    linear_mid_height = 0.1

    assert nonlinear["compressed_height"][0, 1] > (
        linear_mid_height
    )


def test_compressor_records_contract_metadata():
    result = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    assert result["type"] == (
        "portrait_contact_plane_global_gamma_compression"
    )
    assert result["compression_mode"] == (
        "global_gamma_target_maximum_height"
    )
    assert result["source_shape"] == (2, 3)
    assert result["source_maximum_height"] == pytest.approx(
        0.8,
    )
    assert result["target_maximum_height"] == pytest.approx(
        0.2,
    )
    assert result["gamma"] == pytest.approx(
        0.6,
    )
    assert result["lower_percentile"] == pytest.approx(
        0.0,
    )
    assert result["upper_percentile"] == pytest.approx(
        100.0,
    )


def test_default_gamma_is_calibrated_baseline():
    result = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            _projection_result(),
            target_maximum_height=0.2,
        )
    )

    assert result["gamma"] == pytest.approx(
        0.6,
    )


def test_compressor_does_not_modify_projection():
    projection = _projection_result()
    original = projection.distance_to_plane.copy()

    AtlasPortraitContactPlaneGlobalGammaCompressor.compress(
        projection,
        target_maximum_height=0.2,
        gamma=0.6,
    )

    assert projection.distance_to_plane == pytest.approx(
        original,
    )


def test_compressor_is_deterministic():
    projection = _projection_result()

    first = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )
    second = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
            gamma=0.6,
        )
    )

    assert first["compressed_height"] == pytest.approx(
        second["compressed_height"],
        abs=0.0,
    )


def test_zero_depth_range_produces_zero_height():
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
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            projection,
            target_maximum_height=0.2,
            gamma=0.6,
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
            AtlasPortraitContactPlaneGlobalGammaCompressor
            .compress(
                _projection_result(),
                target_maximum_height=invalid_value,
                gamma=0.6,
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
            AtlasPortraitContactPlaneGlobalGammaCompressor
            .compress(
                _projection_result(),
                target_maximum_height=0.2,
                gamma=invalid_value,
            )
        )


def test_compressor_rejects_wrong_projection_type():
    with pytest.raises(
        TypeError,
        match="projection",
    ):
        (
            AtlasPortraitContactPlaneGlobalGammaCompressor
            .compress(
                object(),
                target_maximum_height=0.2,
                gamma=0.6,
            )
        )
