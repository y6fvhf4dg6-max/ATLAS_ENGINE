import numpy as np
import pytest

from CORE.atlas_parametric_face_shaded_preview_renderer import (
    AtlasParametricFaceShadedPreviewRenderer,
)
from CORE.atlas_parametric_face_surface import (
    AtlasParametricFaceSurface,
)
from CORE.atlas_parametric_face_surface_validity_analyzer import (
    AtlasParametricFaceSurfaceValidityAnalyzer,
)
from CORE.atlas_portrait_contact_plane_compression_comparison_result import (
    AtlasPortraitContactPlaneCompressionComparisonResult,
)
from CORE.atlas_portrait_contact_plane_compression_evaluator import (
    AtlasPortraitContactPlaneCompressionEvaluator,
)


def _source_surface() -> AtlasParametricFaceSurface:
    x_axis = np.linspace(
        -1.0,
        1.0,
        5,
        dtype=np.float64,
    )
    y_axis = np.linspace(
        -1.0,
        1.0,
        5,
        dtype=np.float64,
    )

    x_coordinates, y_coordinates = np.meshgrid(
        x_axis,
        y_axis,
    )

    z_coordinates = np.array(
        [
            [0.00, 0.08, 0.12, 0.08, 0.00],
            [0.04, 0.18, 0.32, 0.18, 0.04],
            [0.08, 0.30, 0.80, 0.30, 0.08],
            [0.04, 0.18, 0.32, 0.18, 0.04],
            [0.00, 0.08, 0.12, 0.08, 0.00],
        ],
        dtype=np.float64,
    )

    return AtlasParametricFaceSurface(
        x_coordinates=x_coordinates,
        y_coordinates=y_coordinates,
        z_coordinates=z_coordinates,
    )


def _compression() -> dict[str, object]:
    source = _source_surface()

    return {
        "type": (
            "portrait_contact_plane_linear_compression"
        ),
        "compression_mode": (
            "linear_target_maximum_height"
        ),
        "source_shape": source.shape,
        "source_maximum_height": 0.8,
        "target_maximum_height": 0.2,
        "linear_scale": 0.25,
        "compressed_height": (
            source.z_coordinates * 0.25
        ),
    }


def _evaluate():
    return AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
        _source_surface(),
        compression=_compression(),
        contact_row=2,
        contact_column=2,
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.25,
        diffuse_strength=0.75,
    )


def test_evaluator_returns_comparison_result():
    result = _evaluate()

    assert isinstance(
        result,
        AtlasPortraitContactPlaneCompressionComparisonResult,
    )


def test_evaluator_preserves_source_and_compressed_heights():
    source = _source_surface()
    compression = _compression()

    result = AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
        source,
        compression=compression,
        contact_row=2,
        contact_column=2,
    )

    assert result.source_height == pytest.approx(
        source.z_coordinates,
    )
    assert result.compressed_height == pytest.approx(
        compression["compressed_height"],
    )


def test_evaluator_reports_compression_metrics():
    result = _evaluate()

    assert result.source_maximum_height == pytest.approx(
        0.8,
    )
    assert result.target_maximum_height == pytest.approx(
        0.2,
    )
    assert result.compression_ratio == pytest.approx(
        0.25,
    )


def test_evaluator_calculates_height_error_metrics():
    result = _evaluate()

    expected_absolute_error = np.abs(
        result.compressed_height
        - result.source_height
    )

    assert (
        result.maximum_absolute_height_error
        == pytest.approx(
            float(
                expected_absolute_error.max(),
            )
        )
    )
    assert (
        result.mean_absolute_height_error
        == pytest.approx(
            float(
                expected_absolute_error.mean(),
            )
        )
    )


def test_evaluator_calculates_preview_error_metrics():
    source = _source_surface()
    compression = _compression()

    compressed_surface = AtlasParametricFaceSurface(
        x_coordinates=source.x_coordinates,
        y_coordinates=source.y_coordinates,
        z_coordinates=compression[
            "compressed_height"
        ],
    )

    source_preview = (
        AtlasParametricFaceShadedPreviewRenderer.render(
            source,
            light_direction=(
                0.0,
                0.0,
                1.0,
            ),
            ambient_strength=0.25,
            diffuse_strength=0.75,
        )
    )
    compressed_preview = (
        AtlasParametricFaceShadedPreviewRenderer.render(
            compressed_surface,
            light_direction=(
                0.0,
                0.0,
                1.0,
            ),
            ambient_strength=0.25,
            diffuse_strength=0.75,
        )
    )

    preview_error = np.abs(
        source_preview.preview.astype(
            np.float64,
        )
        - compressed_preview.preview.astype(
            np.float64,
        )
    )

    result = AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
        source,
        compression=compression,
        contact_row=2,
        contact_column=2,
        light_direction=(
            0.0,
            0.0,
            1.0,
        ),
        ambient_strength=0.25,
        diffuse_strength=0.75,
    )

    assert (
        result.preview_mean_absolute_error
        == pytest.approx(
            float(
                preview_error.mean(),
            )
        )
    )
    assert (
        result.preview_maximum_absolute_error
        == pytest.approx(
            float(
                preview_error.max(),
            )
        )
    )


def test_evaluator_reports_surface_safety():
    source = _source_surface()
    compression = _compression()

    compressed_surface = AtlasParametricFaceSurface(
        x_coordinates=source.x_coordinates,
        y_coordinates=source.y_coordinates,
        z_coordinates=compression[
            "compressed_height"
        ],
    )

    expected_source = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            source,
        )
    )
    expected_compressed = (
        AtlasParametricFaceSurfaceValidityAnalyzer.analyze(
            compressed_surface,
        )
    )

    result = AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
        source,
        compression=compression,
        contact_row=2,
        contact_column=2,
    )

    assert (
        result.source_surface_safe
        is expected_source.is_safe
    )
    assert (
        result.compressed_surface_safe
        is expected_compressed.is_safe
    )


def test_evaluator_reports_preserved_contact_point():
    result = _evaluate()

    assert result.contact_index == (
        2,
        2,
    )
    assert result.contact_point_preserved


def test_evaluator_records_metadata():
    result = _evaluate()

    assert result.metadata[
        "compression_mode"
    ] == "linear_target_maximum_height"
    assert result.metadata[
        "evaluation_mode"
    ] == "surface_preview_and_validity"


def test_evaluator_does_not_modify_inputs():
    source = _source_surface()
    compression = _compression()

    original_z = source.z_coordinates.copy()
    original_compressed = compression[
        "compressed_height"
    ].copy()

    AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
        source,
        compression=compression,
        contact_row=2,
        contact_column=2,
    )

    assert source.z_coordinates == pytest.approx(
        original_z,
    )
    assert compression[
        "compressed_height"
    ] == pytest.approx(
        original_compressed,
    )


def test_evaluator_is_deterministic():
    first = _evaluate()
    second = _evaluate()

    assert first.source_height == pytest.approx(
        second.source_height,
    )
    assert first.compressed_height == pytest.approx(
        second.compressed_height,
    )
    assert (
        first.maximum_absolute_height_error
        == pytest.approx(
            second.maximum_absolute_height_error,
        )
    )
    assert (
        first.preview_mean_absolute_error
        == pytest.approx(
            second.preview_mean_absolute_error,
        )
    )


def test_evaluator_rejects_wrong_surface_type():
    with pytest.raises(
        TypeError,
        match="source_surface",
    ):
        AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
            object(),
            compression=_compression(),
            contact_row=2,
            contact_column=2,
        )


def test_evaluator_rejects_wrong_compression_type():
    with pytest.raises(
        TypeError,
        match="compression",
    ):
        AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
            _source_surface(),
            compression=object(),
            contact_row=2,
            contact_column=2,
        )


def test_evaluator_rejects_compressed_shape_mismatch():
    compression = _compression()
    compression["compressed_height"] = np.zeros(
        (
            4,
            4,
        ),
        dtype=np.float64,
    )

    with pytest.raises(
        ValueError,
        match="shape",
    ):
        AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
            _source_surface(),
            compression=compression,
            contact_row=2,
            contact_column=2,
        )


def test_evaluator_rejects_missing_compression_field():
    compression = _compression()
    del compression["compressed_height"]

    with pytest.raises(
        ValueError,
        match="compressed_height",
    ):
        AtlasPortraitContactPlaneCompressionEvaluator.evaluate(
            _source_surface(),
            compression=compression,
            contact_row=2,
            contact_column=2,
        )
