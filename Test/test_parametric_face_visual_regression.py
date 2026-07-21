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
from CORE.atlas_parametric_face_shaded_preview_renderer import (
    AtlasParametricFaceShadedPreviewRenderer,
)
from CORE.atlas_parametric_face_surface_validity_analyzer import (
    AtlasParametricFaceSurfaceValidityAnalyzer,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    AMBIENT_STRENGTH,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    DIFFUSE_STRENGTH,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_MINIMUM_NORMAL_Z,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_MINIMUM_SIGNED_CELL_AREA,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_PREVIEW_MAX,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_PREVIEW_MEAN,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_PREVIEW_MIN,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_PREVIEW_SHA256,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_PREVIEW_SHAPE,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_MAX,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_MEAN,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_MIN,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_QUANTILES,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_SHA256_QUANTIZED_12,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_SHAPE,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    EXPECTED_Z_STD,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    GRID_SIZE,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    LIGHT_DIRECTION,
)
from Test.fixtures.portrait.parametric_face_visual_regression_fixture import (
    QUANTILE_PROBABILITIES,
)


def _sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value,
    ).hexdigest()


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


def test_production_face_z_surface_matches_golden_summary():
    surface = _build_production_surface()

    z_coordinates = np.asarray(
        surface.z_coordinates,
        dtype=np.float64,
    )

    assert z_coordinates.shape == EXPECTED_Z_SHAPE

    assert np.min(
        z_coordinates,
    ) == pytest.approx(
        EXPECTED_Z_MIN,
        abs=1.0e-15,
    )

    assert np.max(
        z_coordinates,
    ) == pytest.approx(
        EXPECTED_Z_MAX,
        abs=1.0e-15,
    )

    assert np.mean(
        z_coordinates,
    ) == pytest.approx(
        EXPECTED_Z_MEAN,
        abs=1.0e-15,
    )

    assert np.std(
        z_coordinates,
    ) == pytest.approx(
        EXPECTED_Z_STD,
        abs=1.0e-15,
    )

    quantiles = np.quantile(
        z_coordinates,
        QUANTILE_PROBABILITIES,
    )

    assert quantiles == pytest.approx(
        EXPECTED_Z_QUANTILES,
        abs=1.0e-15,
    )


def test_production_face_z_surface_matches_golden_checksum():
    surface = _build_production_surface()

    z_coordinates = np.asarray(
        surface.z_coordinates,
        dtype=np.float64,
    )

    quantized_z = np.round(
        z_coordinates,
        decimals=12,
    ).astype(
        "<f8",
        copy=False,
    )

    checksum = _sha256_bytes(
        quantized_z.tobytes(
            order="C",
        )
    )

    assert checksum == EXPECTED_Z_SHA256_QUANTIZED_12


def test_production_face_shaded_preview_matches_golden_summary():
    surface = _build_production_surface()

    rendered = (
        AtlasParametricFaceShadedPreviewRenderer.render(
            surface,
            light_direction=LIGHT_DIRECTION,
            ambient_strength=AMBIENT_STRENGTH,
            diffuse_strength=DIFFUSE_STRENGTH,
        )
    )

    preview = np.ascontiguousarray(
        rendered.preview,
        dtype=np.uint8,
    )

    assert preview.shape == EXPECTED_PREVIEW_SHAPE
    assert int(np.min(preview)) == EXPECTED_PREVIEW_MIN
    assert int(np.max(preview)) == EXPECTED_PREVIEW_MAX

    assert np.mean(
        preview,
    ) == pytest.approx(
        EXPECTED_PREVIEW_MEAN,
        abs=1.0e-12,
    )


def test_production_face_shaded_preview_matches_golden_checksum():
    surface = _build_production_surface()

    rendered = (
        AtlasParametricFaceShadedPreviewRenderer.render(
            surface,
            light_direction=LIGHT_DIRECTION,
            ambient_strength=AMBIENT_STRENGTH,
            diffuse_strength=DIFFUSE_STRENGTH,
        )
    )

    preview = np.ascontiguousarray(
        rendered.preview,
        dtype=np.uint8,
    )

    checksum = _sha256_bytes(
        preview.tobytes(
            order="C",
        )
    )

    assert checksum == EXPECTED_PREVIEW_SHA256


def test_production_face_surface_remains_geometrically_safe():
    surface = _build_production_surface()

    validity = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            surface,
        )
    )

    assert validity.is_safe
    assert validity.folded_cell_count == 0
    assert validity.inverted_normal_count == 0

    assert validity.minimum_signed_cell_area == pytest.approx(
        EXPECTED_MINIMUM_SIGNED_CELL_AREA,
        abs=1.0e-18,
    )

    assert validity.minimum_normal_z == pytest.approx(
        EXPECTED_MINIMUM_NORMAL_Z,
        abs=1.0e-15,
    )
