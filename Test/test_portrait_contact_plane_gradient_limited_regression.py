from __future__ import annotations

import hashlib

import numpy as np
import pytest

from CORE.atlas_neutral_parametric_face_surface_builder import (
    AtlasNeutralParametricFaceSurfaceBuilder,
)
from CORE.atlas_parametric_face_depth_deformer import (
    AtlasParametricFaceDepthDeformer,
)
from CORE.atlas_parametric_face_depth_profile import (
    AtlasParametricFaceDepthProfile,
)
from CORE.atlas_portrait_contact_plane_compression_evaluator import (
    AtlasPortraitContactPlaneCompressionEvaluator,
)
from CORE.atlas_portrait_contact_plane_global_gamma_compressor import (
    AtlasPortraitContactPlaneGlobalGammaCompressor,
)
from CORE.atlas_portrait_contact_plane_gradient_limited_compressor import (
    AtlasPortraitContactPlaneGradientLimitedCompressor,
)
from CORE.atlas_portrait_contact_plane_projector import (
    AtlasPortraitContactPlaneProjector,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    AMBIENT_STRENGTH,
    DIFFUSE_STRENGTH,
    GRID_SIZE,
    LIGHT_DIRECTION,
)


TARGET_MAXIMUM_HEIGHT = 0.20

EXPECTED_SHAPE = (
    401,
    401,
)

EXPECTED_CONTACT_INDEX = (
    180,
    199,
)

EXPECTED_MAXIMUM_POSITIONS = (
    (
        180,
        199,
    ),
    (
        180,
        201,
    ),
)

EXPECTED_SOURCE_MAXIMUM_HEIGHT = (
    0.86198853083640214
)

EXPECTED_TARGET_MAXIMUM_HEIGHT = (
    0.20000000000000001
)

EXPECTED_COMPRESSION_RATIO = (
    0.23202164860121352
)

EXPECTED_MAXIMUM_ABSOLUTE_HEIGHT_ERROR = (
    0.66198853083640219
)

EXPECTED_MEAN_ABSOLUTE_HEIGHT_ERROR = (
    0.11257507835810372
)

EXPECTED_PREVIEW_MEAN_ABSOLUTE_ERROR = (
    25.384524971859626
)

EXPECTED_PREVIEW_MAXIMUM_ABSOLUTE_ERROR = (
    124.0
)

EXPECTED_COMPRESSED_MINIMUM = 0.0

EXPECTED_COMPRESSED_MAXIMUM = (
    0.20000000000000001
)

EXPECTED_COMPRESSED_MEAN = (
    0.067366832027534421
)

EXPECTED_COMPRESSED_STD = (
    0.046287226718442605
)

EXPECTED_GRADIENT_THRESHOLD = (
    0.00099789185705623598
)

EXPECTED_MAXIMUM_GRADIENT = (
    0.0043631690139717639
)

EXPECTED_WEIGHT_MINIMUM = 0.0

EXPECTED_WEIGHT_MAXIMUM = (
    0.59999999999999998
)

EXPECTED_WEIGHT_MEAN = (
    0.020089027251809683
)

EXPECTED_WEIGHT_STD = (
    0.050951109993613054
)

QUANTILE_PROBABILITIES = (
    0.00,
    0.01,
    0.05,
    0.25,
    0.50,
    0.75,
    0.95,
    0.99,
    1.00,
)

EXPECTED_COMPRESSED_QUANTILES = (
    0.0,
    0.0,
    0.0,
    0.029271884938136906,
    0.068278001992682483,
    0.10251010615945473,
    0.14172111466904311,
    0.17637349039077807,
    0.20000000000000001,
)

EXPECTED_COMPRESSED_SHA256_QUANTIZED_12 = (
    "d5fea330fb926a675022dda402575376"
    "3d45f99488a1d6d54ebada41718801f2"
)


def _build_production_surface():
    neutral_surface = (
        AtlasNeutralParametricFaceSurfaceBuilder.build(
            row_count=GRID_SIZE,
            column_count=GRID_SIZE,
        )
    )

    depth_profile = AtlasParametricFaceDepthProfile(
        name="production-eye-brow-cheek-golden",
        brow_projection=0.026,
        eye_socket_depth=0.035,
        cheek_projection=0.028,
        nose_bridge_projection=0.0,
        nose_tip_projection=0.0,
        nose_wing_projection=0.0,
        upper_lip_projection=0.0,
        lower_lip_projection=0.0,
        philtrum_depth=0.0,
        labiomental_fold_depth=0.0,
        chin_projection=0.0,
    )

    return AtlasParametricFaceDepthDeformer.deform(
        neutral_surface,
        depth_profile=depth_profile,
    )


def _build_gradient_comparison():
    source_surface = _build_production_surface()

    projection = (
        AtlasPortraitContactPlaneProjector.project(
            source_surface,
        )
    )

    compression = (
        AtlasPortraitContactPlaneGradientLimitedCompressor
        .compress(
            projection,
            target_maximum_height=(
                TARGET_MAXIMUM_HEIGHT
            ),
        )
    )

    comparison = (
        AtlasPortraitContactPlaneCompressionEvaluator
        .evaluate(
            source_surface,
            compression=compression,
            contact_row=projection.contact_row,
            contact_column=projection.contact_column,
            light_direction=LIGHT_DIRECTION,
            ambient_strength=AMBIENT_STRENGTH,
            diffuse_strength=DIFFUSE_STRENGTH,
        )
    )

    return (
        source_surface,
        projection,
        compression,
        comparison,
    )


def _build_gamma_comparison(
    source_surface,
    projection,
):
    compression = (
        AtlasPortraitContactPlaneGlobalGammaCompressor
        .compress(
            projection,
            target_maximum_height=(
                TARGET_MAXIMUM_HEIGHT
            ),
            gamma=0.60,
        )
    )

    return (
        AtlasPortraitContactPlaneCompressionEvaluator
        .evaluate(
            source_surface,
            compression=compression,
            contact_row=projection.contact_row,
            contact_column=projection.contact_column,
            light_direction=LIGHT_DIRECTION,
            ambient_strength=AMBIENT_STRENGTH,
            diffuse_strength=DIFFUSE_STRENGTH,
        )
    )


def test_production_gradient_limited_contract():
    _, projection, compression, comparison = (
        _build_gradient_comparison()
    )

    assert comparison.shape == EXPECTED_SHAPE

    assert comparison.contact_index == (
        EXPECTED_CONTACT_INDEX
    )

    assert projection.contact_index == (
        EXPECTED_CONTACT_INDEX
    )

    assert compression[
        "type"
    ] == (
        "portrait_contact_plane_"
        "gradient_limited_compression"
    )

    assert compression[
        "compression_mode"
    ] == (
        "global_gamma_"
        "gradient_limited_linear_blend"
    )

    assert compression[
        "gamma"
    ] == pytest.approx(
        0.60,
        abs=0.0,
    )

    assert compression[
        "gradient_percentile"
    ] == pytest.approx(
        70.0,
        abs=0.0,
    )

    assert compression[
        "blend_strength"
    ] == pytest.approx(
        0.60,
        abs=0.0,
    )


def test_production_gradient_limited_height_metrics():
    _, _, _, comparison = (
        _build_gradient_comparison()
    )

    assert (
        comparison.source_maximum_height
        == pytest.approx(
            EXPECTED_SOURCE_MAXIMUM_HEIGHT,
            abs=1.0e-15,
        )
    )

    assert (
        comparison.target_maximum_height
        == pytest.approx(
            EXPECTED_TARGET_MAXIMUM_HEIGHT,
            abs=1.0e-15,
        )
    )

    assert (
        comparison.compression_ratio
        == pytest.approx(
            EXPECTED_COMPRESSION_RATIO,
            abs=1.0e-15,
        )
    )

    assert (
        comparison.maximum_absolute_height_error
        == pytest.approx(
            EXPECTED_MAXIMUM_ABSOLUTE_HEIGHT_ERROR,
            abs=1.0e-15,
        )
    )

    assert (
        comparison.mean_absolute_height_error
        == pytest.approx(
            EXPECTED_MEAN_ABSOLUTE_HEIGHT_ERROR,
            abs=1.0e-15,
        )
    )


def test_production_gradient_limited_preview_metrics():
    _, _, _, comparison = (
        _build_gradient_comparison()
    )

    assert (
        comparison.preview_mean_absolute_error
        == pytest.approx(
            EXPECTED_PREVIEW_MEAN_ABSOLUTE_ERROR,
            abs=1.0e-12,
        )
    )

    assert (
        comparison.preview_maximum_absolute_error
        == pytest.approx(
            EXPECTED_PREVIEW_MAXIMUM_ABSOLUTE_ERROR,
            abs=0.0,
        )
    )


def test_production_gradient_limited_surface_summary():
    _, _, _, comparison = (
        _build_gradient_comparison()
    )

    compressed_height = np.asarray(
        comparison.compressed_height,
        dtype=np.float64,
    )

    assert float(
        compressed_height.min()
    ) == pytest.approx(
        EXPECTED_COMPRESSED_MINIMUM,
        abs=1.0e-15,
    )

    assert float(
        compressed_height.max()
    ) == pytest.approx(
        EXPECTED_COMPRESSED_MAXIMUM,
        abs=1.0e-15,
    )

    assert float(
        compressed_height.mean()
    ) == pytest.approx(
        EXPECTED_COMPRESSED_MEAN,
        abs=1.0e-15,
    )

    assert float(
        compressed_height.std()
    ) == pytest.approx(
        EXPECTED_COMPRESSED_STD,
        abs=1.0e-15,
    )


def test_production_gradient_limited_preserves_contact_patch():
    _, projection, _, comparison = (
        _build_gradient_comparison()
    )

    compressed_height = np.asarray(
        comparison.compressed_height,
        dtype=np.float64,
    )

    maximum = float(
        compressed_height.max()
    )

    maximum_positions = tuple(
        (
            int(position[0]),
            int(position[1]),
        )
        for position in np.argwhere(
            np.isclose(
                compressed_height,
                maximum,
                rtol=0.0,
                atol=1.0e-12,
            )
        )
    )

    assert maximum_positions == (
        EXPECTED_MAXIMUM_POSITIONS
    )

    assert projection.contact_index in (
        maximum_positions
    )

    assert comparison.contact_point_preserved
    assert comparison.source_surface_safe
    assert comparison.compressed_surface_safe


def test_production_gradient_weight_matches_metrics():
    _, _, compression, _ = (
        _build_gradient_comparison()
    )

    gradient_weight = np.asarray(
        compression["gradient_weight"],
        dtype=np.float64,
    )

    assert float(
        compression["gradient_threshold"]
    ) == pytest.approx(
        EXPECTED_GRADIENT_THRESHOLD,
        abs=1.0e-15,
    )

    assert float(
        compression["maximum_gradient"]
    ) == pytest.approx(
        EXPECTED_MAXIMUM_GRADIENT,
        abs=1.0e-15,
    )

    assert float(
        gradient_weight.min()
    ) == pytest.approx(
        EXPECTED_WEIGHT_MINIMUM,
        abs=1.0e-15,
    )

    assert float(
        gradient_weight.max()
    ) == pytest.approx(
        EXPECTED_WEIGHT_MAXIMUM,
        abs=1.0e-15,
    )

    assert float(
        gradient_weight.mean()
    ) == pytest.approx(
        EXPECTED_WEIGHT_MEAN,
        abs=1.0e-15,
    )

    assert float(
        gradient_weight.std()
    ) == pytest.approx(
        EXPECTED_WEIGHT_STD,
        abs=1.0e-15,
    )


def test_production_gradient_limited_quantiles():
    _, _, _, comparison = (
        _build_gradient_comparison()
    )

    compressed_height = np.asarray(
        comparison.compressed_height,
        dtype=np.float64,
    )

    quantiles = np.quantile(
        compressed_height,
        np.asarray(
            QUANTILE_PROBABILITIES,
            dtype=np.float64,
        ),
    )

    assert quantiles == pytest.approx(
        EXPECTED_COMPRESSED_QUANTILES,
        abs=1.0e-15,
    )


def test_production_gradient_limited_checksum():
    _, _, _, comparison = (
        _build_gradient_comparison()
    )

    compressed_height = np.asarray(
        comparison.compressed_height,
        dtype=np.float64,
    )

    quantized = np.round(
        compressed_height,
        decimals=12,
    ).astype(
        "<f8",
        copy=False,
    )

    checksum = hashlib.sha256(
        quantized.tobytes(
            order="C",
        )
    ).hexdigest()

    assert checksum == (
        EXPECTED_COMPRESSED_SHA256_QUANTIZED_12
    )


def test_gradient_limited_improves_global_gamma_mean_error():
    (
        source_surface,
        projection,
        _,
        gradient_comparison,
    ) = _build_gradient_comparison()

    gamma_comparison = _build_gamma_comparison(
        source_surface,
        projection,
    )

    assert (
        gradient_comparison
        .preview_mean_absolute_error
        <
        gamma_comparison
        .preview_mean_absolute_error
    )

    assert (
        gradient_comparison
        .preview_maximum_absolute_error
        <=
        gamma_comparison
        .preview_maximum_absolute_error
    )
