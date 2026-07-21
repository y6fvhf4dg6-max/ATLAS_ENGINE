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
from CORE.atlas_portrait_contact_plane_linear_compressor import (
    AtlasPortraitContactPlaneLinearCompressor,
)
from CORE.atlas_portrait_contact_plane_projector import (
    AtlasPortraitContactPlaneProjector,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    AMBIENT_STRENGTH,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    DIFFUSE_STRENGTH,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    GRID_SIZE,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
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
    0.13798097791024144
)

EXPECTED_PREVIEW_MEAN_ABSOLUTE_ERROR = (
    27.624865517005492
)
EXPECTED_PREVIEW_MAXIMUM_ABSOLUTE_ERROR = (
    109.0
)

EXPECTED_COMPRESSED_MINIMUM = 0.0
EXPECTED_COMPRESSED_MAXIMUM = (
    0.20000000000000001
)
EXPECTED_COMPRESSED_MEAN = (
    0.041686818270372968
)
EXPECTED_COMPRESSED_STD = (
    0.038534847582804961
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
    0.008614849041683224,
    0.03335659325907118,
    0.06565348866007968,
    0.11417562038203978,
    0.164397008767594,
    0.2,
)

EXPECTED_COMPRESSED_SHA256_QUANTIZED_12 = (
    "7e9a9f5b7a5156b11d99ca95b7539efa"
    "3c333c372c0c48609471078af991d826"
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


def _build_comparison():
    source_surface = _build_production_surface()

    projection = (
        AtlasPortraitContactPlaneProjector.project(
            source_surface,
        )
    )

    compression = (
        AtlasPortraitContactPlaneLinearCompressor.compress(
            projection,
            target_maximum_height=(
                TARGET_MAXIMUM_HEIGHT
            ),
        )
    )

    comparison = (
        AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
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
        projection,
        compression,
        comparison,
    )


def test_production_compression_preserves_contract():
    projection, compression, comparison = (
        _build_comparison()
    )

    assert comparison.shape == EXPECTED_SHAPE
    assert comparison.contact_index == (
        EXPECTED_CONTACT_INDEX
    )

    assert compression[
        "compression_mode"
    ] == "linear_target_maximum_height"

    assert comparison.metadata[
        "evaluation_mode"
    ] == "surface_preview_and_validity"

    assert (
        projection.contact_row,
        projection.contact_column,
    ) == EXPECTED_CONTACT_INDEX


def test_production_compression_matches_height_metrics():
    _, _, comparison = _build_comparison()

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

    assert comparison.compression_ratio == pytest.approx(
        EXPECTED_COMPRESSION_RATIO,
        abs=1.0e-15,
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


def test_production_compression_matches_preview_metrics():
    _, _, comparison = _build_comparison()

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


def test_production_compressed_height_matches_summary():
    _, _, comparison = _build_comparison()

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

    quantiles = np.quantile(
        compressed_height,
        QUANTILE_PROBABILITIES,
    )

    assert quantiles == pytest.approx(
        EXPECTED_COMPRESSED_QUANTILES,
        abs=1.0e-15,
    )


def test_production_compressed_height_matches_checksum():
    _, _, comparison = _build_comparison()

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

    assert (
        checksum
        == EXPECTED_COMPRESSED_SHA256_QUANTIZED_12
    )


def test_production_compression_remains_safe():
    _, _, comparison = _build_comparison()

    assert comparison.contact_point_preserved
    assert comparison.source_surface_safe
    assert comparison.compressed_surface_safe


def test_production_compression_is_deterministic():
    first = _build_comparison()[2]
    second = _build_comparison()[2]

    assert first.compressed_height == pytest.approx(
        second.compressed_height,
        abs=0.0,
    )

    assert (
        first.preview_mean_absolute_error
        == pytest.approx(
            second.preview_mean_absolute_error,
            abs=0.0,
        )
    )

    assert (
        first.preview_maximum_absolute_error
        == pytest.approx(
            second.preview_maximum_absolute_error,
            abs=0.0,
        )
    )
