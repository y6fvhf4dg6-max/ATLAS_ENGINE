import numpy as np
import pytest

from CORE.atlas_parametric_face_shaded_preview_result import (
    AtlasParametricFaceShadedPreviewResult,
)


def _result(
    *,
    shading=None,
    preview=None,
    light_direction=(0.4, -0.5, 0.7681145747868608),
    ambient_strength=0.25,
    diffuse_strength=0.75,
):
    if shading is None:
        shading = np.array(
            [
                [0.0, 0.25, 0.50],
                [0.50, 0.75, 1.0],
            ],
            dtype=np.float64,
        )

    if preview is None:
        preview = np.array(
            [
                [0, 64, 128],
                [128, 191, 255],
            ],
            dtype=np.uint8,
        )

    return AtlasParametricFaceShadedPreviewResult(
        shading=shading,
        preview=preview,
        light_direction=light_direction,
        ambient_strength=ambient_strength,
        diffuse_strength=diffuse_strength,
    )


def test_result_normalizes_coordinate_arrays():
    result = AtlasParametricFaceShadedPreviewResult(
        shading=[
            [0.0, 0.5],
            [0.75, 1.0],
        ],
        preview=[
            [0, 128],
            [191, 255],
        ],
        light_direction=(0.0, 0.0, 1.0),
        ambient_strength=0.20,
        diffuse_strength=0.80,
    )

    assert result.shading.dtype == np.float64
    assert result.preview.dtype == np.uint8


def test_result_copies_source_arrays():
    shading = np.array(
        [
            [0.0, 0.5],
            [0.75, 1.0],
        ],
        dtype=np.float64,
    )
    preview = np.array(
        [
            [0, 128],
            [191, 255],
        ],
        dtype=np.uint8,
    )

    result = _result(
        shading=shading,
        preview=preview,
    )

    shading[0, 0] = 1.0
    preview[0, 0] = 255

    assert result.shading[0, 0] == pytest.approx(
        0.0,
    )
    assert result.preview[0, 0] == 0


def test_result_arrays_are_read_only():
    result = _result()

    assert not result.shading.flags.writeable
    assert not result.preview.flags.writeable

    with pytest.raises(
        ValueError,
    ):
        result.shading[0, 0] = 1.0

    with pytest.raises(
        ValueError,
    ):
        result.preview[0, 0] = 255


def test_result_reports_shape_and_dimensions():
    result = _result()

    assert result.shape == (
        2,
        3,
    )
    assert result.row_count == 2
    assert result.column_count == 3


def test_result_reports_intensity_range():
    result = _result()

    assert result.minimum_intensity == pytest.approx(
        0.0,
    )
    assert result.maximum_intensity == pytest.approx(
        1.0,
    )


def test_result_preserves_render_metadata():
    result = _result(
        light_direction=(0.0, -0.6, 0.8),
        ambient_strength=0.30,
        diffuse_strength=0.70,
    )

    assert result.light_direction == pytest.approx(
        (
            0.0,
            -0.6,
            0.8,
        )
    )
    assert result.ambient_strength == pytest.approx(
        0.30,
    )
    assert result.diffuse_strength == pytest.approx(
        0.70,
    )


def test_result_rejects_non_two_dimensional_shading():
    with pytest.raises(
        ValueError,
        match="shading must be two-dimensional",
    ):
        _result(
            shading=np.zeros(
                (
                    2,
                    2,
                    2,
                ),
                dtype=np.float64,
            ),
        )


def test_result_rejects_non_two_dimensional_preview():
    with pytest.raises(
        ValueError,
        match="preview must be two-dimensional",
    ):
        _result(
            preview=np.zeros(
                (
                    2,
                    2,
                    2,
                ),
                dtype=np.uint8,
            ),
        )


def test_result_rejects_mismatched_shapes():
    with pytest.raises(
        ValueError,
        match="identical shapes",
    ):
        _result(
            preview=np.zeros(
                (
                    3,
                    2,
                ),
                dtype=np.uint8,
            ),
        )


def test_result_rejects_too_small_arrays():
    with pytest.raises(
        ValueError,
        match="at least two rows and two columns",
    ):
        _result(
            shading=np.zeros(
                (
                    1,
                    3,
                ),
                dtype=np.float64,
            ),
            preview=np.zeros(
                (
                    1,
                    3,
                ),
                dtype=np.uint8,
            ),
        )


def test_result_rejects_non_finite_shading():
    shading = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.float64,
    )
    shading[0, 0] = np.nan

    with pytest.raises(
        ValueError,
        match="non-finite",
    ):
        _result(
            shading=shading,
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        -0.01,
        1.01,
    ],
)
def test_result_rejects_shading_outside_normalized_range(
    invalid_value,
):
    shading = np.zeros(
        (
            2,
            3,
        ),
        dtype=np.float64,
    )
    shading[0, 0] = invalid_value

    with pytest.raises(
        ValueError,
        match="0.0..1.0",
    ):
        _result(
            shading=shading,
        )


def test_result_rejects_preview_outside_uint8_range():
    with pytest.raises(
        ValueError,
        match="0..255",
    ):
        _result(
            preview=[
                [0, 128, 256],
                [0, 128, 255],
            ],
        )


def test_result_rejects_non_integral_preview_values():
    with pytest.raises(
        ValueError,
        match="integer values",
    ):
        _result(
            preview=[
                [0, 64.5, 128],
                [128, 191, 255],
            ],
        )


def test_result_rejects_invalid_light_direction_length():
    with pytest.raises(
        ValueError,
        match="three components",
    ):
        _result(
            light_direction=(
                0.0,
                1.0,
            ),
        )


def test_result_rejects_non_finite_light_direction():
    with pytest.raises(
        ValueError,
        match="light_direction must be finite",
    ):
        _result(
            light_direction=(
                0.0,
                np.nan,
                1.0,
            ),
        )


def test_result_rejects_non_unit_light_direction():
    with pytest.raises(
        ValueError,
        match="normalized",
    ):
        _result(
            light_direction=(
                0.0,
                0.0,
                2.0,
            ),
        )


@pytest.mark.parametrize(
    "field_name, value",
    [
        (
            "ambient_strength",
            -0.01,
        ),
        (
            "ambient_strength",
            1.01,
        ),
        (
            "diffuse_strength",
            -0.01,
        ),
        (
            "diffuse_strength",
            1.01,
        ),
    ],
)
def test_result_rejects_strength_outside_normalized_range(
    field_name,
    value,
):
    arguments = {
        "ambient_strength": 0.25,
        "diffuse_strength": 0.75,
    }
    arguments[field_name] = value

    with pytest.raises(
        ValueError,
        match=field_name,
    ):
        _result(
            **arguments,
        )
